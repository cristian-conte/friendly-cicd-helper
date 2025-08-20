"""Tests for the security analyzer module."""

import unittest
import tempfile
import os
from lib.security_analyzer import SecurityAnalyzer, VulnerabilityType, Severity


class TestSecurityAnalyzer(unittest.TestCase):
    """Test cases for SecurityAnalyzer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = SecurityAnalyzer()
    
    def test_sql_injection_detection(self):
        """Test SQL injection vulnerability detection."""
        diff_content = '''diff --git a/app.py b/app.py
index 1234567..8901234 100644
--- a/app.py
+++ b/app.py
@@ -1,5 +1,5 @@
 def get_user(user_id):
-    query = "SELECT * FROM users WHERE id = ?"
+    query = "SELECT * FROM users WHERE id = " + user_id
     return execute_query(query)
'''
        findings = self.analyzer.analyze_diff(diff_content)
        
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].vulnerability_type, VulnerabilityType.SQL_INJECTION)
        self.assertEqual(findings[0].severity, Severity.HIGH)
    
    def test_secret_detection(self):
        """Test secret exposure detection."""
        diff_content = '''diff --git a/config.py b/config.py
index 1234567..8901234 100644
--- a/config.py
+++ b/config.py
@@ -1,3 +1,4 @@
 DATABASE_URL = "postgresql://localhost/mydb"
+API_KEY = "AIzaSyDXQlWe7iWlXXXXXXXXXXXXXXXXXXXXXXX"
 DEBUG = True
'''
        findings = self.analyzer.analyze_diff(diff_content)
        
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].vulnerability_type, VulnerabilityType.SECRET_EXPOSURE)
        self.assertEqual(findings[0].severity, Severity.HIGH)
        self.assertIn("Google API Key", findings[0].title)
    
    def test_command_injection_detection(self):
        """Test command injection vulnerability detection."""
        diff_content = '''diff --git a/utils.py b/utils.py
index 1234567..8901234 100644
--- a/utils.py
+++ b/utils.py
@@ -1,5 +1,5 @@
 import subprocess
 def run_cmd(user_input):
-    return subprocess.run(['ls', user_input])
+    return subprocess.call("ls " + user_input, shell=True)
'''
        findings = self.analyzer.analyze_diff(diff_content)
        
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].vulnerability_type, VulnerabilityType.COMMAND_INJECTION)
        self.assertEqual(findings[0].severity, Severity.CRITICAL)
    
    def test_no_vulnerabilities(self):
        """Test that clean code produces no findings."""
        diff_content = '''diff --git a/safe.py b/safe.py
index 1234567..8901234 100644
--- a/safe.py
+++ b/safe.py
@@ -1,5 +1,6 @@
 import os
 def get_env_var():
     return os.getenv('DATABASE_URL', 'default_value')
+    # This is a safe comment
'''
        findings = self.analyzer.analyze_diff(diff_content)
        
        self.assertEqual(len(findings), 0)
    
    def test_confidence_calculation(self):
        """Test confidence calculation for findings."""
        pattern_info = {"pattern": r"SELECT.*\+", "severity": Severity.HIGH}
        line_content = "query = 'SELECT * FROM users WHERE id = ' + user_id"
        
        confidence = self.analyzer._calculate_confidence(pattern_info, line_content)
        
        self.assertGreater(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)
    
    def test_secret_masking(self):
        """Test that secrets are properly masked in output."""
        line_content = 'API_KEY = "sk-1234567890abcdef1234567890abcdef"'
        masked = self.analyzer._mask_secret(line_content)
        
        self.assertNotIn("sk-1234567890abcdef1234567890abcdef", masked)
        self.assertIn("****", masked)
    
    def test_report_generation(self):
        """Test security report generation."""
        diff_content = '''diff --git a/test.py b/test.py
index 1234567..8901234 100644
--- a/test.py
+++ b/test.py
@@ -1,3 +1,4 @@
 def test():
+    query = "SELECT * FROM users WHERE id = " + user_id
     pass
'''
        findings = self.analyzer.analyze_diff(diff_content)
        report = self.analyzer.generate_report(findings)
        
        self.assertIn("summary", report)
        self.assertIn("findings", report)
        self.assertIn("recommendations", report)
        self.assertEqual(report["summary"]["total_findings"], len(findings))
    
    def test_empty_report(self):
        """Test report generation with no findings."""
        report = self.analyzer.generate_report([])
        
        self.assertEqual(report["summary"]["total_findings"], 0)
        self.assertEqual(len(report["findings"]), 0)
    
    def test_diff_parsing(self):
        """Test git diff parsing functionality."""
        diff_content = '''diff --git a/test.py b/test.py
index 1234567..8901234 100644
--- a/test.py
+++ b/test.py
@@ -1,3 +1,5 @@
 def test():
+    # Added line 1
+    # Added line 2
     pass
'''
        parsed_lines = self.analyzer._parse_diff(diff_content)
        
        # Should find 2 added lines
        added_lines = [line for line in parsed_lines if line[2].startswith('+')]
        self.assertEqual(len(added_lines), 2)


class TestSecurityScanFunction(unittest.TestCase):
    """Test cases for scan_diff_file function."""
    
    def test_scan_valid_diff_file(self):
        """Test scanning a valid diff file."""
        from lib.security_analyzer import scan_diff_file
        
        # Create a temporary diff file
        diff_content = '''diff --git a/test.py b/test.py
index 1234567..8901234 100644
--- a/test.py
+++ b/test.py
@@ -1,3 +1,4 @@
 def test():
+    password = "hardcoded_password_123"
     pass
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.patch', delete=False) as f:
            f.write(diff_content)
            temp_file = f.name
        
        try:
            report = scan_diff_file(temp_file)
            
            self.assertNotIn("error", report)
            self.assertIn("summary", report)
            self.assertGreater(report["summary"]["total_findings"], 0)
        finally:
            os.unlink(temp_file)
    
    def test_scan_nonexistent_file(self):
        """Test scanning a non-existent file."""
        from lib.security_analyzer import scan_diff_file
        
        report = scan_diff_file("/nonexistent/file.patch")
        
        self.assertIn("error", report)
        self.assertEqual(report["error"], "Diff file not found")


if __name__ == '__main__':
    unittest.main()
