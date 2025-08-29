import os
import logging
import vertexai
from typing import cast
from vertexai.generative_models import GenerativeModel, GenerationResponse
from lib.config import VERTEX_GCP_PROJECT, VERTEX_LOCATION, VERTEX_MODEL_NAME
from lib.exceptions import APIError, ConfigurationError

logger = logging.getLogger(__name__)

if not VERTEX_GCP_PROJECT:
    raise ConfigurationError("VERTEX_GCP_PROJECT environment variable not set.")

try:
    vertexai.init(project=VERTEX_GCP_PROJECT, location=VERTEX_LOCATION)
    model = GenerativeModel(VERTEX_MODEL_NAME)
except Exception as e:
    raise APIError(f"Failed to initialize Vertex AI: {e}") from e

generation_config = {
    "temperature": 0,
}

def load_diff(diff_path):
    """
    Load a Git diff from a file.
    """
    if not os.path.exists(diff_path):
        raise FileNotFoundError(f"{diff_path} does not exist")
    with open(diff_path, 'r') as file:
        data = file.read()
    return f"""

**Context: Git Diff Analysis**

The following text is a Git diff in the unified format. Here is a guide to its structure:
- Lines starting with `---` or `+++` indicate the original and new files, respectively.
- Lines starting with `@@` are "hunk headers" that specify the line numbers for the changes.
- Lines starting with a `+` character are lines that have been **added**.
- Lines starting with a `-` character are lines that have been **removed**.
- Lines starting with a space are unchanged and are included for context.
- Lines starting with an at character '@' are meta data.
- Lines starting with a caret character '^' are modified.
- Lines starting with a pound character '#' are comments.
Your analysis must be based *exclusively* on the added and removed lines within this diff.

======= START Git Diff =======
${data}
======= END Git Diff =======
    """

def code_summary(diff_path):
    """
    Generate a code summary based on a Git diff.
    """

    response = cast(GenerationResponse, model.generate_content(
        f"""
        **Persona:** You are a principal software engineer acting as a tech lead. Your goal is to provide a clear, high-level overview of a code change for your team.

**Task:** Analyze the following Git diff and create a concise summary. Focus on the "why" behind the changes, not just the "what". Distill the core purpose and impact of the modifications.

**Output Format:**
1.  A single paragraph providing a high-level summary of the change's purpose and overall approach.
2.  A bulleted list highlighting the 3-5 most significant individual changes.

**Constraints:**
- Keep the language clear and technical.
- Do not describe changes line-by-line.
- Base your summary *exclusively* on the provided diff.

${load_diff(diff_path)}

        """,
        generation_config=generation_config,
        stream=False
    ))
    print(response.text.strip())
    return response.text


def code_review(diff_path):
    """
    Generate a code review based on a Git diff.
    """

    response = cast(GenerationResponse, model.generate_content(
        f"""
**Persona:** You are a meticulous and collaborative senior software engineer performing a code review. Your goal is to provide constructive feedback to help your peers improve their code quality, maintainability, and reliability.

**Task:** Conduct a thorough code review of the following Git diff. Identify potential issues and suggest concrete improvements. Focus on logic, clarity, maintainability, potential bugs, and adherence to best practices.

**Output Format:**
1.  Start with one or two sentences of positive, encouraging feedback, if applicable.
2.  Provide a list of suggestions. For each suggestion:
    - Reference the file and approximate line number (e.g., `main.py:~42`).
    - Clearly explain the issue and your reasoning.
    - Provide a specific, actionable recommendation. If possible, include a corrected code snippet.
    - Categorize the suggestion as either **[Critical]**, **[Recommended]**, or **[Minor]**.

**Constraints:**
- All suggestions must be directly related to the code changes in the diff.
- Do not comment on simple style issues that a linter would typically catch (e.g., spacing, line length).
- Maintain a respectful and constructive tone.

${load_diff(diff_path)}

        """,
        generation_config=generation_config,
        stream=False
    ))
    print(response.text.strip())
    return response.text

def release_notes(diff_path):
    """
    Generate release notes based on a Git diff in unified format.
    """

    response = cast(GenerationResponse, model.generate_content(
        f"""
**Persona:** You are a professional technical writer preparing release notes for a software product. Your audience includes both technical and non-technical stakeholders.

**Task:** Analyze the following Git diff and generate clear, concise release notes. Focus on the user-facing or developer-facing impact of the changes, not the low-level implementation details.

**Output Format:**
- Use Markdown format.
- Group the changes into the following categories (only include categories with relevant changes):
  - ### ✨ New Features
  - ### 🛠️ Improvements
  - ### 🐛 Bug Fixes
- Each item should be a single, benefit-oriented sentence.

**Example:**
```markdown
### ✨ New Features
* Users can now export their data to a CSV file from the settings page.

### 🐛 Bug Fixes
* Fixed an issue where the application would crash when uploading an empty file.

${load_diff(diff_path)}
        """,
        generation_config=generation_config,
        stream=False
    ))
    print(response.text.strip())
    return response.text


def generate_content_from_text(prompt_text):
    """
    Generate content from a text prompt directly (not a file path).
    Used for AI-powered test suggestions and other text-based prompts.
    """
    try:
        response = cast(GenerationResponse, model.generate_content(prompt_text, generation_config=generation_config, stream=False))
        logger.info("Successfully generated content from Vertex AI.")
        return response.text.strip()
    except Exception as e:
        raise APIError(f"Error generating content from Vertex AI: {e}") from e