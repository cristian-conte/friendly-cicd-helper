# Friendly CI/CD Helper - Project Overview

## Purpose
`friendly-cicd-helper` is a project that uses Google Cloud Vertex AI for common CI/CD tasks. It analyzes code changes (git diffs) and generates:
- Summaries of changes to speed up code reviews
- PR/MR comments providing initial feedback
- Release notes for code changes

## Key Features
- Integrates with GitHub and GitLab APIs for commenting
- Uses Vertex AI Gemini model for code analysis
- Can be used as a standalone Python app, container image, or in Cloud Build pipelines
- Demonstrates composable CLI commands that can be piped together

## Business Value
This tool helps development teams by:
- Automating initial code review feedback
- Generating consistent release notes
- Speeding up the PR/MR review process
- Providing AI-powered insights into code changes

