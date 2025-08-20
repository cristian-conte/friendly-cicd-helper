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
    from lib.security_analyzer import SecurityAnalyzer
    
    # Read diff content
    try:
        with open(diff, 'r') as f:
            diff_content = f.read()
    except FileNotFoundError:
        click.echo(f"Error: Diff file '{diff}' not found", err=True)
        return
    except Exception as e:
        click.echo(f"Error reading diff file: {e}", err=True)
        return
    
    # Perform security scan
    analyzer = SecurityAnalyzer()
    findings = analyzer.analyze_diff(diff_content)
    
    # Format output
    if format == 'json':
        report = {
            "findings": [
                {
                    "type": finding.vulnerability_type.value,
                    "severity": finding.severity.value,
                    "confidence": finding.confidence,
                    "title": finding.title,
                    "description": finding.description,
                    "file": finding.file_path,
                    "line": finding.line_number,
                    "code": finding.code_snippet,
                    "recommendation": finding.recommendation,
                    "cwe_id": finding.cwe_id
                }
                for finding in findings
            ],
            "summary": {
                "total_findings": len(findings),
                "critical_severity": len([f for f in findings if f.severity.value == "critical"]),
                "high_severity": len([f for f in findings if f.severity.value == "high"]),
                "medium_severity": len([f for f in findings if f.severity.value == "medium"]),
                "low_severity": len([f for f in findings if f.severity.value == "low"])
            }
        }
        output_content = json.dumps(report, indent=2)
    else:  # text format
        output_content = _format_security_report_text(findings)
    
    # Write output
    if output:
        with open(output, 'w') as f:
            f.write(output_content)
        click.echo(f"Security report written to {output}")
    else:
        click.echo(output_content)

def _format_security_report_text(findings):
    """Format security report as human-readable text."""
    if not findings:
        return "✅ No security issues found in the diff."
    
    output = []
    
    # Summary section
    output.append("🔒 SECURITY SCAN REPORT")
    output.append("=" * 50)
    output.append(f"Total findings: {len(findings)}")
    
    # Count by severity
    critical_count = len([f for f in findings if f.severity.value == "critical"])
    high_count = len([f for f in findings if f.severity.value == "high"])
    medium_count = len([f for f in findings if f.severity.value == "medium"])
    low_count = len([f for f in findings if f.severity.value == "low"])
    
    output.append(f"Critical: {critical_count} | High: {high_count} | Medium: {medium_count} | Low: {low_count}")
    output.append("")
    
    # Findings section
    for i, finding in enumerate(findings, 1):
        severity_icon = {
            'critical': '🔴',
            'high': '🟠', 
            'medium': '🟡',
            'low': '🔵',
            'info': 'ℹ️'
        }.get(finding.severity.value, '❓')
        
        output.append(f"{i}. {severity_icon} {finding.title}")
        output.append(f"   File: {finding.file_path}:{finding.line_number}")
        output.append(f"   Severity: {finding.severity.value.upper()}")
        output.append(f"   Confidence: {finding.confidence:.0%}")
        output.append(f"   Description: {finding.description}")
        if finding.cwe_id:
            output.append(f"   CWE: {finding.cwe_id}")
        output.append(f"   Code: {finding.code_snippet}")
        output.append(f"   Recommendation: {finding.recommendation}")
        output.append("")
    
    return "\n".join(output)

if __name__ == '__main__':
    cli()