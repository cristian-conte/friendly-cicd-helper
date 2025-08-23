"""
Test cases for the Test Intelligence Analyzer.

This module tests the test_analyzer.py functionality including:
- Coverage analysis
- Test quality assessment
- Test gap detection
- AI-powered test suggestions
"""

import unittest
import tempfile
import os
from unittest.mock import patch, MagicMock
from lib.test_analyzer import (
    TestIntelligenceAnalyzer, 
    TestFinding, 
    TestIssueType, 
    TestIssueSeverity
)


class TestTestIntelligenceAnalyzer(unittest.TestCase):
    """Test cases for TestIntelligenceAnalyzer."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = TestIntelligenceAnalyzer()
        
        # Sample diff content for testing
        self.sample_diff = """diff --git a/src/calculator.py b/src/calculator.py
new file mode 100644
index 0000000..1234567
--- /dev/null
+++ b/src/calculator.py
@@ -0,0 +1,15 @@
+def add(a, b):
+    '''Add two numbers.'''
+    return a + b
+
+def divide(a, b):
+    '''Divide two numbers.'''
+    if b == 0:
+        raise ValueError("Cannot divide by zero")
+    return a / b
+
+def complex_calculation(x, y, z):
+    '''Perform complex calculation with multiple conditions.'''
+    if x > 0:
+        if y > 0:
+            return x * y + z
+        else:
+            return x - z
+    elif x < 0:
+        return abs(x) + y
+    else:
+        return z
"""
        
        self.sample_test_diff = """diff --git a/tests/test_calculator.py b/tests/test_calculator.py
