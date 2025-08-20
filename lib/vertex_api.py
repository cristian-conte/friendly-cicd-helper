import os
import sys
import vertexai
from vertexai.generative_models import GenerativeModel

if os.environ.get("VERTEX_GCP_PROJECT")==None:
    print("Please set VERTEX_GCP_PROJECT environment variable", file=sys.stderr)
    sys.exit(1)

vertex_location = "us-central1"
if os.environ.get("VERTEX_LOCATION")!=None:
    vertex_location = os.environ.get("VERTEX_LOCATION")

vertexai.init(project=os.environ.get("VERTEX_GCP_PROJECT"), location=vertex_location)

model = GenerativeModel("gemini-2.5-flash")

generation_config = {
    "temperature": 0,
}

def load_diff(diff_path):
    """
    Load a Git diff from a file.
    """
    if not os.path.exists(diff_path):
        print(f"{diff_path} does not exist", file=sys.stderr)
        sys.exit(1)
    with open(diff_path, 'r') as file:
        data = file.read()
    return f"""

A Git Diff works as follows:
- Lines starting with a space character ' ' are unchanged and included for context only.
- Lines starting with a plus character '+' are added.
- Lines starting with a minus character '-' are removed.
- Lines starting with a caret character '^' are modified.
- Lines starting with a pound character '#' are comments.
- Lines starting with an at character '@' are meta data.

When working with the Git diff, you only comment on code that has been changed, added or removed as indicated in the Git diff.

======= START Git Diff =======
${data}
======= END Git Diff =======
    """

def code_summary(diff_path):
    """
    Generate a code summary based on a Git diff.
    """

    response = model.generate_content(
        f"""
You are an experienced software engineer.

Provide a summary of the most important changes based on the following Git diff:

${load_diff(diff_path)}

        """,
        generation_config=generation_config
    )
    print(response.text.strip())
    return response.text


def code_review(diff_path):
    """
    Generate a code review based on a Git diff.
    """

    response = model.generate_content(
        f"""
You are an experienced software engineer.
You only comment on code that you found in the merge request diff.
Provide a code review with suggestions for the most important 
improvements based on the following Git diff. Ensure that suggestions are actionable,
clear and follow best practices:

${load_diff(diff_path)}

        """,
        generation_config=generation_config
    )
    print(response.text.strip())
    return response.text

def release_notes(diff_path):
    """
    Generate release notes based on a Git diff in unified format.
    """

    response = model.generate_content(
        f"""
You are an experienced tech writer.
Write short release notes in markdown bullet point format for the most important changes based on the following Git diff:

${load_diff(diff_path)}
        """,
        generation_config=generation_config
    )
    print(response.text.strip())
    return response.text
