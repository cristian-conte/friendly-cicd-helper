import click
import logging
import sys
from lib.logging_config import setup_logging
from lib.exceptions import FriendlyCICDHelperError

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

# Backwards-compatible alias matching docs: `github-comment`
@cli.command(name='github-comment')
@click.option('--repo', default=None, help='The repository to use (format: user/repo)', required=True, type=str)
@click.option('--issue', default=None, help='The issue number', required=True, type=int)
@click.option('--comment', default=None, help='The comment to post', required=False, type=str)
def github_comment_alias(repo, issue, comment):
    """
    Alias for posting a comment to a GitHub issue (matches docs usage `github-comment`).
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
@click.option('--repo', default=None, help='The repository to use (format: user/repo)', required=True, type=str)
@click.option('--sha', default=None, help='The git SHA of the commit', required=True, type=str)
@click.option('--diff', default=None, help='Path to the Git diff to scan for security issues', required=True, type=str)
def github_security_check(repo, sha, diff):
    """
    Create a GitHub check run for security scan results
    """
    import json
    from lib.security_analyzer import SecurityAnalyzer
    from lib.github_api import create_security_check_run
    
    click.echo(f"Creating GitHub security check for repo: {repo}, sha: {sha}")
    
    # Read diff content
    try:
        with open(diff, 'r') as f:
            diff_content = f.read()
        click.echo(f"Successfully read diff file: {diff} ({len(diff_content)} characters)")
    except FileNotFoundError:
        click.echo(f"Error: Diff file '{diff}' not found", err=True)
        return
    except Exception as e:
        click.echo(f"Error reading diff file: {e}", err=True)
        return
    
    # Perform security scan
    click.echo("Performing security analysis...")
    analyzer = SecurityAnalyzer()
    findings = analyzer.analyze_diff(diff_content)
    click.echo(f"Security analysis completed. Found {len(findings)} findings.")
    
    # Create GitHub check run
    click.echo("Creating GitHub check run...")
    check_run = create_security_check_run(repo, sha, findings)
    if check_run:
        click.echo(f"✅ Security check run created successfully: {check_run.html_url}")
    else:
        click.echo("❌ Failed to create security check run", err=True)

@cli.command()
@click.option('--repo', default=None, help='The repository to use (format: user/repo)', required=True, type=str)
@click.option('--sha', default=None, help='The git SHA of the commit', required=True, type=str)
@click.option('--diff', default=None, help='Path to the Git diff to analyze for test intelligence', required=True, type=str)
@click.option('--coverage-threshold', default=80, help='Minimum coverage threshold percentage', type=int)
def github_test_intelligence_check(repo, sha, diff, coverage_threshold):
    """
    Create a GitHub check run for test intelligence results
    """
    import json
    from lib.test_analyzer import TestIntelligenceAnalyzer
    from lib.github_api import create_test_intelligence_check_run
    
    click.echo(f"Creating GitHub test intelligence check for repo: {repo}, sha: {sha}")
    
    # Read diff content
    try:
        with open(diff, 'r') as f:
            diff_content = f.read()
        click.echo(f"Successfully read diff file: {diff} ({len(diff_content)} characters)")
    except FileNotFoundError:
        click.echo(f"Error: Diff file '{diff}' not found", err=True)
        return
    except Exception as e:
        click.echo(f"Error reading diff file: {e}", err=True)
        return
    
    # Perform test intelligence analysis
    click.echo("Performing test intelligence analysis...")
    analyzer = TestIntelligenceAnalyzer()
    findings = analyzer.analyze_diff(diff_content)
    click.echo(f"Test intelligence analysis completed. Found {len(findings)} findings.")
    
    # Create GitHub check run
    click.echo("Creating GitHub check run...")
    check_run = create_test_intelligence_check_run(repo, sha, findings)
    if check_run:
        click.echo(f"✅ Test intelligence check run created successfully: {check_run.html_url}")
    else:
        click.echo("❌ Failed to create test intelligence check run", err=True)
@cli.command()
@click.option('--diff', default=None, help='Path to the Git diff to scan for security vulnerabilities', required=True, type=str)
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

def sanitize_diff_content(diff, max_lines=200, max_chars=10000):
    """
    Truncate the diff and redact common secrets.
    """
    import re
    
    # Truncate to max_lines
    lines = diff.splitlines()
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines.append(f"... (truncated, showing first {max_lines} lines)")
    truncated = "\n".join(lines)
    
    # Truncate to max_chars
    if len(truncated) > max_chars:
        truncated = truncated[:max_chars] + "\n... (truncated, showing first {} characters)".format(max_chars)
    
    # Redact common secrets (simple regexes)
    patterns = [
        r'(?i)(api[_-]?key\s*[:=]\s*)[A-Za-z0-9_\-]{16,}',
        r'(?i)(secret\s*[:=]\s*)[A-Za-z0-9_\-]{8,}',
        r'(?i)(password\s*[:=]\s*)[^\s]+',
        r'(?i)(token\s*[:=]\s*)[A-Za-z0-9_\-]{8,}',
    ]
    
    redacted = truncated
    for pat in patterns:
        redacted = re.sub(pat, r'\1[REDACTED]', redacted)
    
    return redacted

@cli.command()
@click.option('--diff', default=None, help='Path to the Git diff to analyze for test intelligence', required=True, type=str)
@click.option('--format', default='json', help='Output format (json, text)', type=click.Choice(['json', 'text']))
@click.option('--output', default=None, help='Output file path (stdout if not specified)', type=str)
@click.option('--coverage-threshold', default=80, help='Minimum coverage threshold percentage', type=int)
@click.option('--generate-tests', default=False, help='Include AI-generated test suggestions', is_flag=True)
def test_intelligence(diff, format, output, coverage_threshold, generate_tests):
    """
    Analyze a Git diff for test intelligence and coverage gaps
    """
    import json
    from lib.test_analyzer import TestIntelligenceAnalyzer
    
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
    
    # Perform test intelligence analysis
    analyzer = TestIntelligenceAnalyzer()
    findings = analyzer.analyze_diff(diff_content)
    
    # Generate AI-powered test suggestions if requested
    ai_suggestions = []
    if generate_tests and diff_content.strip():
        try:
            # Deferred import to avoid requiring Vertex config when not used
            from lib.vertex_api import generate_content_from_text
            # Use Vertex AI to generate test suggestions
            sanitized_diff = sanitize_diff_content(diff_content)
            test_prompt = f"""
