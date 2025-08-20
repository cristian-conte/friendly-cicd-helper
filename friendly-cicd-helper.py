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

import click
import sys
from typing import Optional

# --- Local Imports ---
import lib.github_api as github
import lib.gitlab_api as gitlab
import lib.vertex_api as vertex


# --- Helper Functions ---
def _read_comment_from_stdin() -> str:
    """Reads comment text from standard input."""
    click.echo("Reading comment from stdin (Ctrl+D to end)...")
    return sys.stdin.read().strip()


# --- CLI Group ---
@click.group()
def cli():
    """A friendly CLI tool for CI/CD automation with AI assistance."""
    pass


# --- GitHub Commands ---
@cli.group(name="github")
def github_group():
    """Commands for interacting with GitHub."""
    pass


@github_group.command("issue-comment")
@click.option(
    "--repo", required=True, help="The repository to use (format: owner/repo)"
)
@click.option("--issue", required=True, type=int, help="The issue number")
@click.option(
    "--comment", help="The comment to post (reads from stdin if not provided)"
)
def github_issue_comment(repo: str, issue: int, comment: Optional[str]):
    """
    This command will post a comment to a GitHub issue.
    """
    if comment is None:
        comment = _read_comment_from_stdin()
    github.issue_comment(repo, issue, comment)


@github_group.command("pr-comment")
@click.option(
    "--repo", required=True, help="The repository to use (format: owner/repo)"
)
@click.option("--pr", required=True, type=int, help="The pull request number")
@click.option(
    "--comment", help="The comment to post (reads from stdin if not provided)"
)
def github_pr_comment(repo: str, pr: int, comment: Optional[str]):
    """
    This command will post a comment to a GitHub pull request.
    """
    if comment is None:
        comment = _read_comment_from_stdin()
    github.pull_request_comment(repo, pr, comment)


@github_group.command("latest-pr")
@click.option(
    "--repo", required=True, help="The repository to use (format: owner/repo)"
)
@click.option("--source", required=True, help="The name of the source branch")
def github_latest_pr(repo: str, source: str):
    """
    Find the most recent Pull Request for a given source branch.
    """
    pr_number = github.get_latest_pull_request(repo, source)
    if pr_number:
        click.echo(pr_number)


# --- GitLab Commands ---
@cli.group(name="gitlab")
def gitlab_group():
    """Commands for interacting with GitLab."""
    pass


@gitlab_group.command("comment")
@click.option(
    "--project",
    required=True,
    help="The project to use (format: owner/repo or project ID)",
)
@click.option("--issue", type=int, help="The issue number")
@click.option("--mergerequest", type=int, help="The merge request number")
@click.option(
    "--comment", help="The comment to post (reads from stdin if not provided)"
)
def gitlab_comment(
    project: str,
    issue: Optional[int],
    mergerequest: Optional[int],
    comment: Optional[str],
):
    """
    This command will post a comment to a GitLab issue or merge request.
    """
    if not issue and not mergerequest:
        raise click.UsageError("Please specify either --issue or --mergerequest.")
    if issue and mergerequest:
        raise click.UsageError(
            "Please specify either --issue or --mergerequest, not both."
        )

    if comment is None:
        comment = _read_comment_from_stdin()

    if issue:
        gitlab.issue_comment(project, issue, comment)
    elif mergerequest:
        gitlab.merge_request_comment(project, mergerequest, comment)


@gitlab_group.command("latest-mr")
@click.option(
    "--project",
    required=True,
    help="The project to use (format: owner/repo or project ID)",
)
@click.option("--source", required=True, help="The name of the source branch")
def gitlab_latest_mr(project: str, source: str):
    """
    Find the most recent Merge Request for a given source branch.
    """
    mr_id = gitlab.get_latest_merge_request(project, source)
    if mr_id:
        click.echo(mr_id)


# --- Vertex AI Commands ---
@cli.group(name="vertex")
def vertex_group():
    """Commands for interacting with Vertex AI."""
    pass


@vertex_group.command("code-summary")
@click.option(
    "--diff",
    required=True,
    type=click.Path(exists=True),
    help="Path to the Git diff file",
)
def vertex_code_summary(diff: str):
    """
    Write a human-readable summary of a Git Diff.
    """
    vertex.code_summary(diff)


@vertex_group.command("code-review")
@click.option(
    "--diff",
    required=True,
    type=click.Path(exists=True),
    help="Path to the Git diff file",
)
def vertex_code_review(diff: str):
    """
    Provide a code review for a Git Diff.
    """
    vertex.code_review(diff)


@vertex_group.command("release-notes")
@click.option(
    "--diff",
    required=True,
    type=click.Path(exists=True),
    help="Path to the Git diff file",
)
def vertex_release_notes(diff: str):
    """
    Write release notes for a Git Diff.
    """
    vertex.release_notes(diff)


if __name__ == "__main__":
    cli()
