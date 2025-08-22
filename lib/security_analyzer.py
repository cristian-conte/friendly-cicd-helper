"""Security analysis module for friendly-cicd-helper using industry-standard tools."""
import json
import logging
import os
import sys
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class Severity(Enum):
    """Security vulnerability severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class VulnerabilityType(Enum):
    """Types of security vulnerabilities."""
    SQL_INJECTION = "sql_injection"
    XSS = "cross_site_scripting"
    SECRET_EXPOSURE = "secret_exposure"
    HARDCODED_CREDENTIALS = "hardcoded_credentials"
    INSECURE_RANDOM = "insecure_random"
    PATH_TRAVERSAL = "path_traversal"
    COMMAND_INJECTION = "command_injection"
    DESERIALIZATION = "unsafe_deserialization"
    WEAK_CRYPTO = "weak_cryptography"
    UNVALIDATED_REDIRECT = "unvalidated_redirect"
    DEPENDENCY_VULNERABILITY = "dependency_vulnerability"


@dataclass
class SecurityFinding:
    """Represents a security vulnerability finding."""
    vulnerability_type: VulnerabilityType
    severity: Severity
    confidence: float  # 0.0 to 1.0
    title: str
    description: str
    file_path: str
    line_number: int
    code_snippet: str
    recommendation: str
    cwe_id: Optional[str] = None


class SecurityAnalyzer:
    """Security analyzer using industry-standard tools (bandit, safety, semgrep)."""
    
    def __init__(self):
        """Initialize the security analyzer."""
        self.logger = logging.getLogger(__name__)
        
    def analyze_diff(self, diff_content: str) -> List[SecurityFinding]:
        """
        Analyze a git diff for security vulnerabilities using industry-standard tools.
        
        Args:
            diff_content: Git diff content
            
        Returns:
            List of SecurityFinding objects
        """
        findings = []
        
        try:
            # Extract file content from diff for analysis
            temp_files = self._extract_files_from_diff(diff_content)
            
            if not temp_files:
                self.logger.info("No files to analyze in diff")
                return findings
            
            # Run bandit for Python security issues
            self.logger.info("Running bandit security scan...")
            findings.extend(self._run_bandit(temp_files))
            
            # Run safety for dependency vulnerabilities (only if requirements files are present)
            if any(f.endswith(('requirements.txt', 'requirements.in', 'pyproject.toml', 'Pipfile')) for f in temp_files.keys()):
                self.logger.info("Running safety dependency scan...")
                findings.extend(self._run_safety())
            
            # Run semgrep for comprehensive security analysis
            self.logger.info("Running semgrep security scan...")
            findings.extend(self._run_semgrep(temp_files))
            
            # Clean up temporary files
            self._cleanup_temp_files(temp_files)
            
        except Exception as e:
            self.logger.error(f"Error during security analysis: {e}")
            
        return findings
    
    def _extract_files_from_diff(self, diff_content: str) -> Dict[str, str]:
        """Extract file content from git diff for analysis."""
        import tempfile
        import os
        
        temp_files = {}
        current_file = None
        current_content = []
        in_file_content = False
        
        for line in diff_content.split('\n'):
            if line.startswith('diff --git'):
                # Save previous file if exists
                if current_file and current_content:
                    temp_files[current_file] = self._save_temp_file(current_file, '\n'.join(current_content))
                    current_content = []
                
                # Extract file path
                parts = line.split(' ')
                if len(parts) >= 4:
                    current_file = parts[3][2:]  # Remove 'b/' prefix
                in_file_content = False
                    
            elif line.startswith('+++'):
                continue
            elif line.startswith('---'):
                continue
            elif line.startswith('new file mode') or line.startswith('index '):
                continue
            elif line.startswith('@@'):
                in_file_content = True
                continue
            elif in_file_content:
                if line.startswith('+') and not line.startswith('+++'):
                    # Add new line content (remove + prefix)
                    current_content.append(line[1:])
                elif line.startswith(' '):
                    # Add context lines (remove space prefix)
                    current_content.append(line[1:])
                elif not line.startswith('-'):
                    # Add other lines as-is (but skip deletion lines)
                    current_content.append(line)
        
        # Save last file
        if current_file and current_content:
            temp_files[current_file] = self._save_temp_file(current_file, '\n'.join(current_content))
            
        return temp_files
    
    def _save_temp_file(self, file_path: str, content: str) -> str:
        """Save content to a temporary file maintaining the original file extension."""
        import tempfile
        import os
        
        # Get file extension
        _, ext = os.path.splitext(file_path)
        
        # Create temporary file with same extension
        with tempfile.NamedTemporaryFile(mode='w', suffix=ext, delete=False) as f:
            f.write(content)
            return f.name
    
    def _run_bandit(self, temp_files: Dict[str, str]) -> List[SecurityFinding]:
        """Run bandit security analysis on Python files."""
        import subprocess
        import json
        import os
        
        findings = []
        python_files = [temp_path for orig_path, temp_path in temp_files.items() 
                       if orig_path.endswith('.py')]
        
        if not python_files:
            self.logger.info("No Python files found for bandit analysis")
            return findings
            
        try:
            # Use the current Python executable
            python_path = sys.executable
            
            # Run bandit with JSON output
            cmd = [python_path, '-m', 'bandit', '-f', 'json', '--quiet'] + python_files
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.stdout:
                try:
                    bandit_data = json.loads(result.stdout)
                    
                    for issue in bandit_data.get('results', []):
                        finding = SecurityFinding(
                            vulnerability_type=self._map_bandit_test_to_type(issue.get('test_id', '')),
                            severity=self._map_bandit_severity(issue.get('issue_severity', 'LOW')),
                            confidence=self._map_bandit_confidence(issue.get('issue_confidence', 'LOW')),
                            title=f"Bandit {issue.get('test_id', '')}: {issue.get('test_name', '')}",
                            description=issue.get('issue_text', ''),
                            line_number=issue.get('line_number', 0),
                            file_path=self._get_original_path(issue.get('filename', ''), temp_files),
                            code_snippet=issue.get('code', ''),
                            recommendation=f"Review the code for potential {self._map_bandit_test_to_type(issue.get('test_id', '')).value.replace('_', ' ')} and apply secure coding practices. Consult Bandit documentation for test ID {issue.get('test_id', '')} for specific mitigation steps.",
                            cwe_id=str(issue.get('issue_cwe', {}).get('id', '')) if issue.get('issue_cwe') else None
                        )
                        findings.append(finding)
                except json.JSONDecodeError as e:
                    self.logger.error(f"Failed to parse bandit JSON output: {e}")
                    
        except subprocess.TimeoutExpired:
            self.logger.error("Bandit analysis timed out")
        except Exception as e:
            self.logger.error(f"Error running bandit: {e}")
            
        return findings
    
    def _run_safety(self) -> List[SecurityFinding]:
        """Run safety check for dependency vulnerabilities."""
        import subprocess
        import json
        import os
        
        findings = []
        
        try:
            # Use the current Python executable
            python_path = sys.executable
            
            # Run safety check with JSON output
            cmd = [python_path, '-m', 'safety', 'check', '--json']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.stdout:
                try:
                    safety_data = json.loads(result.stdout)
                    
                    for vuln in safety_data:
                        finding = SecurityFinding(
                            vulnerability_type=VulnerabilityType.DEPENDENCY_VULNERABILITY,
                            severity=self._map_safety_severity(vuln.get('vulnerability_id', '')),
                            confidence=0.9,  # High confidence for known vulnerabilities
                            title=f"Vulnerable dependency: {vuln.get('package_name', '')}",
                            description=f"Vulnerable dependency found: {vuln.get('package_name', '')} {vuln.get('installed_version', '')}. {vuln.get('advisory', '')}",
                            line_number=0,
                            file_path="requirements.txt",
                            code_snippet=f"{vuln.get('package_name', '')}=={vuln.get('installed_version', '')}",
                            recommendation=f"Update {vuln.get('package_name', '')} to version {vuln.get('spec', 'latest')} or higher to fix this vulnerability."
                        )
                        findings.append(finding)
                except json.JSONDecodeError:
                    # Safety might return non-JSON output when no vulnerabilities found
                    self.logger.info("No vulnerabilities found by safety (or non-JSON output)")
                    
        except subprocess.TimeoutExpired:
            self.logger.error("Safety analysis timed out")
        except Exception as e:
            self.logger.error(f"Error running safety: {e}")
            
        return findings
    
    def _run_semgrep(self, temp_files: Dict[str, str]) -> List[SecurityFinding]:
        """Run semgrep security analysis on files."""
        import subprocess
        import json
        import tempfile
        import os
        
        findings = []
        
        if not temp_files:
            return findings
            
        try:
            # Create a temporary directory structure for semgrep
            with tempfile.TemporaryDirectory() as temp_dir:
                # Copy files to temp directory preserving relative paths
                for orig_path, temp_path in temp_files.items():
                    target_path = os.path.join(temp_dir, orig_path)
                    os.makedirs(os.path.dirname(target_path), exist_ok=True)
                    
                    # Copy the temp file content to the new location
                    with open(temp_path, 'r', encoding='utf-8', errors='ignore') as src:
                        with open(target_path, 'w', encoding='utf-8') as dst:
                            dst.write(src.read())
                
                # Run semgrep with security rules
                cmd = [
                    'semgrep', 
                    '--config=auto',  # Use automatic security rules
                    '--json',
                    '--quiet',
                    '--no-git-ignore',
                    temp_dir
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                
                if result.stdout:
                    try:
                        semgrep_data = json.loads(result.stdout)
                        
                        for finding_data in semgrep_data.get('results', []):
                            # Extract relative path from temp directory
                            full_path = finding_data.get('path', '')
                            relative_path = os.path.relpath(full_path, temp_dir) if temp_dir in full_path else full_path
                            
                            finding = SecurityFinding(
                                vulnerability_type=self._map_semgrep_rule_to_type(finding_data.get('check_id', '')),
                                severity=self._map_semgrep_severity(finding_data.get('extra', {}).get('severity', 'INFO')),
                                confidence=0.8,  # High confidence for semgrep rules
                                title=f"Semgrep: {finding_data.get('extra', {}).get('message', 'Security issue detected')}",
                                description=finding_data.get('extra', {}).get('message', 'Security issue detected by semgrep'),
                                line_number=finding_data.get('start', {}).get('line', 0),
                                file_path=relative_path,
                                code_snippet=finding_data.get('extra', {}).get('lines', ''),
                                recommendation=f"Review the flagged code and apply secure coding practices. Check semgrep rule {finding_data.get('check_id', '')} for specific guidance."
                            )
                            findings.append(finding)
                    except json.JSONDecodeError as e:
                        self.logger.error(f"Failed to parse semgrep JSON output: {e}")
                        
        except subprocess.TimeoutExpired:
            self.logger.error("Semgrep analysis timed out")
        except Exception as e:
            self.logger.error(f"Error running semgrep: {e}")
            
        return findings
    
    def _cleanup_temp_files(self, temp_files: Dict[str, str]):
        """Clean up temporary files."""
        import os
        
        for temp_path in temp_files.values():
            try:
                os.unlink(temp_path)
            except OSError:
                pass
    
    def _get_original_path(self, temp_path: str, temp_files: Dict[str, str]) -> str:
        """Get original file path from temporary file path."""
        for orig_path, t_path in temp_files.items():
            if t_path == temp_path:
                return orig_path
        return temp_path
    
    def _map_bandit_test_to_type(self, test_id: str) -> VulnerabilityType:
        """Map bandit test ID to vulnerability type."""
        mapping = {
            'B101': VulnerabilityType.HARDCODED_CREDENTIALS,
            'B102': VulnerabilityType.COMMAND_INJECTION,
            'B103': VulnerabilityType.PATH_TRAVERSAL,
            'B104': VulnerabilityType.HARDCODED_CREDENTIALS,
            'B105': VulnerabilityType.HARDCODED_CREDENTIALS,
            'B106': VulnerabilityType.HARDCODED_CREDENTIALS,
            'B107': VulnerabilityType.HARDCODED_CREDENTIALS,
            'B108': VulnerabilityType.PATH_TRAVERSAL,
            'B110': VulnerabilityType.COMMAND_INJECTION,
            'B201': VulnerabilityType.COMMAND_INJECTION,
            'B301': VulnerabilityType.DESERIALIZATION,
            'B302': VulnerabilityType.DESERIALIZATION,
            'B303': VulnerabilityType.WEAK_CRYPTO,
            'B304': VulnerabilityType.WEAK_CRYPTO,
            'B305': VulnerabilityType.WEAK_CRYPTO,
            'B306': VulnerabilityType.PATH_TRAVERSAL,
            'B307': VulnerabilityType.COMMAND_INJECTION,
            'B308': VulnerabilityType.HARDCODED_CREDENTIALS,
            'B309': VulnerabilityType.WEAK_CRYPTO,
            'B310': VulnerabilityType.UNVALIDATED_REDIRECT,
            'B311': VulnerabilityType.INSECURE_RANDOM,
            'B312': VulnerabilityType.PATH_TRAVERSAL,
            'B313': VulnerabilityType.XSS,
            'B314': VulnerabilityType.XSS,
            'B315': VulnerabilityType.XSS,
            'B316': VulnerabilityType.XSS,
            'B317': VulnerabilityType.XSS,
            'B318': VulnerabilityType.XSS,
            'B319': VulnerabilityType.XSS,
            'B320': VulnerabilityType.XSS,
            'B321': VulnerabilityType.PATH_TRAVERSAL,
            'B322': VulnerabilityType.COMMAND_INJECTION,
            'B323': VulnerabilityType.UNVALIDATED_REDIRECT,
            'B324': VulnerabilityType.WEAK_CRYPTO,
            'B325': VulnerabilityType.PATH_TRAVERSAL,
            'B404': VulnerabilityType.SECRET_EXPOSURE,
            'B501': VulnerabilityType.UNVALIDATED_REDIRECT,
            'B502': VulnerabilityType.WEAK_CRYPTO,
            'B503': VulnerabilityType.WEAK_CRYPTO,
            'B504': VulnerabilityType.WEAK_CRYPTO,
            'B505': VulnerabilityType.WEAK_CRYPTO,
            'B506': VulnerabilityType.XSS,
            'B507': VulnerabilityType.XSS,
            'B601': VulnerabilityType.COMMAND_INJECTION,
            'B602': VulnerabilityType.COMMAND_INJECTION,
            'B603': VulnerabilityType.COMMAND_INJECTION,
            'B604': VulnerabilityType.COMMAND_INJECTION,
            'B605': VulnerabilityType.COMMAND_INJECTION,
            'B606': VulnerabilityType.COMMAND_INJECTION,
            'B607': VulnerabilityType.COMMAND_INJECTION,
            'B608': VulnerabilityType.SQL_INJECTION,
            'B609': VulnerabilityType.COMMAND_INJECTION,
            'B610': VulnerabilityType.COMMAND_INJECTION,
            'B611': VulnerabilityType.COMMAND_INJECTION,
            'B701': VulnerabilityType.XSS,
            'B702': VulnerabilityType.COMMAND_INJECTION,
            'B703': VulnerabilityType.XSS
        }
        return mapping.get(test_id, VulnerabilityType.SECRET_EXPOSURE)
    
    def _map_bandit_severity(self, severity: str) -> Severity:
        """Map bandit severity to our severity enum."""
        mapping = {
            'HIGH': Severity.HIGH,
            'MEDIUM': Severity.MEDIUM,
            'LOW': Severity.LOW
        }
        return mapping.get(severity.upper(), Severity.INFO)
    
    def _map_bandit_confidence(self, confidence: str) -> float:
        """Map bandit confidence to float value."""
        mapping = {
            'HIGH': 0.9,
            'MEDIUM': 0.6,
            'LOW': 0.3
        }
        return mapping.get(confidence.upper(), 0.5)
    
    def _map_safety_severity(self, vuln_id: str) -> Severity:
        """Map safety vulnerability to severity (simplified approach)."""
        # This is a simplified approach - in reality you'd want to parse the CVE score
        return Severity.HIGH  # Default to high for known vulnerabilities
    
    def _map_semgrep_rule_to_type(self, check_id: str) -> VulnerabilityType:
        """Map semgrep rule ID to vulnerability type."""
        check_id_lower = check_id.lower()
        
        if 'injection' in check_id_lower or 'exec' in check_id_lower:
            return VulnerabilityType.COMMAND_INJECTION
        elif 'sql' in check_id_lower:
            return VulnerabilityType.SQL_INJECTION
        elif 'xss' in check_id_lower or 'cross-site' in check_id_lower:
            return VulnerabilityType.XSS
        elif 'secret' in check_id_lower or 'password' in check_id_lower or 'key' in check_id_lower:
            return VulnerabilityType.SECRET_EXPOSURE
        elif 'crypto' in check_id_lower or 'hash' in check_id_lower or 'cipher' in check_id_lower:
            return VulnerabilityType.WEAK_CRYPTO
        elif 'path' in check_id_lower or 'traversal' in check_id_lower:
            return VulnerabilityType.PATH_TRAVERSAL
        elif 'redirect' in check_id_lower:
            return VulnerabilityType.UNVALIDATED_REDIRECT
        elif 'deser' in check_id_lower or 'pickle' in check_id_lower:
            return VulnerabilityType.DESERIALIZATION
        else:
            return VulnerabilityType.SECRET_EXPOSURE
    
    def _map_semgrep_severity(self, severity: str) -> Severity:
        """Map semgrep severity to our severity enum."""
        mapping = {
            'ERROR': Severity.HIGH,
            'WARNING': Severity.MEDIUM,
            'INFO': Severity.LOW
        }
        return mapping.get(severity.upper(), Severity.INFO)

    def generate_report(self, findings: List[SecurityFinding]) -> dict:
        """Generate a structured security findings report."""
        summary = {
            "total_findings": len(findings),
            "severities": {},
        }
        for sev in Severity:
            summary[sev.value] = len([f for f in findings if f.severity == sev])
        summary["severities"] = {sev.value: summary[sev.value] for sev in Severity}
        report = {
            "summary": summary,
            "findings": [f.__dict__ for f in findings],
            "recommendations": list(set(f.recommendation for f in findings)),
        }
        return report

def scan_diff_file(diff_file_path: str) -> dict:
    """Scan a diff file for security issues and return a report."""
    import os
    if not os.path.exists(diff_file_path):
        return {"error": "Diff file not found"}
    with open(diff_file_path, 'r') as f:
        diff_content = f.read()
    analyzer = SecurityAnalyzer()
    findings = analyzer.analyze_diff(diff_content)
    return analyzer.generate_report(findings)
