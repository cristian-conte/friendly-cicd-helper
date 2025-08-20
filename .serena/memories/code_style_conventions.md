# Code Style and Conventions

## File Organization
- **Main CLI**: `friendly-cicd-helper.py` in project root
- **Libraries**: Organized in `lib/` directory by function (github_api.py, gitlab_api.py, vertex_api.py)
- **Documentation**: `docs/` directory with usage examples and demo pipelines

## Python Coding Conventions
- **Standard Python naming**: snake_case for functions and variables
- **Function docstrings**: Simple format with brief description
- **Import organization**: Standard library, then third-party, then local imports
- **Error handling**: Uses `sys.exit(1)` for critical errors with stderr output

## Code Headers
- **Copyright header**: All files include Google LLC copyright header (2023)
- **Apache 2.0 License**: Standard license header in all source files

## Environment Configuration
- **Environment variables**: Used for configuration (VERTEX_GCP_PROJECT, GITHUB_TOKEN, etc.)
- **Default values**: Sensible defaults where possible (vertex_location defaults to "us-central1")
- **Error messages**: Clear error messages to stderr when environment is misconfigured

## CLI Design
- **Click framework**: Uses Click decorators for command definition
- **Composable commands**: Designed to pipe output between commands
- **STDIN support**: Supports reading comment content from STDIN when not provided as parameter
- **Required vs optional**: Clear distinction with required=True/False in Click options

## No Formal Style Enforcement
- No linting configuration files (flake8, black, etc.) found
- No testing framework configuration
- This is typical for demo/example projects