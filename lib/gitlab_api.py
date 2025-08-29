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
from gitlab.exceptions import GitlabError
import logging
from lib.config import GITLAB_TOKEN
from lib.exceptions import APIError, ConfigurationError

logger = logging.getLogger(__name__)

def issue_comment(project, issue, comment):
    """
    Post a comment to a Gitlab issue
    """
    if not GITLAB_TOKEN:
        raise ConfigurationError("GITLAB_TOKEN environment variable not set.")
    try:
        gl = gitlab.Gitlab(private_token=GITLAB_TOKEN)
        project = gl.projects.get(project)
        issue = project.issues.get(issue)
        note = issue.notes.create({'body': comment})
        logger.info(f'Posted a comment to Gitlab issue. Link: {issue.web_url}#note_{note.id}')
    except GitlabError as e:
        raise APIError(f"Failed to post comment to GitLab issue: {e}") from e

def merge_request_comment(project, mr, comment):
    """
    Post a comment to a Gitlab merge request
    """
    if not GITLAB_TOKEN:
        raise ConfigurationError("GITLAB_TOKEN environment variable not set.")
    try:
        gl = gitlab.Gitlab(private_token=GITLAB_TOKEN)
        project = gl.projects.get(project)
        merge_request = project.mergerequests.get(mr)
        note = merge_request.notes.create({'body': comment})
        logger.info(f'Posted a comment to Gitlab MR. Link: {merge_request.web_url}#note_{note.id}')
    except GitlabError as e:
        raise APIError(f"Failed to post comment to GitLab merge request: {e}") from e

def get_latest_merge_request(project, source_branch):
    """
    Find the latest merge request id for a given source branch
    """
    if not GITLAB_TOKEN:
        raise ConfigurationError("GITLAB_TOKEN environment variable not set.")
    try:
        gl = gitlab.Gitlab(private_token=GITLAB_TOKEN)
        project = gl.projects.get(project)
        merge_requests = project.mergerequests.list(source_branch=source_branch)
        if merge_requests:
            mr_list = list(merge_requests)
            if mr_list:
                first_mr = mr_list[0]
                logger.info(f'Latest merge request for {source_branch} is {first_mr.iid}')
                return first_mr.iid
        else:
            logger.info(f'No merge requests found for {source_branch}')
            return None
    except GitlabError as e:
        raise APIError(f"Failed to get latest merge request: {e}") from e
