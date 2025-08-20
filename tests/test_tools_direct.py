#!/usr/bin/env python3
"""
Simple test to check if security tools are working
"""

import subprocess
import sys
import json

def test_bandit():
    """Test bandit directly"""
    print("Testing bandit...")
    
    # Create a simple test file with security issue
    test_code = '''
import subprocess
subprocess.call("ls", shell=True)  # Should trigger B602
password = "admin123"  # Should trigger B105
'''
    
    with open('/tmp/test_bandit.py', 'w') as f:
        f.write(test_code)
    
    try:
        cmd = ['/Users/cristian/Documents/dev/Ravl/friendly-cicd-helper-1/venv/bin/python', '-m', 'bandit', '-f', 'json', '/tmp/test_bandit.py']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        print(f"Bandit exit code: {result.returncode}")
        print(f"Stdout: {result.stdout[:500]}")
        print(f"Stderr: {result.stderr[:500]}")
        
        if result.stdout:
            try:
                data = json.loads(result.stdout)
                print(f"Found {len(data.get('results', []))} bandit findings")
                return True
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
        
    except Exception as e:
        print(f"Error: {e}")
    
    return False

def test_safety():
    """Test safety directly"""
    print("\nTesting safety...")
    
    try:
        cmd = ['/Users/cristian/Documents/dev/Ravl/friendly-cicd-helper-1/venv/bin/python', '-m', 'safety', 'check', '--json']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        print(f"Safety exit code: {result.returncode}")
        print(f"Stdout: {result.stdout[:500]}")
        print(f"Stderr: {result.stderr[:500]}")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
    
    return False

def test_semgrep():
    """Test semgrep directly"""
    print("\nTesting semgrep...")
    
    # Create a simple test file with security issue
    test_code = '''
import subprocess
subprocess.call("ls", shell=True)  # Should trigger semgrep rule
'''
    
    with open('/tmp/test_semgrep.py', 'w') as f:
        f.write(test_code)
    
    try:
        cmd = ['semgrep', '--config=auto', '--json', '--quiet', '/tmp/test_semgrep.py']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        
        print(f"Semgrep exit code: {result.returncode}")
        print(f"Stdout: {result.stdout[:500]}")
        print(f"Stderr: {result.stderr[:500]}")
        
        if result.stdout:
            try:
                data = json.loads(result.stdout)
                print(f"Found {len(data.get('results', []))} semgrep findings")
                return True
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
        
    except Exception as e:
        print(f"Error: {e}")
    
    return False

if __name__ == "__main__":
    print("Testing security tools directly...")
    
    bandit_ok = test_bandit()
    safety_ok = test_safety()
    semgrep_ok = test_semgrep()
    
    print(f"\nResults:")
    print(f"Bandit: {'✅' if bandit_ok else '❌'}")
    print(f"Safety: {'✅' if safety_ok else '❌'}")
    print(f"Semgrep: {'✅' if semgrep_ok else '❌'}")
