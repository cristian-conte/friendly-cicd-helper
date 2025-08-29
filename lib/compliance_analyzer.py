import logging
import json
import os
import tempfile
import subprocess
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict

from lib.utils import extract_files_from_diff

logger = logging.getLogger(__name__)


class ComplianceIssueType(Enum):
    IAC_BEST_PRACTICES = "iac_best_practices"
    LICENSE_VIOLATION = "license_violation"
    DOCS_STANDARD_DEVIATION = "docs_standard_deviation"


class Severity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class ComplianceFinding:
    """Represents a single compliance finding."""
    issue_type: ComplianceIssueType
    severity: Severity
    confidence: float
    title: str
    description: str
    file_path: str
    line_number: int
    code_snippet: str
    recommendation: str
    cwe_id: str = ""


class ComplianceAnalyzer:
    """Analyzes code for compliance using industry-standard tools (Checkov)."""

    def analyze_diff(self, diff_content: str) -> List[ComplianceFinding]:
        """Analyze a Git diff for compliance issues via Checkov."""
        logger.info("Starting compliance analysis with Checkov...")
        findings: List[ComplianceFinding] = []

        temp_files = extract_files_from_diff(diff_content)
        if not temp_files:
            logger.info("No files to analyze in diff")
            return findings

        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                # Recreate file structure for Checkov
                for orig_path, tmp_path in temp_files.items():
                    target_path = os.path.join(temp_dir, orig_path)
                    os.makedirs(os.path.dirname(target_path), exist_ok=True)
                    with open(tmp_path, 'r', encoding='utf-8', errors='ignore') as src, \
                         open(target_path, 'w', encoding='utf-8') as dst:
                        dst.write(src.read())

                # Run checkov using Python module to avoid PATH issues
                cmd = [
                    os.environ.get('PYTHON_EXECUTABLE') or os.sys.executable,
                    '-m', 'checkov',
                    '-d', temp_dir,
                    '-o', 'json'
                ]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

                if result.returncode not in (0, 1):  # 0 no findings, 1 findings
                    logger.warning(f"Checkov exited with code {result.returncode}: {result.stderr[:200]}")

                if result.stdout:
                    try:
                        data = json.loads(result.stdout)
                        findings.extend(self._parse_checkov_results(data, temp_dir))
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse Checkov JSON output: {e}")
        except subprocess.TimeoutExpired:
            logger.error("Checkov analysis timed out")
        except Exception as e:
            logger.error(f"Error running Checkov: {e}")

        logger.info(f"Compliance analysis completed. Found {len(findings)} findings.")
        return findings

    def _parse_checkov_results(self, data: Dict, temp_root: str) -> List[ComplianceFinding]:
        results = []
        res = data.get('results') or {}
        failed = res.get('failed_checks') or []

        for item in failed:
            file_path = item.get('file_path') or item.get('repo_file_path') or ''
            # Normalize to original relative path
            rel_path = os.path.relpath(file_path, temp_root) if file_path.startswith(temp_root) else file_path.lstrip('./')

            sev = self._map_checkov_severity(item.get('severity'))
            line_range = item.get('file_line_range') or []
            line_no = line_range[0] if isinstance(line_range, list) and line_range else 0

            title = f"Checkov {item.get('check_id', '')}: {item.get('check_name', 'Policy violation')}"
            desc = f"Resource {item.get('resource', '')} violated policy {item.get('check_id', '')}."
            guideline = item.get('guideline') or item.get('url')
            recommendation = f"Review and remediate per guideline: {guideline}" if guideline else "Review and remediate per Checkov policy guidance."

            results.append(ComplianceFinding(
                issue_type=ComplianceIssueType.IAC_BEST_PRACTICES,
                severity=sev,
                confidence=0.9,
                title=title,
                description=desc,
                file_path=rel_path,
                line_number=line_no,
                code_snippet="",
                recommendation=recommendation,
            ))

        return results

    def _map_checkov_severity(self, severity: str) -> Severity:
        mapping = {
            'critical': Severity.CRITICAL,
            'high': Severity.HIGH,
            'medium': Severity.MEDIUM,
            'low': Severity.LOW,
            'info': Severity.INFO,
            'undefined': Severity.MEDIUM,
            None: Severity.MEDIUM
        }
        return mapping.get(str(severity).lower(), Severity.MEDIUM)

    def generate_report(self, findings: List[ComplianceFinding]) -> Dict:
        """Generate a structured compliance findings report."""
        summary: Dict[str, int] = {
            "total_findings": len(findings),
            "severities": {sev.value: 0 for sev in Severity},
            "issue_types": {t.value: 0 for t in ComplianceIssueType}
        }
        for f in findings:
            summary["severities"][f.severity.value] += 1
            summary["issue_types"][f.issue_type.value] += 1

        report = {
            "summary": summary,
            "findings": [
                {
                    "issue_type": f.issue_type.value,
                    "severity": f.severity.value,
                    "confidence": f.confidence,
                    "title": f.title,
                    "description": f.description,
                    "file_path": f.file_path,
                    "line_number": f.line_number,
                    "code_snippet": f.code_snippet,
                    "recommendation": f.recommendation,
                    "cwe_id": f.cwe_id,
                }
                for f in findings
            ],
            "recommendations": list(set(f.recommendation for f in findings if f.recommendation))
        }
        return report
