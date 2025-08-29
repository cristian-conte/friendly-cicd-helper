import tempfile
import os

def extract_files_from_diff(diff_content: str) -> dict[str, str]:
    """Extract file content from git diff for analysis."""
    temp_files = {}
    current_file = None
    current_content = []
    in_file_content = False

    for line in diff_content.split('\n'):
        if line.startswith('diff --git'):
            if current_file and current_content:
                temp_files[current_file] = save_temp_file(current_file, '\n'.join(current_content))
            parts = line.split(' ')
            if len(parts) >= 4:
                current_file = parts[3][2:]  # Remove 'b/' prefix
            current_content = []
            in_file_content = False
        elif line.startswith('@@'):
            in_file_content = True
        elif in_file_content and not line.startswith('-'):
            current_content.append(line[1:] if line.startswith('+') or line.startswith(' ') else line)

    if current_file and current_content:
        temp_files[current_file] = save_temp_file(current_file, '\n'.join(current_content))

    return temp_files

def save_temp_file(file_path: str, content: str) -> str:
    """Save content to a temporary file maintaining the original file extension."""
    _, ext = os.path.splitext(file_path)
    with tempfile.NamedTemporaryFile(mode='w', suffix=ext, delete=False) as f:
        f.write(content)
        return f.name