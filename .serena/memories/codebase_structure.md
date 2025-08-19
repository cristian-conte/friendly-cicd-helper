# Codebase Structure

## Root Directory Files
- **`friendly-cicd-helper.py`** - Main CLI entry point with Click commands
- **`requirements.txt`** - Python dependencies
- **`Dockerfile`** - Container build configuration (Python 3.10-slim)
- **`cloudbuild.yaml`** - Google Cloud Build configuration
- **`setup.sh`** - Quick setup script for Cloud Build deployment
- **`README.md`** - Project documentation and getting started guide
- **`CONTRIBUTING.md`** - Contribution guidelines (Google CLA requirements)
- **`LICENSE`** - Apache 2.0 license
- **`.gitignore`** - Git ignore rules (Python artifacts, VS Code, GCloud CLI)

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

## Documentation Directory (`docs/`)
- **`USAGE.md`** - Detailed usage instructions and examples
- **`demo-pipeline/`** - Cloud Build pipeline examples
  - `gitlab-comment.yaml` - Example GitLab integration pipeline
  - `print-cli-help.yaml` - Simple help output pipeline
- **`img/`** - Screenshots and images for documentation

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

## Key Design Patterns
- **Modular API clients** - Separate modules for each external service
- **Environment-based configuration** - Uses env vars for credentials and settings
- **Composable CLI** - Commands designed to pipe output to each other
- **Error handling** - Graceful failures with helpful error messages to stderr