## IMPORTANT, DO NOT FORGET
## Always use:
- serena tool for semantic code retrieval and editing tools
- context7 tool for up to date documentation on third party code
- sequential tool thinking for any decision making
- Always commit after each complete task. Use detailed commit messages. 
- Use new branches for new features or bug fixes.

# GitHub Copilot Instructions for Friendly CI/CD Helper

## Project Overview

This is `friendly-cicd-helper`, a Python CLI tool that integrates Vertex AI with CI/CD pipelines to provide automated code review assistance. The tool analyzes git diffs and generates:

- Code review summaries and comments
- Release notes
- PR/MR feedback

It supports both GitHub and GitLab integrations and can be used as a standalone Python application, container image, or within Cloud Build pipelines.

## Architecture and Key Components

### Main Entry Point
- `friendly-cicd-helper.py` - Click-based CLI application with commands for GitHub, GitLab, and Vertex AI operations

### Core Libraries (`lib/` directory)
- `github_api.py` - GitHub API integration for commenting on issues and PRs
- `gitlab_api.py` - GitLab API integration for commenting on MRs and issues  
- `vertex_api.py` - Google Cloud Vertex AI integration for code analysis

### Infrastructure
- `Dockerfile` - Container image definition
- `cloudbuild.yaml` - Google Cloud Build pipeline configuration
- `.github/cloudbuild/cloudbuild.yml` - Conditional Cloud Build config for GitHub/GitLab triggers

## Development Guidelines

### Code Style and Patterns
- Use Click framework for CLI commands with proper options and help text
- Follow Google Cloud Python client library patterns for API integrations
- Use environment variables for authentication tokens and configuration
- Implement proper error handling and user-friendly error messages
- Add type hints where appropriate

### API Integration Patterns
- **GitHub**: Use PyGithub library, authenticate with `GITHUB_TOKEN` environment variable
- **GitLab**: Use python-gitlab library, authenticate with `GITLAB_TOKEN` environment variable  
- **Vertex AI**: Use google-cloud-aiplatform library, authenticate with GCP credentials

### CLI Command Structure
Commands should follow this pattern:
```python
@cli.command()
@click.option('--param', required=True, help='Description')
def command_name(param):
    """Command description."""
    # Implementation
```

### Cloud Build Integration
- Use substitution variables for configuration (`_GITLAB_PROJECT`, `_GITHUB_PROJECT`, `_REPO_TYPE`)
- Implement conditional logic based on repository type (GitLab vs GitHub)
- Store sensitive data in Google Secret Manager
- Use appropriate Docker images for each build step

### Testing and Validation
- Test CLI commands with both required and optional parameters
- Validate API integrations with both GitHub and GitLab
- Test container builds and Cloud Build pipeline execution
- Ensure proper error handling for network failures and API rate limits

## Common Tasks

### Adding New CLI Commands
1. Add new command function with Click decorators
2. Implement proper option validation and help text
3. Add corresponding API integration if needed
4. Update documentation and help output

### Modifying API Integrations
1. Update relevant library file (`github_api.py`, `gitlab_api.py`, `vertex_api.py`)
2. Ensure proper error handling and logging
3. Test with actual API endpoints
4. Update CLI commands that use the modified API

### Updating Cloud Build Configuration
1. Modify `.github/cloudbuild/cloudbuild.yml` for conditional logic
2. Update substitution variables as needed
3. Test with both GitHub and GitLab triggers
4. Ensure secrets are properly configured

## Dependencies and External Services

### Required Services
- Google Cloud Vertex AI (for code analysis)
- GitHub API (for GitHub integration)
- GitLab API (for GitLab integration)
- Google Cloud Build (for CI/CD pipelines)

### Environment Variables
- `GITHUB_TOKEN` - GitHub personal access token
- `GITLAB_TOKEN` - GitLab personal access token  
- `VERTEX_GCP_PROJECT` - Google Cloud project ID for Vertex AI

## Security Considerations

- Never commit API tokens or secrets to the repository
- Use Google Secret Manager for sensitive data in Cloud Build
- Validate input parameters to prevent injection attacks
- Use least-privilege access for API tokens
- Regularly rotate API tokens and secrets

