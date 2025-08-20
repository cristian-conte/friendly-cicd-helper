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

import gitlab
from os import environ


def issue_comment(project_id: str, issue_id: int, comment: str):
    """
    Post a comment to a Gitlab issue
    """
    gl = gitlab.Gitlab(private_token=environ["GITLAB_TOKEN"])
    project = gl.projects.get(project_id)
    issue = project.issues.get(issue_id)
    note = issue.notes.create({"body": comment})
    print(f"Posted a comment to Gitlab issue. Link: {issue.web_url}#note_{note.id}")


def merge_request_comment(project_id: str, mr_id: int, comment: str):
    """
    Post a comment to a Gitlab merge request
    """
    gl = gitlab.Gitlab(private_token=environ["GITLAB_TOKEN"])
    project = gl.projects.get(project_id)
    merge_request = project.mergerequests.get(mr_id)
    note = merge_request.notes.create({"body": comment})
    print(
        f"Posted a comment to Gitlab MR. Link: {merge_request.web_url}#note_{note.id}"
    )


def get_latest_merge_request(project_id: str, source_branch: str):
    """
    Find the latest merge request id for a given source branch
    """
    gl = gitlab.Gitlab(private_token=environ["GITLAB_TOKEN"])
    project = gl.projects.get(project_id)
    merge_requests = project.mergerequests.list(source_branch=source_branch)
    if merge_requests:
        print(f"Latest merge request for {source_branch} is {merge_requests[0].iid}")
        return merge_requests[0].iid

    print(f"No merge requests found for {source_branch}")
    return None
