# Architectural Improvements

This document outlines suggested architectural improvements for the `friendly-cicd-helper` project.

## 1. Centralized Configuration

**Problem:** Configuration settings like API endpoints, model names, and other parameters are currently hardcoded or managed through environment variables directly in the code. This makes the application difficult to configure and maintain.

**Suggestion:** Implement `lib/config.py` to centralize all configuration settings.

**Example `lib/config.py`:**
```python
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
```

## 2. Standardized Logging

**Problem:** The application lacks a standardized logging mechanism, making it difficult to trace execution flow and debug issues. The `lib/logging_config.py` file is currently empty.

**Suggestion:** Implement a centralized logging configuration in `lib/logging_config.py` to ensure consistent, structured logging throughout the application.

**Example `lib/logging_config.py`:**
```python
import logging
import sys
from lib.config import LOG_LEVEL

def setup_logging():
    """
    Set up standardized logging for the application.
    """
    logging.basicConfig(
        level=LOG_LEVEL,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stdout,
    )

    # Suppress verbose logging from third-party libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("google").setLevel(logging.WARNING)

```

## 3. Code Refactoring (DRY Principle)

**Problem:** There is significant code duplication between `lib/security_analyzer.py` and `lib/test_analyzer.py`. Specifically, the `_extract_files_from_diff` and `_save_temp_file` methods are nearly identical.

**Suggestion:** Create a new `lib/utils.py` module to house shared utility functions.

**Proposed `lib/utils.py`:**
```python
import tempfile
import os

def extract_files_from_diff(diff_content: str) -> dict[str, str]:
    """Extract file content from git diff for analysis."""
    temp_files = {}
    current_file = None
    current_content = []
    in_file_content = False

    for line in diff_content.split('\n'):
        if line.startswith('diff --git'):
            if current_file and current_content:
                temp_files[current_file] = save_temp_file(current_file, '\n'.join(current_content))
            parts = line.split(' ')
            if len(parts) >= 4:
                current_file = parts[3][2:]  # Remove 'b/' prefix
            current_content = []
            in_file_content = False
        elif line.startswith('@@'):
            in_file_content = True
        elif in_file_content and not line.startswith('-'):
            current_content.append(line[1:] if line.startswith('+') or line.startswith(' ') else line)

    if current_file and current_content:
        temp_files[current_file] = save_temp_file(current_file, '\n'.join(current_content))

    return temp_files

def save_temp_file(file_path: str, content: str) -> str:
    """Save content to a temporary file maintaining the original file extension."""
    _, ext = os.path.splitext(file_path)
    with tempfile.NamedTemporaryFile(mode='w', suffix=ext, delete=False) as f:
        f.write(content)
        return f.name
```

## 4. Improved Error Handling

**Problem:** The error handling in the API modules (`lib/github_api.py`, `lib/gitlab_api.py`, `lib/vertex_api.py`) could be more specific and robust. Currently, it relies on generic `Exception` handling, which can obscure the root cause of failures.

**Suggestion:** Create a dedicated `lib/exceptions.py` module for custom exception classes. This will allow for more granular error handling and clearer error messages.

**Proposed `lib/exceptions.py`:**
```python
class FriendlyCICDHelperError(Exception):
    """Base exception for the application."""
    pass

class APIError(FriendlyCICDHelperError):
    """Raised for issues related to external API calls."""
    pass

class ConfigurationError(FriendlyCICDHelperError):
    """Raised for configuration-related errors."""
    pass

class AnalysisError(FriendlyCICDHelperError):
    """Raised for errors during code analysis."""
    pass