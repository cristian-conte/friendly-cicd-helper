# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import sys
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig

# --- Vertex AI Initialization ---
try:
    GCP_PROJECT = os.environ["VERTEX_GCP_PROJECT"]
except KeyError:
    print("Please set the VERTEX_GCP_PROJECT environment variable", file=sys.stderr)
    sys.exit(1)

VERTEX_LOCATION = os.environ.get("VERTEX_LOCATION", "us-central1")

vertexai.init(project=GCP_PROJECT, location=VERTEX_LOCATION)

# --- Model Configuration ---
MODEL = GenerativeModel("gemini-1.5-flash")
GENERATION_CONFIG = GenerationConfig(temperature=0.2)


def load_diff(diff_path: str) -> str:
    """
    Load a Git diff from a file.
    """
    try:
        with open(diff_path, "r") as file:
            data = file.read()
    except FileNotFoundError:
        print(f"Error: Diff file not found at {diff_path}", file=sys.stderr)
        sys.exit(1)

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
{data}
======= END Git Diff =======
    """


def _generate_content(prompt: str) -> str:
    """Generic function to generate content from the model."""
    try:
        response = MODEL.generate_content(prompt, generation_config=GENERATION_CONFIG)
        return response.text.strip()
    except Exception as e:
        print(f"An error occurred during content generation: {e}", file=sys.stderr)
        return ""


def code_summary(diff_path: str) -> str:
    """
    Generate a code summary based on a Git diff.
    """
    diff_content = load_diff(diff_path)
    prompt = f"""
You are an experienced software engineer.
Provide a concise, high-level summary of the most important changes based on the following Git diff:

{diff_content}
    """
    summary = _generate_content(prompt)
    print(summary)
    return summary


def code_review(diff_path: str) -> str:
    """
    Generate a code review based on a Git diff.
    """
    diff_content = load_diff(diff_path)
    prompt = f"""
You are an experienced software engineer.
Provide a code review with actionable suggestions for the most important
improvements based on the following Git diff. Focus on clarity, best practices,
and potential issues. Only comment on code that has been changed, added, or removed.

{diff_content}
    """
    review = _generate_content(prompt)
    print(review)
    return review


def release_notes(diff_path: str) -> str:
    """
    Generate release notes based on a Git diff in unified format.
    """
    diff_content = load_diff(diff_path)
    prompt = f"""
You are an experienced technical writer.
Write short, clear release notes in markdown bullet-point format for the
most important user-facing changes based on the following Git diff:

{diff_content}
    """
    notes = _generate_content(prompt)
    print(notes)
    return notes
