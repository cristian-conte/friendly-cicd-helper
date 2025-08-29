"""
Test Intelligence Analyzer for friendly-cicd-helper.

This module provides intelligent test analysis capabilities using industry-standard tools:
- coverage.py for test coverage analysis
- pytest for test discovery and quality assessment
- mutmut for mutation testing
- AI-powered test generation and gap analysis
"""

import sys
import os
import logging
import subprocess
import json
import tempfile
import shutil
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from lib.utils import extract_files_from_diff
from enum import Enum


class TestIssueType(Enum):
    """Types of test-related issues that can be detected."""
    COVERAGE_GAP = "coverage_gap"
    POOR_TEST_QUALITY = "poor_test_quality"
    MISSING_EDGE_CASES = "missing_edge_cases"
    TEST_SMELL = "test_smell"
    MUTATION_SURVIVOR = "mutation_survivor"


class TestIssueSeverity(Enum):
    """Severity levels for test issues."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class TestFinding:
    """Represents a test-related finding."""
    issue_type: TestIssueType
    severity: TestIssueSeverity
    confidence: float
    title: str
    description: str
    file_path: str
    line_number: int
    code_snippet: str
    recommendation: str
    coverage_percentage: Optional[float] = None
    test_file_suggestion: Optional[str] = None


class TestIntelligenceAnalyzer:
    """Test intelligence analyzer using industry-standard tools and AI."""
    
    def __init__(self, test_length_threshold: int = 20):
        """Initialize the test intelligence analyzer.
        
        Args:
            test_length_threshold: Maximum number of lines for a test method before it's flagged as too long
        """
        self.logger = logging.getLogger(__name__)
        self.test_length_threshold = test_length_threshold
        
    def analyze_diff(self, diff_content: str) -> List[TestFinding]:
        """
        Analyze a git diff for test-related issues and opportunities.
        
        Args:
            diff_content: Git diff content
            
        Returns:
            List of TestFinding objects
        """
        findings = []
        
        try:
            # Extract file content from diff for analysis
            temp_files = extract_files_from_diff(diff_content)
            
            if not temp_files:
                self.logger.info("No files to analyze in diff")
                return findings
            
            # Run coverage analysis
            self.logger.info("Running coverage analysis...")
            findings.extend(self._run_coverage_analysis(temp_files))
            
            # Run test quality analysis
            self.logger.info("Running test quality analysis...")
            findings.extend(self._run_test_quality_analysis(temp_files))
            
            # Run test discovery analysis
            self.logger.info("Running test discovery analysis...")
            findings.extend(self._run_test_discovery_analysis(temp_files))
            
            # Clean up temporary files
            self._cleanup_temp_files(temp_files)
            
        except Exception as e:
            self.logger.error(f"Error during test intelligence analysis: {e}")
            
        return findings
    
    def _run_coverage_analysis(self, temp_files: Dict[str, str]) -> List[TestFinding]:
        """Run coverage analysis on Python files."""
        findings = []
        python_files = [orig_path for orig_path in temp_files.keys() 
                       if orig_path.endswith('.py') and not orig_path.startswith('test_')]
        
        if not python_files:
            self.logger.info("No source Python files found for coverage analysis")
            return findings
            
        try:
            # Check if we have any test files in the project
            test_files = self._find_test_files()
            if not test_files:
                # Create a finding about missing tests
                for py_file in python_files:
                    finding = TestFinding(
                        issue_type=TestIssueType.COVERAGE_GAP,
                        severity=TestIssueSeverity.HIGH,
                        confidence=0.9,
                        title=f"No test files found for {py_file}",
                        description=f"Source file {py_file} has been modified but no corresponding test files exist in the project.",
                        file_path=py_file,
                        line_number=0,
                        code_snippet="",
                        recommendation=f"Create test file tests/test_{os.path.basename(py_file)} to ensure code quality and prevent regressions.",
                        coverage_percentage=0.0,
                        test_file_suggestion=f"tests/test_{os.path.basename(py_file)}"
                    )
                    findings.append(finding)
                return findings
            
            # Run coverage analysis using pytest with coverage
            python_path = sys.executable
            
            # Create a temporary directory to run tests from
            with tempfile.TemporaryDirectory() as temp_dir:
                # Copy source files to temp directory
                for orig_path, temp_path in temp_files.items():
                    if orig_path.endswith('.py'):
                        target_path = os.path.join(temp_dir, orig_path)
                        os.makedirs(os.path.dirname(target_path), exist_ok=True)
                        
                        import shutil
                        shutil.copyfile(temp_path, target_path)
                
                # Run coverage with pytest
                cmd = [
                    python_path, '-m', 'coverage', 'run', 
                    '--source', temp_dir,
                    '-m', 'pytest', 
                    '--tb=no', '-q',
                    temp_dir
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60, cwd=temp_dir)
                
                # Get coverage report
                report_cmd = [python_path, '-m', 'coverage', 'report', '--format=json']
                report_result = subprocess.run(report_cmd, capture_output=True, text=True, timeout=30, cwd=temp_dir)
                
                if report_result.stdout:
                    try:
                        coverage_data = json.loads(report_result.stdout)
                        
                        for file_data in coverage_data.get('files', {}).values():
                            file_path = file_data.get('filename', '')
                            coverage_percent = file_data.get('summary', {}).get('percent_covered', 0)
                            missing_lines = file_data.get('missing_lines', [])
                            
                            if coverage_percent < 80:  # Configurable threshold
                                finding = TestFinding(
                                    issue_type=TestIssueType.COVERAGE_GAP,
                                    severity=self._map_coverage_to_severity(coverage_percent),
                                    confidence=0.9,
                                    title=f"Low test coverage in {os.path.basename(file_path)}",
                                    description=f"File has {coverage_percent:.1f}% test coverage, below recommended 80% threshold.",
                                    file_path=self._get_original_path(file_path, temp_files),
                                    line_number=missing_lines[0] if missing_lines else 0,
                                    code_snippet=f"Coverage: {coverage_percent:.1f}%, Missing lines: {missing_lines[:5]}...",
                                    recommendation=f"Add test cases to improve coverage. Focus on lines {missing_lines[:10]}.",
                                    coverage_percentage=coverage_percent
                                )
                                findings.append(finding)
                    except json.JSONDecodeError as e:
                        self.logger.error(f"Failed to parse coverage JSON output: {e}")
                        
        except subprocess.TimeoutExpired:
            self.logger.error("Coverage analysis timed out")
        except Exception as e:
            self.logger.error(f"Error running coverage analysis: {e}")
            
        return findings
    
    def _run_test_quality_analysis(self, temp_files: Dict[str, str]) -> List[TestFinding]:
        """Analyze test file quality for test smells and issues."""
        findings = []
        test_files = [orig_path for orig_path in temp_files.keys() 
                     if orig_path.endswith('.py') and 'test_' in orig_path]
        
        if not test_files:
            self.logger.info("No test files found for quality analysis")
            return findings
        
        try:
            for orig_path, temp_path in temp_files.items():
                if not ('test_' in orig_path and orig_path.endswith('.py')):
                    continue
                    
                # Analyze test file content for common issues
                with open(temp_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    lines = content.split('\n')
                    
                    # Check for test smells
                    findings.extend(self._detect_test_smells(orig_path, lines))
                    
        except Exception as e:
            self.logger.error(f"Error running test quality analysis: {e}")
            
        return findings
    
    def _run_test_discovery_analysis(self, temp_files: Dict[str, str]) -> List[TestFinding]:
        """Analyze for missing test cases and edge cases."""
        findings = []
        python_files = [orig_path for orig_path in temp_files.keys() 
                       if orig_path.endswith('.py') and not orig_path.startswith('test_')]
        
        for orig_path, temp_path in temp_files.items():
            if not (orig_path.endswith('.py') and not orig_path.startswith('test_')):
                continue
                
            try:
                with open(temp_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    lines = content.split('\n')
                    
                    # Look for functions/methods that might need testing
                    findings.extend(self._detect_untested_functions(orig_path, lines))
                    
            except Exception as e:
                self.logger.error(f"Error analyzing {orig_path}: {e}")
                
        return findings
    
    def _detect_test_smells(self, file_path: str, lines: List[str]) -> List[TestFinding]:
        """Detect common test smells in test files."""
        findings = []
        
        for i, line in enumerate(lines, 1):
            # Test smell: Tests that are too long
            if line.strip().startswith('def test_'):
                test_length = self._count_test_length(lines, i-1)
                if test_length > self.test_length_threshold:
                    finding = TestFinding(
                        issue_type=TestIssueType.TEST_SMELL,
                        severity=TestIssueSeverity.MEDIUM,
                        confidence=0.7,
                        title=f"Test method too long in {os.path.basename(file_path)}",
                        description=f"Test method is {test_length} lines long, making it hard to understand and maintain.",
                        file_path=file_path,
                        line_number=i,
                        code_snippet=line.strip(),
                        recommendation="Break down the test into smaller, focused test methods or use helper methods."
                    )
                    findings.append(finding)
            
            # Test smell: Weak assertions
            if 'assert True' in line or 'assert 1' in line:
                finding = TestFinding(
                    issue_type=TestIssueType.TEST_SMELL,
                    severity=TestIssueSeverity.HIGH,
                    confidence=0.9,
                    title=f"Weak assertion in {os.path.basename(file_path)}",
                    description="Test contains weak assertion that doesn't verify meaningful behavior.",
                    file_path=file_path,
                    line_number=i,
                    code_snippet=line.strip(),
                    recommendation="Replace with meaningful assertions that verify specific behavior."
                )
                findings.append(finding)
        
        return findings
    
    def _detect_untested_functions(self, file_path: str, lines: List[str]) -> List[TestFinding]:
        """Detect functions that might need testing."""
        findings = []
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Look for function definitions
            if stripped.startswith('def ') and not stripped.startswith('def _'):
                func_name = stripped.split('(')[0].replace('def ', '')
                
                # Skip if it's already a test function
                if func_name.startswith('test_'):
                    continue
                
                # Check for complex functions that likely need testing
                if self._is_complex_function(lines, i-1):
                    finding = TestFinding(
                        issue_type=TestIssueType.COVERAGE_GAP,
                        severity=TestIssueSeverity.MEDIUM,
                        confidence=0.8,
                        title=f"Complex function may need testing: {func_name}",
                        description=f"Function '{func_name}' contains complex logic that should be tested.",
                        file_path=file_path,
                        line_number=i,
                        code_snippet=stripped,
                        recommendation=f"Create test cases for function '{func_name}' covering normal and edge cases.",
                        test_file_suggestion=f"tests/test_{os.path.basename(file_path)}"
                    )
                    findings.append(finding)
        
        return findings
    
    def _find_test_files(self) -> List[str]:
        """Find existing test files in the project."""
        test_files = []
        
        # Look for test files in common locations
        test_dirs = ['tests', 'test', '.']
        
        for test_dir in test_dirs:
            if os.path.exists(test_dir):
                for root, dirs, files in os.walk(test_dir):
                    for file in files:
                        if file.startswith('test_') and file.endswith('.py'):
                            test_files.append(os.path.join(root, file))
        
        return test_files
    
    def _count_test_length(self, lines: List[str], start_idx: int) -> int:
        """Count the number of lines in a test method."""
        count = 0
        indent_level = None
        
        for i in range(start_idx, len(lines)):
            line = lines[i]
            
            if not line.strip():  # Skip empty lines but continue counting
                count += 1
                continue
                
            current_indent = len(line) - len(line.lstrip())
            
            if indent_level is None:
                indent_level = current_indent
                count += 1
            elif current_indent > indent_level:
                # Still inside the method
                count += 1
            elif current_indent <= indent_level and line.strip() and i > start_idx:
                # We've reached the end of the method (another method or class)
                break
            else:
                count += 1
                
        return count
    
    def _is_complex_function(self, lines: List[str], start_idx: int) -> bool:
        """Determine if a function is complex enough to need testing."""
        complexity_indicators = ['if ', 'for ', 'while ', 'try:', 'except', 'elif', 'else:']
        
        function_lines = []
        indent_level = None
        
        for i in range(start_idx, len(lines)):
            line = lines[i]
            
            if not line.strip():
                continue
                
            current_indent = len(line) - len(line.lstrip())
            
            if indent_level is None:
                indent_level = current_indent
            elif current_indent <= indent_level and line.strip() and not line.strip().startswith('@'):
                break
                
            function_lines.append(line)
        
        # Check for complexity indicators
        complexity_count = sum(1 for line in function_lines 
                             for indicator in complexity_indicators 
                             if indicator in line)
        
        return complexity_count >= 2 or len(function_lines) > 10
    
    def _map_coverage_to_severity(self, coverage_percent: float) -> TestIssueSeverity:
        """Map coverage percentage to severity level."""
        if coverage_percent < 50:
            return TestIssueSeverity.CRITICAL
        elif coverage_percent < 70:
            return TestIssueSeverity.HIGH
        elif coverage_percent < 80:
            return TestIssueSeverity.MEDIUM
        else:
            return TestIssueSeverity.LOW
    
    def _cleanup_temp_files(self, temp_files: Dict[str, str]):
        """Clean up temporary files."""
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
    
    def generate_report(self, findings: List[TestFinding]) -> dict:
        """Generate a structured test intelligence report."""
        summary = {
            "total_findings": len(findings),
            "coverage_gaps": len([f for f in findings if f.issue_type == TestIssueType.COVERAGE_GAP]),
            "test_smells": len([f for f in findings if f.issue_type == TestIssueType.TEST_SMELL]),
            "missing_tests": len([f for f in findings if f.test_file_suggestion]),
            "severities": {}
        }
        
        for sev in TestIssueSeverity:
            summary["severities"][sev.value] = len([f for f in findings if f.severity == sev])
        
        # Calculate average coverage if available
        coverage_findings = [f for f in findings if f.coverage_percentage is not None]
        if coverage_findings:
            summary["average_coverage"] = sum(f.coverage_percentage for f in coverage_findings if f.coverage_percentage is not None) / len(coverage_findings)
        
        report = {
            "summary": summary,
            "findings": [self._finding_to_dict(f) for f in findings],
            "recommendations": list(set(f.recommendation for f in findings)),
            "suggested_test_files": list(set(f.test_file_suggestion for f in findings if f.test_file_suggestion))
        }
        
        return report
    
    def _finding_to_dict(self, finding: TestFinding) -> dict:
        """Convert a TestFinding to a dictionary."""
        return {
            "issue_type": finding.issue_type.value,
            "severity": finding.severity.value,
            "confidence": finding.confidence,
            "title": finding.title,
            "description": finding.description,
            "file_path": finding.file_path,
            "line_number": finding.line_number,
            "code_snippet": finding.code_snippet,
            "recommendation": finding.recommendation,
            "coverage_percentage": finding.coverage_percentage,
            "test_file_suggestion": finding.test_file_suggestion
        }
