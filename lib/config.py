import os

# Vertex AI Configuration
VERTEX_GCP_PROJECT = os.environ.get("VERTEX_GCP_PROJECT")
VERTEX_LOCATION = os.environ.get("VERTEX_LOCATION", "us-central1")
VERTEX_MODEL_NAME = "gemini-1.0-pro"

# GitHub Configuration
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

# GitLab Configuration
GITLAB_TOKEN = os.getenv('GITLAB_TOKEN')

# Logging Configuration
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()