new file mode 100644
index 0000000..1234567
--- /dev/null
+++ b/tests/test_calculator.py
@@ -0,0 +1,20 @@
+import unittest
+from src.calculator import add, divide
+
+class TestCalculator(unittest.TestCase):
+    
+    def test_add(self):
+        # This is a very long test method that does too many things
+        # Line 1 of test
+        # Line 2 of test
+        # Line 3 of test
+        # Line 4 of test
+        # Line 5 of test
+        # Line 6 of test
+        # Line 7 of test
+        # Line 8 of test
+        # Line 9 of test
+        # Line 10 of test
+        # Line 11 of test
+        # Line 12 of test
+        # Line 13 of test
+        # Line 14 of test
+        # Line 15 of test
+        # Line 16 of test
+        # Line 17 of test
+        # Line 18 of test
+        # Line 19 of test
+        # Line 20 of test
+        # Line 21 of test
+        # Line 22 of test
+        assert True  # Weak assertion
+    
+    def test_divide_basic(self):
+        result = divide(10, 2)
+        assert result == 5
"""
    
    def test_extract_files_from_diff(self):
        """Test extracting files from git diff."""
        temp_files = self.analyzer._extract_files_from_diff(self.sample_diff)
        
        self.assertIn('src/calculator.py', temp_files)
        self.assertTrue(os.path.exists(temp_files['src/calculator.py']))
        
        # Check content is correctly extracted
        with open(temp_files['src/calculator.py'], 'r') as f:
            content = f.read()
            self.assertIn('def add(a, b):', content)
            self.assertIn('def complex_calculation(x, y, z):', content)
        
        # Clean up
        self.analyzer._cleanup_temp_files(temp_files)
    
    def test_detect_test_smells(self):
        """Test detection of test smells in test files."""
        lines = [
            "import unittest",
            "",
            "class TestExample(unittest.TestCase):",
            "    def test_long_method(self):",
            "        # Line 1", "        # Line 2", "        # Line 3", "        # Line 4",
            "        # Line 5", "        # Line 6", "        # Line 7", "        # Line 8",
            "        # Line 9", "        # Line 10", "        # Line 11", "        # Line 12",
            "        # Line 13", "        # Line 14", "        # Line 15", "        # Line 16",
            "        # Line 17", "        # Line 18", "        # Line 19", "        # Line 20",
            "        # Line 21", "        # Line 22", "        # Line 23",
            "        assert True",
            "",
            "    def test_weak_assertion(self):",
            "        assert True"
        ]
        
        findings = self.analyzer._detect_test_smells('test_example.py', lines)
        
        # Should detect long test method
        long_test_findings = [f for f in findings if 'lines long' in f.description]
        self.assertEqual(len(long_test_findings), 1)
        
        # Should detect weak assertions
        weak_assertion_findings = [f for f in findings if 'weak assertion' in f.title.lower()]
        self.assertEqual(len(weak_assertion_findings), 2)  # Two assert True statements
    
    def test_detect_untested_functions(self):
        """Test detection of functions that need testing."""
        lines = [
            "def simple_function():",
            "    return True",
            "",
            "def complex_function(x, y):",
            "    if x > 0:",
            "        for i in range(y):",
            "            if i % 2 == 0:",
            "                continue",
            "        return x * y",
            "    else:",
            "        try:",
            "            return x / y",
            "        except ZeroDivisionError:",
            "            return 0",
            "",
            "def _private_function():",
            "    return False"
        ]
        
        findings = self.analyzer._detect_untested_functions('example.py', lines)
        
        # Should detect complex_function but not simple_function or private function
        complex_findings = [f for f in findings if 'complex_function' in f.description]
        self.assertEqual(len(complex_findings), 1)
        
        # Should not detect private functions
        private_findings = [f for f in findings if '_private_function' in f.description]
        self.assertEqual(len(private_findings), 0)
    
    def test_is_complex_function(self):
        """Test function complexity detection."""
        # Simple function - not complex
        simple_lines = [
            "def simple_func():",
            "    return True"
        ]
        self.assertFalse(self.analyzer._is_complex_function(simple_lines, 0))
        
        # Complex function with multiple conditions
        complex_lines = [
            "def complex_func(x, y):",
            "    if x > 0:",
            "        for i in range(y):",
            "            if i % 2 == 0:",
            "                continue",
            "        return x * y",
            "    else:",
            "        try:",
            "            return x / y",
            "        except ZeroDivisionError:",
            "            return 0"
        ]
        self.assertTrue(self.analyzer._is_complex_function(complex_lines, 0))
        
        # Long function - should be considered complex
        long_lines = ["def long_func():"] + [f"    line_{i} = {i}" for i in range(15)]
        self.assertTrue(self.analyzer._is_complex_function(long_lines, 0))
    
    def test_count_test_length(self):
        """Test counting test method length."""
        lines = [
            "class TestExample:",
            "    def test_method(self):",
            "        line1 = 1",
            "        line2 = 2",
            "        line3 = 3",
            "        assert line1 == 1",
            "",
            "    def another_method(self):",
            "        pass"
        ]
        
        # Should count 6 lines in test_method (including def line and empty line)
        length = self.analyzer._count_test_length(lines, 1)  # Start at test_method line
        self.assertEqual(length, 6)  # Including the def line and empty line
    
    def test_map_coverage_to_severity(self):
        """Test coverage percentage to severity mapping."""
        self.assertEqual(
            self.analyzer._map_coverage_to_severity(30), 
            TestIssueSeverity.CRITICAL
        )
        self.assertEqual(
            self.analyzer._map_coverage_to_severity(60), 
            TestIssueSeverity.HIGH
        )
        self.assertEqual(
            self.analyzer._map_coverage_to_severity(75), 
            TestIssueSeverity.MEDIUM
        )
        self.assertEqual(
            self.analyzer._map_coverage_to_severity(85), 
            TestIssueSeverity.LOW
        )
    
    @patch('subprocess.run')
    def test_coverage_analysis_no_tests(self, mock_run):
        """Test coverage analysis when no test files exist."""
        # Mock that no test files are found
        with patch.object(self.analyzer, '_find_test_files', return_value=[]):
            temp_files = {'src/example.py': '/tmp/example.py'}
            findings = self.analyzer._run_coverage_analysis(temp_files)
            
            # Should create findings for missing tests
            self.assertEqual(len(findings), 1)
            self.assertEqual(findings[0].issue_type, TestIssueType.COVERAGE_GAP)
            self.assertIn('No test files found', findings[0].title)
    
    @patch('os.walk')
    @patch('os.path.exists')
    def test_find_test_files(self, mock_exists, mock_walk):
        """Test finding existing test files."""
        # Mock file system structure
        def side_effect(path):
            return path in ['tests', 'test', '.']
        mock_exists.side_effect = side_effect
        
        def walk_side_effect(test_dir):
            if test_dir == 'tests':
                return [('tests', [], ['test_example.py', 'test_utils.py', 'not_a_test.py'])]
            else:
                return []
        mock_walk.side_effect = walk_side_effect
        
        test_files = self.analyzer._find_test_files()
        
        # Should find only files starting with test_
        self.assertEqual(len(test_files), 2)
        self.assertIn('tests/test_example.py', test_files)
        self.assertIn('tests/test_utils.py', test_files)
    
    def test_generate_report(self):
        """Test report generation."""
        findings = [
            TestFinding(
                issue_type=TestIssueType.COVERAGE_GAP,
                severity=TestIssueSeverity.HIGH,
                confidence=0.9,
                title="Low coverage",
                description="File has low coverage",
                file_path="src/example.py",
                line_number=10,
                code_snippet="def func():",
                recommendation="Add tests",
                coverage_percentage=45.0,
                test_file_suggestion="tests/test_example.py"
            ),
            TestFinding(
                issue_type=TestIssueType.TEST_SMELL,
                severity=TestIssueSeverity.MEDIUM,
                confidence=0.8,
                title="Test smell",
                description="Test has issues",
                file_path="tests/test_example.py",
                line_number=20,
                code_snippet="assert True",
                recommendation="Fix assertion"
            )
        ]
        
        report = self.analyzer.generate_report(findings)
        
        # Check report structure
        self.assertEqual(report['summary']['total_findings'], 2)
        self.assertEqual(report['summary']['coverage_gaps'], 1)
        self.assertEqual(report['summary']['test_smells'], 1)
        self.assertEqual(report['summary']['missing_tests'], 1)
        self.assertEqual(report['summary']['average_coverage'], 45.0)
        
        # Check findings are converted to dicts
        self.assertEqual(len(report['findings']), 2)
        self.assertEqual(report['findings'][0]['issue_type'], 'coverage_gap')
        
        # Check suggestions
        self.assertIn('tests/test_example.py', report['suggested_test_files'])
    
    def test_finding_to_dict(self):
        """Test converting TestFinding to dictionary."""
        finding = TestFinding(
            issue_type=TestIssueType.COVERAGE_GAP,
            severity=TestIssueSeverity.HIGH,
            confidence=0.9,
            title="Test title",
            description="Test description",
            file_path="test/path.py",
            line_number=42,
            code_snippet="test code",
            recommendation="Test recommendation",
            coverage_percentage=75.5,
            test_file_suggestion="tests/test_path.py"
        )
        
        finding_dict = self.analyzer._finding_to_dict(finding)
        
        # Check all fields are converted
        self.assertEqual(finding_dict['issue_type'], 'coverage_gap')
        self.assertEqual(finding_dict['severity'], 'high')
        self.assertEqual(finding_dict['confidence'], 0.9)
        self.assertEqual(finding_dict['title'], 'Test title')
        self.assertEqual(finding_dict['coverage_percentage'], 75.5)
        self.assertEqual(finding_dict['test_file_suggestion'], 'tests/test_path.py')


class TestTestFinding(unittest.TestCase):
    """Test cases for TestFinding dataclass."""
    
    def test_test_finding_creation(self):
        """Test creating a TestFinding object."""
        finding = TestFinding(
            issue_type=TestIssueType.COVERAGE_GAP,
            severity=TestIssueSeverity.HIGH,
            confidence=0.9,
            title="Test Coverage Gap",
            description="Low test coverage detected",
            file_path="src/example.py",
            line_number=42,
            code_snippet="def example():",
            recommendation="Add test cases"
        )
        
        self.assertEqual(finding.issue_type, TestIssueType.COVERAGE_GAP)
        self.assertEqual(finding.severity, TestIssueSeverity.HIGH)
        self.assertEqual(finding.confidence, 0.9)
        self.assertEqual(finding.title, "Test Coverage Gap")
        self.assertEqual(finding.line_number, 42)
        self.assertIsNone(finding.coverage_percentage)
        self.assertIsNone(finding.test_file_suggestion)


if __name__ == '__main__':
    unittest.main()
