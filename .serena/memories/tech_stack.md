# Updated Tech Stack and Dependencies

## Programming Language
- **Python 3.10** - Base language (as defined in Dockerfile)

## Core Dependencies
- **click==8.1.7** - CLI framework for command-line interface
- **PyGithub==2.2.0** - GitHub API integration
- **python-gitlab==4.4.0** - GitLab API integration  
- **google-cloud-aiplatform==1.52.0** - Vertex AI integration

## Security Analysis Tools (NEW)
- **bandit==1.7.5** - Python security vulnerability detection
  - SAST (Static Application Security Testing) for Python
  - Detects common security issues like SQL injection, hardcoded passwords
  - JSON output support for automation
- **safety==3.0.1** - Python dependency vulnerability scanning
  - Checks Python packages against CVE database
  - Identifies known vulnerabilities in dependencies
  - JSON output for structured reporting
- **semgrep** - Multi-language security analysis
  - Uses `--config=auto` for comprehensive rule sets
  - Supports Python, JavaScript, Java, Go, and more
  - Community and proprietary rule sets

## Infrastructure & Deployment
- **Docker** - Containerization (Python 3.10-slim base image)
- **Google Cloud Build** - CI/CD pipeline support with security scanning
- **Google Cloud Vertex AI** - AI/ML services (Gemini 2.5 Flash model)
- **Google Container Registry** - Container image storage

## Development & Testing
- **pytest** - Testing framework for comprehensive test coverage
- **Virtual Environment** - Isolated Python environment with all tools pre-installed
- **Git Integration** - Diff analysis and automated commenting

## Environment Configuration
Environment variables for configuration:
- **VERTEX_GCP_PROJECT** - Google Cloud project for Vertex AI
- **VERTEX_LOCATION** - Vertex AI location/region
- **GITHUB_TOKEN** - GitHub API authentication
- **GITLAB_TOKEN** - GitLab API authentication

## Architecture Components
- **Main CLI**: `friendly-cicd-helper.py` - Entry point with Click commands
- **Core Libraries**: 
  - `lib/vertex_api.py` - Vertex AI integration
  - `lib/github_api.py` - GitHub API functions
  - `lib/gitlab_api.py` - GitLab API functions
  - `lib/security_analyzer.py` (NEW) - Security analysis with industry tools
  - `lib/security_patterns.py` (NEW) - Security pattern definitions
  - `lib/config.py` (NEW) - Configuration management
  - `lib/logging_config.py` (NEW) - Logging setup

## CI/CD Integration Features
- **Automated Security Scanning** - Every code change analyzed
- **Dual Output Formats** - JSON for machines, text for humans
- **Multi-Platform Support** - GitHub and GitLab pipelines
- **Artifact Storage** - Security reports saved as build artifacts
- **Professional Formatting** - Enhanced output with emojis and clear attribution

## Security Analysis Workflow
1. **Git Diff Generation** - Extract changes from commits
2. **Multi-Tool Analysis** - Run Bandit, Safety, and Semgrep in parallel
3. **Results Aggregation** - Combine findings from all tools
4. **Format Output** - Generate both JSON and text reports
5. **Automated Commenting** - Post findings to PRs/MRs
6. **Artifact Storage** - Save JSON reports for audit trails