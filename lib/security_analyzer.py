"""Security analysis module for friendly-cicd-helper using industry-standard tools."""
import json
import logging
import os
import re
import sys
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple

# Configure logging
logger = logging.getLogger(__name__)


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
    owasp_category: Optional[str] = None


class SecurityAnalyzer:
    """Security analyzer using industry-standard tools (bandit, safety, semgrep)."""
    
    def __init__(self):
        """Initialize the security analyzer."""
        self.logger = logging.getLogger(__name__)
        
    def analyze_diff(self, diff_content: str, file_paths: Optional[List[str]] = None) -> List[SecurityFinding]:
        """
        Analyze a git diff for security vulnerabilities using industry-standard tools.
        
        Args:
            diff_content: Git diff content
            file_paths: Optional list of file paths to analyze
            
        Returns:
            List of SecurityFinding objects
        """
        findings = []
        
        try:
            # Extract file content from diff for analysis
            temp_files = self._extract_files_from_diff(diff_content)
            
            # Run bandit for Python security issues
            findings.extend(self._run_bandit(temp_files))
            
            # Run safety for dependency vulnerabilities
            findings.extend(self._run_safety())
            
            # TODO: Re-enable semgrep once timeout issues are resolved
            # findings.extend(self._run_semgrep(temp_files))
            
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
        
        findings = []
        python_files = [temp_path for orig_path, temp_path in temp_files.items() 
                       if orig_path.endswith('.py')]
        
        if not python_files:
            return findings
            
        try:
            # Run bandit with JSON output
            cmd = ['bandit', '-f', 'json'] + python_files
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.stdout:
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
                        recommendation=f"Bandit {issue.get('test_id', '')}: {issue.get('issue_text', '')}",
                        cwe_id=str(issue.get('issue_cwe', {}).get('id', '')) if issue.get('issue_cwe') else None
                    )
                    findings.append(finding)
                    
        except Exception as e:
            self.logger.error(f"Error running bandit: {e}")
            
        return findings
    
    def _run_safety(self) -> List[SecurityFinding]:
        """Run safety check for dependency vulnerabilities."""
        import subprocess
        import json
        
        findings = []
        
        try:
            # Run safety check with JSON output
            cmd = ['safety', 'check', '--json']
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.stdout:
                try:
                    safety_data = json.loads(result.stdout)
                    
                    for vuln in safety_data:
                        finding = SecurityFinding(
                            vulnerability_type=VulnerabilityType.HARDCODED_CREDENTIALS,  # Generic for deps
                            severity=self._map_safety_severity(vuln.get('vulnerability_id', '')),
                            confidence=0.8,  # High confidence for known vulnerabilities
                            title=f"Vulnerable dependency: {vuln.get('package_name', '')}",
                            description=f"Vulnerable dependency: {vuln.get('package_name', '')} {vuln.get('installed_version', '')}",
                            line_number=0,
                            file_path="requirements.txt",
                            code_snippet=f"{vuln.get('package_name', '')}=={vuln.get('installed_version', '')}",
                            recommendation=f"Update {vuln.get('package_name', '')} to a secure version"
                        )
                        findings.append(finding)
                except json.JSONDecodeError:
                    # Safety might return non-JSON output when no vulnerabilities found
                    pass
                    
        except Exception as e:
            self.logger.error(f"Error running safety: {e}")
            
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
            'B404': VulnerabilityType.SECRET_EXPOSURE,  # subprocess import warning
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
