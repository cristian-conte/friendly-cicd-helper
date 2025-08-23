#!/bin/bash

# .github/cloudbuild/run_test_intelligence.sh
# Shared script for Test Intelligence Analysis across CI/CD platforms
# Arguments: $1 = diff_path, $2 = comment_helper_command, $3 = repo_var, $4 = pr_var

set -e

if [ $# -ne 4 ]; then
    echo "Usage: $0 <diff_path> <comment_helper_command> <repo_var> <pr_var>"
    exit 1
fi

DIFF_PATH="$1"
COMMENT_HELPER_CMD="$2"
REPO_VAR="$3"
PR_VAR="$4"

# Generate test intelligence report
echo "## 🧪 Test Intelligence Analysis" | tee test-intelligence.md
echo "_Automated test analysis using coverage.py, pytest, and AI-powered insights_" | tee -a test-intelligence.md
echo "" | tee -a test-intelligence.md

# Run test intelligence analysis
friendly-cicd-helper test-intelligence --diff "$DIFF_PATH" --format text --generate-tests --coverage-threshold 80 | tee -a test-intelligence.md

# Generate JSON report for automation purposes
friendly-cicd-helper test-intelligence --diff "$DIFF_PATH" --format json --output /workspace/test-intelligence-report.json

# Post the report as a comment
cat test-intelligence.md | friendly-cicd-helper "$COMMENT_HELPER_CMD" --repo "$REPO_VAR" --pr "$PR_VAR"
