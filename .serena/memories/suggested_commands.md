# Suggested Commands for Development

## Environment Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Set required environment variables
export VERTEX_GCP_PROJECT=<your-project-id>
export GITHUB_TOKEN=<your-github-token>  # For GitHub operations
export GITLAB_TOKEN=<your-gitlab-token>  # For GitLab operations
export VERTEX_LOCATION=us-central1       # Optional, defaults to us-central1
export GOOGLE_CLOUD_QUOTA_PROJECT=$VERTEX_GCP_PROJECT  # For quota management
```

## Running the Application

### Local Python Execution
```bash
# Show help
python friendly-cicd-helper.py --help

# Generate code summary
python friendly-cicd-helper.py vertex-code-summary --diff /path/to/git.diff

# Generate code review
python friendly-cicd-helper.py vertex-code-review --diff /path/to/git.diff

# Generate release notes
python friendly-cicd-helper.py vertex-release-notes --diff /path/to/git.diff

# Comment on GitHub issue
python friendly-cicd-helper.py github-comment --repo user/repo --issue 1 --comment "text"

# Comment on GitLab issue
python friendly-cicd-helper.py gitlab-comment --repo user/repo --issue 1 --comment "text"
```

### Container Usage
```bash
# Build container
docker build . -t friendly-cicd-helper

# Run with help
docker run friendly-cicd-helper --help

# Run with environment variables
docker run --env GITHUB_TOKEN=$GITHUB_TOKEN friendly-cicd-helper github-comment --repo user/repo --issue 1 --comment "test"
```

## Cloud Build Deployment
```bash
# Set variables
PROJECT_ID=<your-project-id>
REGION=europe-west1
REPO_NAME=default
IMAGE_PATH="$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/friendly-cicd-helper"

# Submit build and test
gcloud builds submit . --substitutions "_IMAGE_PATH=$IMAGE_PATH"
gcloud builds submit --config ./docs/demo-pipeline/print-cli-help.yaml --substitutions "_IMAGE_PATH=$IMAGE_PATH"
```

## System Utilities (macOS)
```bash
# File operations
ls -la                    # List files
find . -name "*.py"       # Find Python files
grep -r "pattern" .       # Search in files
cat filename              # Display file content

# Git operations
git status
git diff
git add .
git commit -m "message"
git push

# Directory navigation
cd /path/to/directory
pwd                       # Current directory
```

## Composable Command Examples
```bash
# Generate summary and comment on GitLab
python friendly-cicd-helper.py vertex-code-summary --diff $GIT_DIFF_PATH | \
python friendly-cicd-helper.py gitlab-comment --repo user/repo --issue 1
```