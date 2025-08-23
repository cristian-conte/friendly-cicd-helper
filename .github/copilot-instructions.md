# Friendly CI/CD Helper - Repository Instructions
## IMPORTANT DEVELOPER WORKFLOW
**Always use**:
- **Serena tool** for semantic code retrieval and editing tools
- **Context7 tool** for up-to-date documentation on third-party libraries
- **Sequential thinking tool** for any decision making or complex analysis
- **Always commit** after each complete task with detailed commit messages
- **Use new branches** for new features or bug fixes

## Project Overview

**Purpose**: `friendly-cicd-helper` is a Python CLI tool that integrates Google Cloud Vertex AI with CI/CD pipelines to provide automated code analysis. 

**Core Functionality**: 
- **AI-Powered Code Analysis**: Generates code review summaries, comments, and release notes using Vertex AI
- **Security Vulnerability Scanning**: Integrates industry-standard tools (Bandit, Safety, Semgrep) for comprehensive security analysis
- **Platform Integration**: Works with both GitHub and GitLab APIs for automated commenting on issues, PRs, and MRs
- **CI/CD Pipeline Support**: Deployable as standalone Python app, Docker container, or integrated into Cloud Build pipelines

**Repository Size**: Small-to-medium Python project (~15 core files, 222 lines in main CLI)
**Languages**: Python 3.10 (primary), Docker, YAML (configurations)
**Target Runtime**: Google Cloud (Vertex AI, Cloud Build), local development, containerized deployment

## Repository Structure and Key Files

### Root Directory
- **`friendly-cicd-helper.py`** - Main CLI entry point (222 lines, Click framework)
- **`requirements.txt`** - Python dependencies including security tools
- **`Dockerfile`** - Container image (Python 3.10-slim base)
- **`cloudbuild.yaml`** - Google Cloud Build configuration
- **`README.md`** - Project documentation and quick start guide
- **`setup.sh`** - Cloud Build deployment script

### Library Directory (`lib/`)
- **`vertex_api.py`** - Vertex AI integration (WORKING: code summaries, reviews, release notes)
- **`github_api.py`** - GitHub API functions (WORKING: issue/PR commenting)
- **`gitlab_api.py`** - GitLab API functions (WORKING: issue/MR commenting)
- **`security_analyzer.py`** - Security analysis core (WORKING: Bandit, Safety, Semgrep integration)
- **`config.py`** - Configuration management
- **`logging_config.py`** - Logging setup

### Testing (`tests/`)
- **`test_security_analyzer.py`** - Security analyzer unit tests
- **`test_security_integration.py`** - Integration tests for security tools
- **Multiple test files** - Comprehensive test coverage

### Documentation (`docs/`)
- **`USAGE.md`** - Detailed usage examples and commands
- **`SECURITY_INTEGRATION.md`** - Security analysis guide
- **`demo-pipeline/`** - Cloud Build pipeline examples

## Technology Stack and Dependencies

**Core Framework**: Click 8.1.7 (CLI), Python 3.10
**AI/ML**: google-cloud-aiplatform 1.52.0 (Vertex AI with Gemini 2.5 Flash)
**Platform APIs**: PyGithub 2.2.0, python-gitlab 4.4.0
**Security Tools**: bandit 1.7.5, safety 3.0.1, semgrep 1.45.0
**Infrastructure**: Docker, Google Cloud Build, Google Container Registry

## Build and Validation Instructions

### Environment Setup (REQUIRED)
```bash
# Required environment variables
export VERTEX_GCP_PROJECT=<your-gcp-project>  # REQUIRED for Vertex AI
export GOOGLE_CLOUD_QUOTA_PROJECT=$VERTEX_GCP_PROJECT  # REQUIRED for quotas
export GITHUB_TOKEN=<token>  # Optional: for GitHub operations
export GITLAB_TOKEN=<token>  # Optional: for GitLab operations
```

### Local Development Setup
```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Test CLI help (validates basic setup)
python friendly-cicd-helper.py --help

# 3. Verify security tools are available
bandit --version
safety --version
semgrep --version
```

