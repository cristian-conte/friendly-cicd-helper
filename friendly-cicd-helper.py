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

@click.group()
def cli():
    pass

@cli.command()
@click.option('--repo', default=None, help='The repository to use (format: user/repo)', required=True, type=str)
@click.option('--issue', default=None, help='The issue number', required=True, type=int)
@click.option('--comment', default=None, help='The comment to post', required=False, type=str)
def github_issue_comment(repo, issue, comment):
    """
    This command will post a comment to a GitHub issue.
    """
    import lib.github_api as github
    if comment is None:
        click.echo('Reading the comment from stdin. Press Ctrl+D when done.')
        std_in = click.get_text_stream('stdin')
        comment = std_in.read()

    github.issue_comment(repo, issue, comment)

# Add GitHub pull request comment command
@cli.command()
@click.option('--repo', default=None, help='The repository to use (format: user/repo)', required=True, type=str)
@click.option('--pr', default=None, help='The pull request number', required=True, type=int)
@click.option('--comment', default=None, help='The comment to post', required=False, type=str)
def github_pr_comment(repo, pr, comment):
    """
    This command will post a comment to a GitHub pull request.
    """
    import lib.github_api as github
    if comment is None:
        click.echo('Reading the comment from stdin. Press Ctrl+D when done.')
        std_in = click.get_text_stream('stdin')
        comment = std_in.read()
    github.pull_request_comment(repo, pr, comment)

# Add GitHub latest pull request command
@cli.command()
@click.option('--repo', default=None, help='The repository to use (format: user/repo)', required=True, type=str)
@click.option('--source', default=None, help='The name of the source branch of the pull request', required=True, type=str)
def github_latest_pr(repo, source):
    """
    Find the most recent Pull Request for a given source branch
    """
    import lib.github_api as github
    pr = github.get_latest_pull_request(repo, source)
    return pr

@cli.command()
@click.option('--project', default=None, help='The project to use (format: user/repo)', required=True, type=str)
@click.option('--issue', default=None, help='The issue number', required=False, type=int)
@click.option('--mergerequest', default=None, help='The merge request number', required=False, type=int)
@click.option('--comment', default=None, help='The comment to post', required=False, type=str)
def gitlab_comment(project, issue, mergerequest, comment):
    """
    This command will post a comment to a Gitlab issue.
    """

    import lib.gitlab_api as gitlab
    if comment is None:
        click.echo('Reading the comment from stdin. Press Ctrl+D when done.')
        std_in = click.get_text_stream('stdin')
        comment = std_in.read()

    if issue is not None:
        gitlab.issue_comment(project, issue, comment)
    elif mergerequest is not None:
        gitlab.merge_request_comment(project, mergerequest, comment)
    else:
        click.echo('Please specify either an issue or a merge request to comment on')

@cli.command()
@click.option('--project', default=None, help='The project to use (format: user/repo)', required=True, type=str)
@click.option('--source', default=None, help='The name of the source branch of the merge request', required=False, type=str)
def gitlab_mergerequest(project, source):
    """
    Find the most recent Merge Request for a given source branch
    """
    import lib.gitlab_api as gitlab
    mergerequest = gitlab.get_latest_merge_request(project, source)
    return mergerequest


@cli.command()
@click.option('--diff', default=None, help='Path to the Git diff to comment on', required=True, type=str)
def vertex_code_summary(diff):
    """
    Write a human-readable summary of a Git Diff
    """
    import lib.vertex_api as vertex
    return vertex.code_summary(diff)

@cli.command()
@click.option('--diff', default=None, help='Path to the Git diff to comment on', required=True, type=str)
def vertex_code_review(diff):
    """
    Review on a Git Diff
    """
    import lib.vertex_api as vertex
    return vertex.code_review(diff)

@cli.command()
@click.option('--diff', default=None, help='Path to the Git diff to comment on', required=True, type=str)
def vertex_release_notes(diff):
    """
    Write release notes for a Git Diff
    """
    import lib.vertex_api as vertex
    return vertex.release_notes(diff)

@cli.command()
@click.option('--diff', default=None, help='Path to the Git diff to scan for security issues', required=True, type=str)
@click.option('--format', default='json', help='Output format (json, text)', type=click.Choice(['json', 'text']))
@click.option('--output', default=None, help='Output file path (stdout if not specified)', type=str)
def security_scan(diff, format, output):
    """
    Scan a Git diff for security vulnerabilities
    """
    import json
    import lib.security_analyzer as security
    
    # Perform security scan
    report = security.scan_diff_file(diff)
    
    # Handle errors
    if "error" in report:
        click.echo(f"Error: {report['error']}", err=True)
        return
    
    # Format output
    if format == 'json':
        output_content = json.dumps(report, indent=2)
    else:  # text format
        output_content = _format_security_report_text(report)
    
    # Write output
    if output:
        with open(output, 'w') as f:
            f.write(output_content)
        click.echo(f"Security report written to {output}")
    else:
        click.echo(output_content)

def _format_security_report_text(report):
    """Format security report as human-readable text."""
    if not report.get('findings'):
        return "✅ No security issues found in the diff."
    
    summary = report['summary']
    output = []
    
    # Summary section
    output.append("🔒 SECURITY SCAN REPORT")
    output.append("=" * 50)
    output.append(f"Total findings: {summary['total_findings']}")
    output.append(f"Critical: {summary['critical']} | High: {summary['high']} | Medium: {summary['medium']} | Low: {summary['low']}")
    output.append("")
    
    # Findings section
    for i, finding in enumerate(report['findings'], 1):
        severity_icon = {
            'critical': '🔴',
            'high': '🟠', 
            'medium': '🟡',
            'low': '🔵',
            'info': 'ℹ️'
        }.get(finding['severity'], '❓')
        
        output.append(f"{i}. {severity_icon} {finding['title']}")
        output.append(f"   File: {finding['file_path']}:{finding['line_number']}")
        output.append(f"   Severity: {finding['severity'].upper()}")
        output.append(f"   Confidence: {finding['confidence']:.0%}")
        output.append(f"   Description: {finding['description']}")
        if finding.get('cwe_id'):
            output.append(f"   CWE: {finding['cwe_id']}")
        if finding.get('owasp_category'):
            output.append(f"   OWASP: {finding['owasp_category']}")
        output.append(f"   Code: {finding['code_snippet']}")
        output.append(f"   Recommendation: {finding['recommendation']}")
        output.append("")
    
    # Recommendations section
    if report.get('recommendations'):
        output.append("💡 RECOMMENDATIONS")
        output.append("-" * 30)
        for rec in report['recommendations']:
            output.append(f"• {rec}")
    
    return "\n".join(output)

if __name__ == '__main__':
    cli()