# Tech Stack and Dependencies

## Programming Language
- **Python 3.10** - Base language (as defined in Dockerfile)

## Core Dependencies
- **click==8.1.7** - CLI framework for command-line interface
- **PyGithub==2.2.0** - GitHub API integration
- **python-gitlab==4.4.0** - GitLab API integration  
- **google-cloud-aiplatform==1.52.0** - Vertex AI integration

## Infrastructure & Deployment
- **Docker** - Containerization (Python 3.10-slim base image)
- **Google Cloud Build** - CI/CD pipeline support
- **Google Cloud Vertex AI** - AI/ML services (Gemini 2.5 Flash model)
- **Google Container Registry** - Container image storage

## Development Environment
- Supports both local Python execution and containerized deployment
- Environment variables for configuration (VERTEX_GCP_PROJECT, VERTEX_LOCATION, GITHUB_TOKEN, GITLAB_TOKEN)

## Architecture
- **Main CLI**: `friendly-cicd-helper.py` - Entry point with Click commands
- **Library modules**: 
  - `lib/vertex_api.py` - Vertex AI integration
  - `lib/github_api.py` - GitHub API functions
  - `lib/gitlab_api.py` - GitLab API functions