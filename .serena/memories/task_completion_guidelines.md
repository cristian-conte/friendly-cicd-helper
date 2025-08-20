# Task Completion Guidelines

## Testing
⚠️ **No formal testing framework** is configured in this demo project.

**Manual Testing Approach:**
- Test CLI commands manually with `--help` flag
- Test with sample git diffs from the docs/USAGE.md examples
- Verify Docker container builds and runs correctly
- Test Cloud Build pipeline with demo configurations

**Basic Manual Test Commands:**
```bash
# Test CLI help
python friendly-cicd-helper.py --help

# Test Docker build
docker build . -t friendly-cicd-helper
docker run friendly-cicd-helper --help

# Test with sample diff (create sample diff first)
git diff HEAD~1 HEAD > test.diff
python friendly-cicd-helper.py vertex-code-summary --diff test.diff
```

## Code Quality Checks
⚠️ **No linting/formatting tools** are configured.

**Manual Code Quality:**
- Follow existing code style (see code_style_conventions.md)
- Ensure proper Google copyright headers on new files
- Use clear error messages to stderr
- Test environment variable handling

## Documentation Updates
When making changes, update:
- **README.md** - For user-facing changes
- **docs/USAGE.md** - For new commands or usage patterns
- **CONTRIBUTING.md** - For contribution process changes
- **Comments/docstrings** - For code functionality

## Deployment Verification
After changes:
```bash
# Test local execution
python friendly-cicd-helper.py --help

# Test Docker build
docker build . -t friendly-cicd-helper

# Test Cloud Build (if GCP access available)
gcloud builds submit . --substitutions "_IMAGE_PATH=$IMAGE_PATH"
```

## Environment Requirements Check
Ensure required environment variables are documented:
- `VERTEX_GCP_PROJECT` (required)
- `GITHUB_TOKEN` (for GitHub operations)
- `GITLAB_TOKEN` (for GitLab operations)
- `VERTEX_LOCATION` (optional, defaults to us-central1)

## Pre-commit Checklist
- [ ] Code follows existing style conventions
- [ ] Environment variables are properly handled
- [ ] Error messages are clear and go to stderr
- [ ] Docker build succeeds
- [ ] CLI help is accurate
- [ ] Documentation is updated if needed
- [ ] Manual testing performed