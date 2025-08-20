#!/usr/bin/env python3
"""
Test script for security analyzer integration
"""

import sys
import os

# Add lib directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib'))

from security_analyzer import SecurityAnalyzer

def test_basic_security_scan():
    """Test basic security scanning functionality."""
    
    # Create a sample diff with security issues
    sample_diff = """diff --git a/test_file.py b/test_file.py
new file mode 100644
index 0000000..1234567
--- /dev/null
+++ b/test_file.py
@@ -0,0 +1,10 @@
+import os
+import subprocess
+
+# This should trigger bandit B602 - subprocess with shell=True
+def bad_function():
+    user_input = input("Enter command: ")
+    subprocess.call(user_input, shell=True)
+
+# This should trigger bandit B105 - hardcoded password
+password = "admin123"
"""
    
    print("Testing Security Analyzer...")
    analyzer = SecurityAnalyzer()
    
    print("Running security scan on sample diff...")
    findings = analyzer.analyze_diff(sample_diff)
    
    print(f"\nFound {len(findings)} security findings:")
    for i, finding in enumerate(findings, 1):
        print(f"\n{i}. {finding.title}")
        print(f"   File: {finding.file_path}")
        print(f"   Line: {finding.line_number}")
        print(f"   Severity: {finding.severity.value}")
        print(f"   Confidence: {finding.confidence}")
        print(f"   Description: {finding.description}")
        print(f"   Recommendation: {finding.recommendation}")
    
    if not findings:
        print("No security findings detected.")
    
    return len(findings)

if __name__ == "__main__":
    try:
        num_findings = test_basic_security_scan()
        print(f"\n✅ Test completed. Found {num_findings} security findings.")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
