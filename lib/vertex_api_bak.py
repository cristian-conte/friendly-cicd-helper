import os
import sys
import vertexai
from vertexai.generative_models import GenerativeModel

# --- Initialization ---
# Ensure the GCP project is set
if not os.environ.get("VERTEX_GCP_PROJECT"):
    print("Please set the VERTEX_GCP_PROJECT environment variable.", file=sys.stderr)
    sys.exit(1)

# Configure Vertex AI
vertex_location = os.environ.get("VERTEX_LOCATION", "us-central1")
vertexai.init(project=os.environ.get("VERTEX_GCP_PROJECT"), location=vertex_location)

# --- Model and Configuration ---
# It's a best practice to define the model and its configuration at the top.
# Using a specific model version like "gemini-1.5-flash-001" is recommended for stability.
model = GenerativeModel("gemini-1.5-flash-001")
generation_config = {
    "temperature": 0.0, # Set to 0.0 for deterministic, fact-based outputs
}

def load_diff(diff_path: str) -> str:
    """
    Loads a Git diff from a file and wraps it with clear instructions for the AI.
    """
    if not os.path.exists(diff_path):
        print(f"Error: The file '{diff_path}' does not exist.", file=sys.stderr)
        sys.exit(1)
    with open(diff_path, 'r') as file:
        data = file.read()
    
    # Optimized instructions for the AI on how to interpret the diff.
    return f"""
**Context: Git Diff Analysis**

The following text is a Git diff in the unified format. Here is a guide to its structure:
- Lines starting with `---` or `+++` indicate the original and new files, respectively.
- Lines starting with `@@` are "hunk headers" that specify the line numbers for the changes.
- Lines starting with a `+` character are lines that have been **added**.
- Lines starting with a `-` character are lines that have been **removed**.
- Lines starting with a space are unchanged and are included for context.

Your analysis must be based *exclusively* on the added and removed lines within this diff.

======= START Git Diff =======
{data}
======= END Git Diff =======
"""

def code_summary(diff_path: str) -> str:
    """
    Generates a high-level technical summary from a Git diff.
    """
    # Optimized Prompt for Code Summary
    prompt = f"""
**Persona:** You are a principal software engineer acting as a tech lead. Your goal is to provide a clear, high-level overview of a code change for your team.

**Task:** Analyze the following Git diff and create a concise summary. Focus on the "why" behind the changes, not just the "what". Distill the core purpose and impact of the modifications.

**Output Format:**
1.  A single paragraph providing a high-level summary of the change's purpose and overall approach.
2.  A bulleted list highlighting the 3-5 most significant individual changes.

**Constraints:**
- Keep the language clear and technical.
- Do not describe changes line-by-line.
- Base your summary *exclusively* on the provided diff.

{load_diff(diff_path)}
"""
    response = model.generate_content(prompt, generation_config=generation_config)
    print(response.text.strip())
    return response.text


def code_review(diff_path: str) -> str:
    """
    Generates a constructive code review from a Git diff.
    """
    # Optimized Prompt for Code Review
    prompt = f"""
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

{load_diff(diff_path)}
"""
    response = model.generate_content(prompt, generation_config=generation_config)
    print(response.text.strip())
    return response.text


def release_notes(diff_path: str) -> str:
    """
    Generates user-focused release notes from a Git diff.
    """
    # Optimized Prompt for Release Notes
    prompt = f"""
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