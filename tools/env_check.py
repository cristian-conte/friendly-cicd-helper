#!/usr/bin/env python3
"""
Utility to verify Python executable path and security tools availability.
This helps debug environment-specific issues.
"""
import sys
import subprocess
import os
from pathlib import Path


def check_python_executable():
    """Check the current Python executable and its environment."""
    print("🐍 Python Environment Check")
    print("=" * 40)
    print(f"Python executable: {sys.executable}")
    print(f"Python version: {sys.version}")
    print(f"Python path: {sys.path[0] if sys.path else 'N/A'}")
    print()


def check_security_tools():
    """Check if security tools are available in the current environment."""
    tools = {
        'bandit': [sys.executable, '-m', 'bandit', '--version'],
        'safety': [sys.executable, '-m', 'safety', '--version'],
        'semgrep': ['semgrep', '--version']
    }
    
    print("🔧 Security Tools Check")
    print("=" * 40)
    
    for tool_name, cmd in tools.items():
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                version = result.stdout.strip() or result.stderr.strip()
                print(f"✅ {tool_name}: {version.split()[0] if version else 'Available'}")
            else:
                print(f"❌ {tool_name}: Command failed (exit code: {result.returncode})")
        except subprocess.TimeoutExpired:
            print(f"⏱️ {tool_name}: Timeout")
        except FileNotFoundError:
            print(f"❌ {tool_name}: Not found")
        except Exception as e:
            print(f"❌ {tool_name}: Error - {e}")
    print()


def check_environment_compatibility():
    """Check if the environment is suitable for security scanning."""
    print("🌍 Environment Compatibility")
    print("=" * 40)
    
    # Check if we're in a virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Virtual environment detected")
    else:
        print("⚠️  Not in a virtual environment")
    
    # Check if we're in a container
    if os.path.exists('/.dockerenv'):
        print("🐳 Docker container detected")
    elif os.environ.get('KUBERNETES_SERVICE_HOST'):
        print("☸️  Kubernetes environment detected")
    else:
        print("💻 Local environment")
    
    # Check current working directory
    print(f"📂 Working directory: {os.getcwd()}")
    
    # Check if requirements.txt exists
    if Path('requirements.txt').exists():
        print("✅ requirements.txt found")
    else:
        print("⚠️  requirements.txt not found")
    
    print()


def main():
    """Run all environment checks."""
    print("🔍 Friendly CI/CD Helper - Environment Diagnostic")
    print("=" * 60)
    print()
    
    check_python_executable()
    check_security_tools()
    check_environment_compatibility()
    
    print("✨ Diagnostic complete!")


if __name__ == '__main__':
    main()
