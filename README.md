# Friendly CI/CD Helper

`friendly-cicd-helper` is a powerful tool that leverages Vertex AI to streamline common CI/CD tasks. By analyzing code changes in the form of a Git diff, it automatically generates insightful summaries, constructive code reviews, and clear release notes.

## Key Features

- **Automated Code Summaries**: Get a high-level overview of pull requests and merge requests, making code reviews faster and more efficient.
- **AI-Powered Code Reviews**: Receive instant feedback on your code, identifying potential issues and suggesting improvements to enhance code quality.
- **Effortless Release Notes**: Automatically generate well-structured release notes from your commit history, saving you time and effort.
- **Seamless Integration**: Easily integrate with GitHub and GitLab to post comments on issues, pull requests, and merge requests.

## Getting Started

You can use `friendly-cicd-helper` as a standalone Python application, a container image, or within a CI/CD pipeline.

### Prerequisites

- Python 3.8+
- [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
- [Docker](https://docs.docker.com/get-docker/)

### Installation

1.  **Clone the repository:**
    ```sh
    git clone https://github.com/GoogleCloudPlatform/friendly-cicd-helper.git
    cd friendly-cicd-helper
    ```

2.  **Install dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

### Configuration

Before you can use `friendly-cicd-helper`, you need to set up the following environment variables:

- `GITHUB_TOKEN`: A GitHub personal access token with `repo` scope.
- `GITLAB_TOKEN`: A GitLab personal access token with `api` scope.
- `VERTEX_GCP_PROJECT`: The ID of your Google Cloud project.
- `VERTEX_LOCATION`: The Google Cloud region where you want to run Vertex AI jobs (e.g., `us-central1`).

### Usage

The `friendly-cicd-helper` provides a command-line interface (CLI) for easy interaction.

**Container Image**

1.  **Build the Docker image:**
    ```sh
    docker build . -t friendly-cicd-helper
    ```

2.  **Run the container:**
    ```sh
    docker run -e GITHUB_TOKEN -e GITLAB_TOKEN -e VERTEX_GCP_PROJECT -e VERTEX_LOCATION friendly-cicd-helper --help
    ```

**Python Application**

```sh
python friendly-cicd-helper.py --help
```

**Cloud Build Pipeline**

1.  **Build the image and submit the pipeline:**
    ```sh
    # adapt these with your values
    PROJECT_ID=<your-project-id>
    REGION=europe-west1
    REPO_NAME=default
    IMAGE_PATH="$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/friendly-cicd-helper"

    gcloud builds submit . --substitutions "_IMAGE_PATH=$IMAGE_PATH"
    gcloud builds submit --config ./docs/demo-pipeline/print-cli-help.yaml --substitutions "_IMAGE_PATH=$IMAGE_PATH"
    ```

## CLI Commands

- `github-comment`: Post a comment to a GitHub issue.
- `gitlab-comment`: Post a comment to a GitLab issue.
- `gitlab-mergerequest`: Find the most recent merge request for a given source branch.
- `vertex-code-review`: Generate a code review from a Git diff.
- `vertex-code-summary`: Generate a human-readable summary of a Git diff.
- `vertex-release-notes`: Generate release notes from a Git diff.

For detailed instructions on how to use each command, refer to the [official documentation](./docs/USAGE.md).

## Contributing

We welcome contributions! Please see the [Contributing Guide](CONTRIBUTING.md) for more details.

## Support

If you encounter any issues or have feedback, please open an issue on the [issues page](https://github.com/GoogleCloudPlatform/friendly-cicd-helper/issues).

## Disclaimer

This is not an officially supported Google product. The code in this repository is for demonstrative purposes only.
