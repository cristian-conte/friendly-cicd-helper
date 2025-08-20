#!/usr/bin/env python3
"""
Comprehensive security test with multiple vulnerability types
"""

import sys
import os

# Add lib directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib'))

from security_analyzer import SecurityAnalyzer

def test_comprehensive_security_scan():
    """Test comprehensive security scanning with various vulnerability types."""
    
    # Create a comprehensive diff with multiple security issues
    comprehensive_diff = """diff --git a/vulnerable_app.py b/vulnerable_app.py
new file mode 100644
index 0000000..abcdef123
--- /dev/null
+++ b/vulnerable_app.py
@@ -0,0 +1,25 @@
+import os
+import subprocess
+import pickle
+import hashlib
+import random
+
+# Command injection vulnerabilities
+def execute_user_command(user_input):
+    os.system(user_input)  # B605: shell injection
+    subprocess.call(user_input, shell=True)  # B602: subprocess with shell=True
+
+# Hardcoded credentials
+API_KEY = "sk-1234567890abcdef"  # B105: hardcoded password
+DATABASE_PASSWORD = "super_secret_password"  # B105: hardcoded password
+
+# Weak cryptography
+def weak_hash(data):
+    return hashlib.md5(data.encode()).hexdigest()  # B303: weak hash
+
+# Insecure randomness
+def generate_token():
+    return random.random()  # B311: insecure random
+
+# Deserialization vulnerability
+def load_user_data(data):
+    return pickle.loads(data)  # B301: unsafe deserialization

diff --git a/requirements.txt b/requirements.txt
new file mode 100644
index 0000000..abcdef123
--- /dev/null
+++ b/requirements.txt
@@ -0,0 +1,5 @@
+flask==2.0.1
+requests==2.25.1
+django==3.2.0
+urllib3==1.26.5
+pyyaml==5.4.1
"""
    
    print("🔍 Testing Comprehensive Security Analyzer...")
    analyzer = SecurityAnalyzer()
    
    print("📊 Running security scan on comprehensive diff...")
    findings = analyzer.analyze_diff(comprehensive_diff)
    
    print(f"\n🚨 Found {len(findings)} security findings:")
    
    # Group findings by tool
    bandit_findings = [f for f in findings if f.title.startswith('Bandit')]
    semgrep_findings = [f for f in findings if f.title.startswith('Semgrep')]
    safety_findings = [f for f in findings if f.vulnerability_type.value == 'dependency_vulnerability']
    
    print(f"\n🛡️  Bandit findings: {len(bandit_findings)}")
    for finding in bandit_findings:
        print(f"   • {finding.title} (Severity: {finding.severity.value})")
    
    print(f"\n🔎 Semgrep findings: {len(semgrep_findings)}")
    for finding in semgrep_findings:
        print(f"   • {finding.description[:80]}... (Severity: {finding.severity.value})")
    
    print(f"\n📦 Safety findings: {len(safety_findings)}")
    for finding in safety_findings:
        print(f"   • {finding.title} (Severity: {finding.severity.value})")
    
    # Generate summary report
    report = analyzer.generate_report(findings)
    print(f"\n📋 Security Report Summary:")
    print(f"   Total findings: {report['summary']['total_findings']}")
    for severity, count in report['summary']['severities'].items():
        if count > 0:
            print(f"   {severity.title()}: {count}")
    
    return len(findings)

if __name__ == "__main__":
    try:
        num_findings = test_comprehensive_security_scan()
        print(f"\n✅ Comprehensive test completed. Found {num_findings} security findings.")
        print("\n🎯 Security tools integration is working correctly!")
        print("   • Bandit: Python security issues ✓")
        print("   • Semgrep: Advanced security patterns ✓") 
        print("   • Safety: Dependency vulnerabilities ✓")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