Analyze this code diff and provide specific test case suggestions:

{sanitized_diff}

Please provide:
1. Specific test methods with descriptive names
2. Test scenarios including edge cases
3. Mock requirements if needed
4. Test data suggestions

Focus on functions, classes, and logic that have been added or modified.
"""
            ai_response = generate_content_from_text(test_prompt)
            ai_suggestions = [ai_response] if ai_response else []
        except Exception as e:
            click.echo(f"Warning: Could not generate AI test suggestions: {e}", err=True)
    
    # Format output
    if format == 'json':
        report = analyzer.generate_report(findings)
        if ai_suggestions:
            report["ai_test_suggestions"] = ai_suggestions
        output_content = json.dumps(report, indent=2)
    else:  # text format
        output_content = _format_test_intelligence_report_text(findings, ai_suggestions, coverage_threshold)
    
    # Write output
    if output:
        with open(output, 'w') as f:
            f.write(output_content)
        click.echo(f"Test intelligence report written to {output}")
    else:
        click.echo(output_content)

@cli.command()
@click.option('--diff', default=None, help='Path to the Git diff to scan for compliance issues', required=True, type=str)
@click.option('--format', default='json', help='Output format (json, text)', type=click.Choice(['json', 'text']))
@click.option('--output', default=None, help='Output file path (stdout if not specified)', type=str)
def compliance_scan(diff, format, output):
    """
    Scan a Git diff for compliance issues
    """
    import json
    from lib.compliance_analyzer import ComplianceAnalyzer

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
    
    # Perform compliance scan
    analyzer = ComplianceAnalyzer()
    findings = analyzer.analyze_diff(diff_content)

    # Format output
    if format == 'json':
        try:
            report = analyzer.generate_report(findings)
        except Exception:
            # Fallback simple JSON if analyzer doesn't implement report
            report = {
                "findings": [f.__dict__ for f in findings],
                "summary": {"total_findings": len(findings)}
            }
        output_content = json.dumps(report, indent=2)
    else:
        output_content = _format_compliance_report_text(findings)

    # Write output
    if output:
        with open(output, 'w') as f:
            f.write(output_content)
        click.echo(f"Compliance report written to {output}")
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

def _format_test_intelligence_report_text(findings, ai_suggestions=None, coverage_threshold=80):
    """Format test intelligence report as human-readable text."""
    if not findings and not ai_suggestions:
        return f"✅ No test intelligence issues found. All code appears to have adequate test coverage above {coverage_threshold}%."
    
    output = []
    
    # Header section
    output.append("🧪 TEST INTELLIGENCE REPORT")
    output.append("=" * 50)
    
    if findings:
        # Summary section
        total_findings = len(findings)
        coverage_gaps = len([f for f in findings if f.issue_type.value == "coverage_gap"])
        test_smells = len([f for f in findings if f.issue_type.value == "test_smell"])
        missing_tests = len([f for f in findings if f.test_file_suggestion])
        
        output.append(f"Total findings: {total_findings}")
        output.append(f"Coverage gaps: {coverage_gaps} | Test smells: {test_smells} | Missing tests: {missing_tests}")
        
        # Coverage summary if available
        coverage_findings = [f for f in findings if f.coverage_percentage is not None]
        if coverage_findings:
            avg_coverage = sum(f.coverage_percentage for f in coverage_findings) / len(coverage_findings)
            output.append(f"Average coverage: {avg_coverage:.1f}%")
        
        output.append("")
        
        # Severity breakdown
        critical_count = len([f for f in findings if f.severity.value == "critical"])
        high_count = len([f for f in findings if f.severity.value == "high"])
        medium_count = len([f for f in findings if f.severity.value == "medium"])
        low_count = len([f for f in findings if f.severity.value == "low"])
        
        output.append(f"Severity: Critical: {critical_count} | High: {high_count} | Medium: {medium_count} | Low: {low_count}")
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
            
            issue_icon = {
                'coverage_gap': '📊',
                'test_smell': '🦨',
                'missing_edge_cases': '🎯',
                'poor_test_quality': '⚠️',
                'mutation_survivor': '🧬'
            }.get(finding.issue_type.value, '🔍')
            
            output.append(f"{i}. {severity_icon} {issue_icon} {finding.title}")
            output.append(f"   File: {finding.file_path}:{finding.line_number}")
            output.append(f"   Type: {finding.issue_type.value.replace('_', ' ').title()}")
            output.append(f"   Severity: {finding.severity.value.upper()}")
            output.append(f"   Confidence: {finding.confidence:.0%}")
            output.append(f"   Description: {finding.description}")
            
            if finding.coverage_percentage is not None:
                output.append(f"   Coverage: {finding.coverage_percentage:.1f}%")
            
            if finding.code_snippet:
                output.append(f"   Code: {finding.code_snippet}")
            
            output.append(f"   Recommendation: {finding.recommendation}")
            
            if finding.test_file_suggestion:
                output.append(f"   Suggested test file: {finding.test_file_suggestion}")
            
            output.append("")
    
    # AI suggestions section
    if ai_suggestions:
        output.append("🤖 AI-GENERATED TEST SUGGESTIONS")
        output.append("=" * 40)
        for suggestion in ai_suggestions:
            output.append(suggestion)
            output.append("")
    
    # Action items summary
    if findings:
        output.append("📋 ACTION ITEMS")
        output.append("=" * 20)
        
        # Unique test file suggestions
        test_files_needed = list(set(f.test_file_suggestion for f in findings if f.test_file_suggestion))
        if test_files_needed:
            output.append("Test files to create:")
            for test_file in test_files_needed:
                output.append(f"  • {test_file}")
            output.append("")
        
        # Coverage improvements needed
        coverage_issues = [f for f in findings if f.issue_type.value == "coverage_gap"]
        if coverage_issues:
            output.append("Files needing coverage improvement:")
            for finding in coverage_issues[:5]:  # Show top 5
                coverage_str = f" ({finding.coverage_percentage:.1f}%)" if finding.coverage_percentage else ""
                output.append(f"  • {finding.file_path}{coverage_str}")
            if len(coverage_issues) > 5:
                output.append(f"  ... and {len(coverage_issues) - 5} more files")
            output.append("")
        
        # Test quality improvements
        quality_issues = [f for f in findings if f.issue_type.value == "test_smell"]
        if quality_issues:
            output.append("Test quality improvements needed:")
            for finding in quality_issues[:3]:  # Show top 3
                output.append(f"  • {finding.file_path}: {finding.title}")
            if len(quality_issues) > 3:
                output.append(f"  ... and {len(quality_issues) - 3} more issues")
    
    return "\n".join(output)

def _format_compliance_report_text(findings):
    """Format compliance report as human-readable text."""
    if not findings:
        return "✅ No compliance issues found in the diff."

    output = []
    output.append("📏 COMPLIANCE SCAN REPORT")
    output.append("=" * 50)
    output.append(f"Total findings: {len(findings)}")

    # Count by severity (best effort if enum present)
    try:
        critical = len([f for f in findings if getattr(f.severity, 'value', str(getattr(f.severity, 'name', f.severity))).lower() == 'critical'])
        high = len([f for f in findings if getattr(f.severity, 'value', str(getattr(f.severity, 'name', f.severity))).lower() == 'high'])
        medium = len([f for f in findings if getattr(f.severity, 'value', str(getattr(f.severity, 'name', f.severity))).lower() == 'medium'])
        low = len([f for f in findings if getattr(f.severity, 'value', str(getattr(f.severity, 'name', f.severity))).lower() == 'low'])
        output.append(f"Critical: {critical} | High: {high} | Medium: {medium} | Low: {low}")
        output.append("")
    except Exception:
        output.append("")

    for i, finding in enumerate(findings, 1):
        output.append(f"{i}. {finding.title}")
        output.append(f"   File: {finding.file_path}:{finding.line_number}")
        sev = getattr(finding.severity, 'value', str(getattr(finding.severity, 'name', finding.severity))).upper()
        output.append(f"   Severity: {sev}")
        output.append(f"   Description: {finding.description}")
        if getattr(finding, 'code_snippet', ''):
            output.append(f"   Code: {finding.code_snippet}")
        output.append(f"   Recommendation: {finding.recommendation}")
        output.append("")

    return "\n".join(output)


if __name__ == '__main__':
    setup_logging()
    logger = logging.getLogger(__name__)
    try:
        cli()
    except FriendlyCICDHelperError as e:
        logger.error(f"A known application error occurred: {e}", exc_info=True)
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        logger.critical(f"An unexpected error occurred: {e}", exc_info=True)
        click.echo(f"An unexpected error occurred: {e}", err=True)
        sys.exit(1)