### Docker Build and Validation
```bash
# 1. Build container (takes 2-3 minutes)
docker build . -t friendly-cicd-helper

# 2. Test container
docker run friendly-cicd-helper --help

# 3. Test with volume mount for local files
docker run -v $(pwd):/workspace -w /workspace friendly-cicd-helper vertex-code-summary --diff <file>
```

### Testing
**Note**: No formal testing framework configured. Use manual testing approach:
```bash
# Test CLI commands
python friendly-cicd-helper.py --help

# Test with sample diff (create test diff first)
git diff HEAD~1 HEAD > test.diff
python friendly-cicd-helper.py vertex-code-summary --diff test.diff
python friendly-cicd-helper.py security-scan --diff test.diff --format text
```

## Available CLI Commands

### WORKING Commands
- **`github-issue-comment`** - Post comments to GitHub issues
- **`github-pr-comment`** - Post comments to GitHub pull requests  
- **`github-latest-pr`** - Get latest PR for a repository branch
- **`gitlab-comment`** - Post comments to GitLab issues or merge requests
- **`gitlab-mergerequest`** - Get latest MR for a repository branch
- **`vertex-code-summary`** - Generate AI-powered code change summaries
- **`vertex-code-review`** - Generate AI-powered code review comments
- **`vertex-release-notes`** - Generate AI-powered release notes
- **`security-scan`** - Run security analysis with Bandit, Safety, Semgrep

### MISSING Commands (Referenced in docs but not implemented)
- **`vertex-security-scan`** - Planned but not implemented (use `security-scan` instead)

## Current Implementation Status

### ✅ COMPLETED Features
- Core CLI framework with Click
- GitHub/GitLab API integrations
- Vertex AI integration (code summaries, reviews, release notes)
- Security analysis with industry-standard tools (Bandit, Safety, Semgrep)
- Docker containerization
- Cloud Build pipeline integration
- Comprehensive test coverage

### ❌ MISSING Features (Open GitHub Issues)
- **`lib/security_patterns.py`** - Referenced in tests but file doesn't exist
- **SARIF output format** - Planned but not implemented
- **Performance analysis module** (`lib/performance_analyzer.py`) - Not implemented
- **PR intelligence module** (`lib/pr_intelligence.py`) - Not implemented
- **Methods referenced in tests** - Some test methods expect functions that don't exist

## Development Guidelines

### Code Style Conventions
- Use Click framework for all CLI commands with proper options and help text
- Follow Google Cloud Python client library patterns
- Use environment variables for authentication (never hardcode tokens)
- Implement proper error handling with user-friendly messages to stderr
- Add type hints where appropriate

### Environment Variable Handling
```python
# Standard pattern for env vars
import os
project = os.environ.get('VERTEX_GCP_PROJECT')
if not project:
    click.echo("Error: VERTEX_GCP_PROJECT environment variable required", err=True)
    sys.exit(1)
```

### Security Tool Integration Pattern
The SecurityAnalyzer class in `lib/security_analyzer.py` provides the standard pattern:
- Extract files from git diff
- Run multiple security tools in parallel
- Aggregate and normalize findings
- Support both JSON and text output formats

## Validation and Quality Checks

### Manual Testing Checklist
- [ ] CLI help displays correctly: `python friendly-cicd-helper.py --help`
- [ ] Docker builds successfully: `docker build . -t friendly-cicd-helper`
- [ ] Security tools are functional: Test with sample diff
- [ ] Environment variables are handled properly
- [ ] Error messages go to stderr and are user-friendly

### Before Making Changes
1. **Test existing functionality** with sample diffs
2. **Verify environment setup** with required variables
3. **Check dependencies** in requirements.txt match actual usage
4. **Test Docker build** after any dependency changes
5. **Update documentation** if adding new commands or changing behavior

## Important Notes for Development

- **Trust these instructions** - They reflect the current accurate state of the repository
- **Check GitHub issues** for planned vs. implemented features before adding new functionality
- **Security tools require network access** for vulnerability database updates
- **Vertex AI requires active GCP project** with billing enabled
- **Test with real git diffs** rather than synthetic examples for realistic validation
---

