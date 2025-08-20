#!/bin/bash

# GitHub Project Setup Script for Friendly CI/CD Helper
# This script helps set up the GitHub project with all necessary components

set -e

echo "🚀 Setting up GitHub Project for Friendly CI/CD Helper"
echo "=================================================="

# Configuration
REPO_OWNER="cristian-conte"
REPO_NAME="friendly-cicd-helper"
PROJECT_NAME="Friendly CI/CD Helper Enhancement"

# Check if GitHub CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) is not installed. Please install it first:"
    echo "   https://cli.github.com/"
    exit 1
fi

# Check if user is authenticated
if ! gh auth status &> /dev/null; then
    echo "❌ Not authenticated with GitHub. Please run 'gh auth login' first."
    exit 1
fi

echo "✅ GitHub CLI is installed and authenticated"

# Function to create labels
create_labels() {
    echo "🏷️ Creating labels..."
    
    # Priority labels
    gh label create "priority-critical" --color "B60205" --description "Security issues, production blockers" --repo "$REPO_OWNER/$REPO_NAME" || true
    gh label create "priority-high" --color "D93F0B" --description "Important features, performance issues" --repo "$REPO_OWNER/$REPO_NAME" || true
    gh label create "priority-medium" --color "FBCA04" --description "Standard enhancements" --repo "$REPO_OWNER/$REPO_NAME" || true
    gh label create "priority-low" --color "0E8A16" --description "Nice-to-have improvements" --repo "$REPO_OWNER/$REPO_NAME" || true
    
    # Type labels
    gh label create "epic" --color "5319E7" --description "Large initiatives (3+ weeks)" --repo "$REPO_OWNER/$REPO_NAME" || true
    gh label create "feature" --color "A2EEEF" --description "New functionality" --repo "$REPO_OWNER/$REPO_NAME" || true
    gh label create "task" --color "D4C5F9" --description "Implementation tasks" --repo "$REPO_OWNER/$REPO_NAME" || true
    
    # Size labels
    gh label create "size-xs" --color "C2E0C6" --description "< 1 day" --repo "$REPO_OWNER/$REPO_NAME" || true
    gh label create "size-s" --color "7057FF" --description "1-2 days" --repo "$REPO_OWNER/$REPO_NAME" || true
    gh label create "size-m" --color "008672" --description "3-5 days" --repo "$REPO_OWNER/$REPO_NAME" || true
    gh label create "size-l" --color "D73A4A" --description "1-2 weeks" --repo "$REPO_OWNER/$REPO_NAME" || true
    gh label create "size-xl" --color "B60205" --description "2+ weeks" --repo "$REPO_OWNER/$REPO_NAME" || true
    
    # Status labels
    gh label create "blocked" --color "D73A4A" --description "Cannot proceed" --repo "$REPO_OWNER/$REPO_NAME" || true
    gh label create "in-progress" --color "0052CC" --description "Currently being worked on" --repo "$REPO_OWNER/$REPO_NAME" || true
    gh label create "ready-for-review" --color "0E8A16" --description "Awaiting review" --repo "$REPO_OWNER/$REPO_NAME" || true
    gh label create "needs-feedback" --color "FBCA04" --description "Requires input" --repo "$REPO_OWNER/$REPO_NAME" || true
    
    # Component labels
    gh label create "security" --color "B60205" --description "Security-related work" --repo "$REPO_OWNER/$REPO_NAME" || true
    gh label create "performance" --color "0052CC" --description "Performance improvements" --repo "$REPO_OWNER/$REPO_NAME" || true
    gh label create "ai-ml" --color "5319E7" --description "AI/ML functionality" --repo "$REPO_OWNER/$REPO_NAME" || true
    gh label create "github-integration" --color "0E8A16" --description "GitHub API work" --repo "$REPO_OWNER/$REPO_NAME" || true
    gh label create "cicd" --color "D93F0B" --description "CI/CD pipeline work" --repo "$REPO_OWNER/$REPO_NAME" || true
    
    echo "✅ Labels created successfully"
}

# Function to create milestones
create_milestones() {
    echo "📅 Creating milestones..."
    
    # Calculate dates (3 months from now)
    DATE_1M=$(date -d "+1 month" +%Y-%m-%d)
    DATE_2M=$(date -d "+2 months" +%Y-%m-%d)
    DATE_3M=$(date -d "+3 months" +%Y-%m-%d)
    
    gh api repos/$REPO_OWNER/$REPO_NAME/milestones \
        --method POST \
        --field title="v1.1.0 - Security Foundation" \
        --field description="Enhanced Security Analysis, GitHub Actions Integration, SARIF Output Support" \
        --field due_on="${DATE_1M}T23:59:59Z" \
        --field state="open" || true
    
    gh api repos/$REPO_OWNER/$REPO_NAME/milestones \
        --method POST \
        --field title="v1.2.0 - Intelligence Features" \
        --field description="PR Intelligence & Reviewer Assignment, Risk Assessment & Prioritization" \
        --field due_on="${DATE_2M}T23:59:59Z" \
        --field state="open" || true
    
    gh api repos/$REPO_OWNER/$REPO_NAME/milestones \
        --method POST \
        --field title="v1.3.0 - Performance & Analytics" \
        --field description="Performance Impact Analysis, Analytics Dashboard, Team Productivity Metrics" \
        --field due_on="${DATE_3M}T23:59:59Z" \
        --field state="open" || true
    
    echo "✅ Milestones created successfully"
}

# Function to enable repository features
enable_features() {
    echo "⚙️ Enabling repository features..."
    
    echo "Please manually enable the following features in your repository settings:"
    echo "1. Go to: https://github.com/$REPO_OWNER/$REPO_NAME/settings"
    echo "2. Under 'Features', enable:"
    echo "   ✅ Issues"
    echo "   ✅ Projects"
    echo "   ✅ Discussions (optional)"
    echo ""
    read -p "Press Enter when you have enabled these features..."
}

# Function to create GitHub project
create_project() {
    echo "📋 Creating GitHub Project..."
    
    echo "Please create the GitHub Project manually:"
    echo "1. Go to: https://github.com/users/$REPO_OWNER/projects"
    echo "2. Click 'New project'"
    echo "3. Choose 'Board' template"
    echo "4. Name: '$PROJECT_NAME'"
    echo "5. Add columns: Backlog, In Progress, In Review, Done"
    echo ""
    echo "Project URL will be: https://github.com/users/$REPO_OWNER/projects/[NUMBER]"
    echo ""
    read -p "Press Enter when project is created..."
}

# Main execution
main() {
    echo "Starting setup process..."
    echo ""
    
    # Enable repository features
    enable_features
    
    # Create labels
    create_labels
    
    # Create milestones
    create_milestones
    
    # Create project (manual step)
    create_project
    
    echo ""
    echo "🎉 Setup complete!"
    echo ""
    echo "Next steps:"
    echo "1. Update the project URL in .github/workflows/project-automation.yml"
    echo "2. Create epic issues using the issue templates"
    echo "3. Link issues to the GitHub project"
    echo "4. Start development!"
    echo ""
    echo "📖 See PROJECT_PLAN.md for detailed guidance"
}

# Run the main function
main
