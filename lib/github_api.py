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

from github import Github, Auth

import os

def issue_comment(repo_path: str, issue_number: int, comment: str):
    """Posts a comment to a GitHub issue.

    Args:
        repo_path: The full path of the repository (e.g., 'owner/repo').
        issue_number: The number of the issue to comment on.
        comment: The content of the comment.
    """
    token = os.getenv('GITHUB_TOKEN')
    if token is None:
        print('Please set the GITHUB_TOKEN environment variable.')
        return

    auth = Auth.Token(token)
    client = Github(auth=auth)
    repo = client.get_repo(repo_path)
    issue = repo.get_issue(number=issue_number)
    issue_comment = issue.create_comment(comment)
    print(f'Posted a comment to GitHub issue. Link: {issue_comment.html_url}')

def pull_request_comment(repo_path: str, pr_number: int, comment: str):
    """Posts a comment to a GitHub pull request.

    Args:
        repo_path: The full path of the repository (e.g., 'owner/repo').
        pr_number: The number of the pull request to comment on.
        comment: The content of the comment.
    """
    token = os.getenv('GITHUB_TOKEN')
    if token is None:
        print('Please set the GITHUB_TOKEN environment variable.')
        return
    auth = Auth.Token(token)
    client = Github(auth=auth)
    repo = client.get_repo(repo_path)
    pr = repo.get_pull(number=pr_number)
    pr_comment = pr.create_issue_comment(comment)
    print(f'Posted a comment to GitHub PR. Link: {pr_comment.html_url}')

def get_latest_pull_request(repo_path: str, source_branch: str) -> int | None:
    """Finds the latest open pull request for a given source branch.

    Args:
        repo_path: The full path of the repository (e.g., 'owner/repo').
        source_branch: The name of the source branch.

    Returns:
        The pull request number if found, otherwise None.
    """
    import sys
    token = os.getenv('GITHUB_TOKEN')
    if token is None:
        print('Please set the GITHUB_TOKEN environment variable.')
        return None
    auth = Auth.Token(token)
    client = Github(auth=auth)
    repo = client.get_repo(repo_path)
    pulls = repo.get_pulls(state='open', sort='created')
    for pr in pulls:
        if pr.head.ref == source_branch:
            print(f'Latest pull request for {source_branch} is {pr.number}', file=sys.stderr)
            print(pr.number)
            return pr.number
    print(f'No pull requests found for {source_branch}', file=sys.stderr)
    return None
