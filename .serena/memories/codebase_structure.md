# Updated Codebase Structure

## Root Directory Files
- **`friendly-cicd-helper.py`** - Main CLI entry point with Click commands (updated with security-scan command)
- **`requirements.txt`** - Python dependencies (includes bandit, safety, semgrep)
- **`Dockerfile`** - Container build configuration (Python 3.10-slim)
- **`cloudbuild.yaml`** - Google Cloud Build configuration for image building
- **`setup.sh`** - Quick setup script for Cloud Build deployment
- **`setup-github-project.sh`** - GitHub-specific setup script
- **`README.md`** - Project documentation and getting started guide
- **`CONTRIBUTING.md`** - Contribution guidelines (Google CLA requirements)
- **`LICENSE`** - Apache 2.0 license
- **`.gitignore`** - Enhanced Git ignore rules (Python artifacts, security tools, cache files)

## Library Directory (`lib/`)
- **`github_api.py`** - GitHub API integration functions
  - `issue_comment()` - Post comments to GitHub issues
  - `pull_request_comment()` - Post comments to GitHub PRs
  - `get_latest_pull_request()` - Get latest PR for repo
- **`gitlab_api.py`** - GitLab API integration functions
  - `issue_comment()` - Post comments to GitLab issues
  - `merge_request_comment()` - Post comments to GitLab MRs
  - `get_latest_merge_request()` - Get latest MR for repo
- **`vertex_api.py`** - Vertex AI integration
  - `load_diff()` - Load and format git diff files
  - `code_summary()` - Generate code change summaries
  - `code_review()` - Generate code review comments
  - `release_notes()` - Generate release notes
- **`security_analyzer.py`** (NEW) - Security analysis core module
  - `SecurityAnalyzer` class with industry-standard tool integration
  - `analyze_diff()` - Main analysis method
  - `_run_bandit()`, `_run_safety()`, `_run_semgrep()` - Tool-specific methods
- **`security_patterns.py`** (NEW) - Security pattern definitions and utilities
- **`config.py`** (NEW) - Configuration management
- **`logging_config.py`** (NEW) - Logging configuration
- **`vertex_api_bak.py`** - Backup of original vertex API

## Tests Directory (`tests/`) - REORGANIZED
- **`__init__.py`** - Test package initialization
- **`test_security_analyzer.py`** - Unit tests for SecurityAnalyzer
- **`test_security_integration.py`** - Integration tests for security tools
- **`test_comprehensive_security.py`** - Comprehensive security testing
- **`test_tools_direct.py`** - Direct tool testing
- **`test_security.py`** - Legacy security tests
- **`test_diff.txt`** - Test diff file for security analysis
- **`test_security_diff.patch`** - Security-focused test patch file

## Documentation Directory (`docs/`) - ENHANCED
- **`USAGE.md`** - Detailed usage instructions and examples
- **`SECURITY_INTEGRATION.md`** (NEW) - Comprehensive security integration guide
- **`CLOUDBUILD_SECURITY_INTEGRATION.md`** (NEW) - Cloud Build security integration documentation
- **`demo-pipeline/`** - Cloud Build pipeline examples
  - `gitlab-comment.yaml` - Example GitLab integration pipeline
  - `print-cli-help.yaml` - Simple help output pipeline
  - `security-scan-demo.yaml` (NEW) - Security scan demonstration pipeline
- **`img/`** - Screenshots and images for documentation

## Cloud Build Directory (`.github/cloudbuild/`)
- **`cloudbuild_github.yml`** - GitHub-specific pipeline (enhanced with security scanning)
- **`cloudbuild_gitlab.yml`** - GitLab-specific pipeline (enhanced with security scanning)
- **`cloudbuild.yml`** - Hybrid pipeline (enhanced with security scanning)

## CLI Commands Structure
- **`cli()`** - Main Click group
- **`github_issue_comment()`** - GitHub issue commenting
- **`github_pr_comment()`** - GitHub PR commenting  
- **`github_latest_pr()`** - Get latest GitHub PR
- **`gitlab_comment()`** - GitLab issue commenting
- **`gitlab_mergerequest()`** - GitLab MR operations
- **`vertex_code_summary()`** - Generate AI summaries
- **`vertex_code_review()`** - Generate AI reviews
- **`vertex_release_notes()`** - Generate AI release notes
- **`security_scan()`** (NEW) - Security vulnerability scanning with industry tools

## Key Design Patterns
- **Modular API clients** - Separate modules for each external service
- **Industry-Standard Security** - Bandit, Safety, Semgrep integration instead of custom patterns
- **Environment-based configuration** - Uses env vars for credentials and settings
- **Composable CLI** - Commands designed to pipe output to each other
- **Dual Format Support** - JSON for automation, text for human readability
- **Error handling** - Graceful failures with helpful error messages to stderr
- **Professional CI/CD Integration** - Automated security scanning in all pipelines