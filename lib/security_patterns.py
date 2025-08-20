"""Security vulnerability and secret detection patterns for friendly-cicd-helper."""

# Example patterns for vulnerabilities and secrets
SECURITY_PATTERNS = [
    {
        "name": "SQL Injection",
        "pattern": r"SELECT.*\+|\+.*SELECT",
        "severity": "HIGH",
        "description": "Possible SQL injection via string concatenation in SQL queries."
    },
    {
        "name": "Hardcoded API Key",
        "pattern": r"(AIza[0-9A-Za-z-_]{35}|sk_live_[0-9a-zA-Z]{24,})",
        "severity": "HIGH",
        "description": "Possible hardcoded API key detected."
    },
    {
        "name": "Command Injection",
        "pattern": r"subprocess\\.call\\(.*\+.*\)",
        "severity": "CRITICAL",
        "description": "Possible command injection via user input in subprocess call."
    },
    # Add more patterns as needed
]

SECRET_PATTERNS = [
    {
        "name": "AWS Secret Key",
        "pattern": r"AKIA[0-9A-Z]{16}",
        "severity": "HIGH",
        "description": "Possible AWS secret key detected."
    },
    {
        "name": "Google API Key",
        "pattern": r"AIza[0-9A-Za-z-_]{35}",
        "severity": "HIGH",
        "description": "Possible Google API key detected."
    },
    # Add more secret patterns as needed
]
