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
import sys

def issue_comment(repo_path, issue_number, comment):
    """
    Post a comment to an existing GitHub issue in the specified repo.
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

def pull_request_comment(repo_path, pr_number, comment):
    """
    Post a comment to a GitHub pull request in the specified repo.
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

def get_latest_pull_request(repo_path, source_branch):
    """
    Find the latest open pull request for a given source branch.
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


def create_check_run(repo_path, head_sha, name, status, conclusion=None, title=None, summary=None, details_url=None, annotations=None):
    """
    Create a GitHub check run for better CI/CD integration.
    
    Args:
        repo_path: Repository path (owner/repo)
        head_sha: Git SHA of the commit
        name: Name of the check
        status: 'queued', 'in_progress', or 'completed'
        conclusion: 'success', 'failure', 'neutral', 'cancelled', 'skipped', 'timed_out', or 'action_required'
        title: Title of the check run
        summary: Summary markdown content
        details_url: URL for more details
        annotations: List of annotation objects
    """
    token = os.getenv('GITHUB_TOKEN')
    if token is None:
        print('Please set the GITHUB_TOKEN environment variable.')
        return None
        
    auth = Auth.Token(token)
    client = Github(auth=auth)
    repo = client.get_repo(repo_path)
    
    output = {}
    if title:
        output['title'] = title
    if summary:
        output['summary'] = summary
    if annotations:
        output['annotations'] = annotations
    
    check_run_data = {
        'name': name,
        'head_sha': head_sha,
        'status': status
    }
    
    if conclusion:
        check_run_data['conclusion'] = conclusion
    if details_url:
        check_run_data['details_url'] = details_url
    if output:
        check_run_data['output'] = output
    
    try:
        check_run = repo.create_check_run(**check_run_data)
        print(f'Created GitHub check run: {check_run.html_url}')
        return check_run
    except Exception as e:
        print(f'Failed to create check run: {e}', file=sys.stderr)
        return None


def create_security_check_run(repo_path, head_sha, findings):
    """Create a security scan check run with findings."""
    if not findings:
        return create_check_run(
            repo_path=repo_path,
            head_sha=head_sha,
            name="Security Scan",
            status="completed",
            conclusion="success",
            title="✅ No security vulnerabilities found",
            summary="Security scan completed successfully with no vulnerabilities detected."
        )
    
    # Count findings by severity
    critical_count = len([f for f in findings if f.severity.value == "critical"])
    high_count = len([f for f in findings if f.severity.value == "high"])
    medium_count = len([f for f in findings if f.severity.value == "medium"])
    low_count = len([f for f in findings if f.severity.value == "low"])
    
    # Determine conclusion based on severity
    if critical_count > 0:
        conclusion = "failure"
        title = f"🔴 {critical_count} critical security vulnerabilities found"
    elif high_count > 0:
        conclusion = "failure"
        title = f"🟠 {high_count} high-severity security vulnerabilities found"
    elif medium_count > 0:
        conclusion = "neutral"
        title = f"🟡 {medium_count} medium-severity security vulnerabilities found"
    else:
        conclusion = "success"
        title = f"🔵 {low_count} low-severity security vulnerabilities found"
    
    summary = f"""
**Security Scan Results:**
- Critical: {critical_count}
- High: {high_count}
- Medium: {medium_count}
- Low: {low_count}

**Total findings:** {len(findings)}
"""
    
    # Create annotations for findings (max 50 per check run)
    annotations = []
    for finding in findings[:50]:  # GitHub API limit
        annotations.append({
            'path': finding.file_path,
            'start_line': finding.line_number,
            'end_line': finding.line_number,
            'annotation_level': 'failure' if finding.severity.value in ['critical', 'high'] else 'warning',
            'message': f"{finding.title}: {finding.description}",
            'title': finding.title
        })
    
    return create_check_run(
        repo_path=repo_path,
        head_sha=head_sha,
        name="Security Scan",
        status="completed",
        conclusion=conclusion,
        title=title,
        summary=summary,
        annotations=annotations
    )


def create_test_intelligence_check_run(repo_path, head_sha, findings):
    """Create a test intelligence check run with findings."""
    if not findings:
        return create_check_run(
            repo_path=repo_path,
            head_sha=head_sha,
            name="Test Intelligence",
            status="completed",
            conclusion="success",
            title="✅ Test coverage analysis completed",
            summary="Test intelligence analysis completed with no issues found."
        )
    
    # Count findings by type and severity
    coverage_gaps = len([f for f in findings if f.issue_type.value == "coverage_gap"])
    test_smells = len([f for f in findings if f.issue_type.value == "test_smell"])
    missing_tests = len([f for f in findings if f.test_file_suggestion])
    
    # Calculate average coverage if available
    coverage_findings = [f for f in findings if f.coverage_percentage is not None]
    avg_coverage = sum(f.coverage_percentage for f in coverage_findings) / len(coverage_findings) if coverage_findings else None
    
    # Determine conclusion
    high_severity_count = len([f for f in findings if f.severity.value in ['critical', 'high']])
    if high_severity_count > 0:
        conclusion = "failure"
        title = f"❌ {high_severity_count} critical test issues found"
    elif coverage_gaps > 0:
        conclusion = "neutral" 
        title = f"⚠️ {coverage_gaps} coverage gaps identified"
    else:
        conclusion = "success"
        title = "✅ Test analysis completed"
    
    summary = f"""
**Test Intelligence Analysis:**
- Coverage gaps: {coverage_gaps}
- Test smells: {test_smells}
- Missing test files: {missing_tests}
"""
    
    if avg_coverage is not None:
        summary += f"\n**Average coverage:** {avg_coverage:.1f}%"
    
    # Create annotations for findings
    annotations = []
    for finding in findings[:50]:  # GitHub API limit
        level = 'failure' if finding.severity.value in ['critical', 'high'] else 'warning'
        annotations.append({
            'path': finding.file_path,
            'start_line': finding.line_number,
            'end_line': finding.line_number,
            'annotation_level': level,
            'message': f"{finding.title}: {finding.description}",
            'title': finding.title
        })
    
    return create_check_run(
        repo_path=repo_path,
        head_sha=head_sha,
        name="Test Intelligence",
        status="completed",
        conclusion=conclusion,
        title=title,
        summary=summary,
        annotations=annotations
    )
