"""Built-in file import tools for agents to read and process local files."""

import csv
import json
import os
from pathlib import Path


def read_file(file_path: str, max_length: int = 10000) -> str:
    """Read the contents of a text file and return it as a string.

    Args:
        file_path: The path to the file to read.
        max_length: The maximum number of characters to return (default=10000).
                    If max_length==-1, the full file content is returned.

    Returns:
        The contents of the file as a string.

    """
    try:
        path = Path(file_path).expanduser().resolve()
        if not path.exists():
            return f"Error: File not found: {path}"
        if not path.is_file():
            return f"Error: Path is not a file: {path}"

        content = path.read_text(encoding="utf-8")
        if max_length == -1:
            return content
        if len(content) > max_length:
            return (
                content[: max_length // 2]
                + f"\n..._Content truncated to stay below {max_length} characters_...\n"
                + content[-max_length // 2 :]
            )
        return content
    except UnicodeDecodeError:
        return f"Error: File is not a valid text file: {file_path}"
    except PermissionError:
        return f"Error: Permission denied reading file: {file_path}"
    except Exception as e:
        return f"Error reading file: {e!s}"


def list_directory(directory_path: str = ".", pattern: str = "*") -> str:
    """List the contents of a directory, optionally filtering by a glob pattern.

    Args:
        directory_path: The path to the directory to list (default: current directory).
        pattern: A glob pattern to filter entries (e.g., "*.txt", "*.csv"). Default is "*".

    Returns:
        A formatted string listing directory contents with file sizes.

    """
    try:
        path = Path(directory_path).expanduser().resolve()
        if not path.exists():
            return f"Error: Directory not found: {path}"
        if not path.is_dir():
            return f"Error: Path is not a directory: {path}"

        entries = sorted(path.glob(pattern))
        if not entries:
            return f"No entries matching '{pattern}' in {path}"

        lines = []
        for entry in entries:
            if entry.is_dir():
                lines.append(f"  [DIR]  {entry.name}/")
            else:
                size = entry.stat().st_size
                if size < 1024:
                    size_str = f"{size} B"
                elif size < 1024 * 1024:
                    size_str = f"{size / 1024:.1f} KB"
                else:
                    size_str = f"{size / (1024 * 1024):.1f} MB"
                lines.append(f"  {size_str:>10}  {entry.name}")
        return f"Contents of {path}:\n" + "\n".join(lines)
    except PermissionError:
        return f"Error: Permission denied accessing directory: {directory_path}"
    except Exception as e:
        return f"Error listing directory: {e!s}"


def read_csv(file_path: str, max_rows: int = 100) -> str:
    """Read a CSV file and return its contents as a formatted string.

    Args:
        file_path: The path to the CSV file to read.
        max_rows: The maximum number of data rows to return (default=100).

    Returns:
        The CSV contents as a formatted string with headers and rows.

    """
    try:
        path = Path(file_path).expanduser().resolve()
        if not path.exists():
            return f"Error: File not found: {path}"

        with path.open(encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = []
            for i, row in enumerate(reader):
                if i > max_rows:
                    rows.append(f"... (truncated, showing {max_rows} of remaining rows)")
                    break
                rows.append(row)

        if not rows:
            return "Error: CSV file is empty"

        header = rows[0]
        output = [" | ".join(header), " | ".join("---" for _ in header)]
        for row in rows[1:]:
            if isinstance(row, str):
                output.append(row)
            else:
                output.append(" | ".join(row))
        return "\n".join(output)
    except UnicodeDecodeError:
        return f"Error: File is not a valid text/CSV file: {file_path}"
    except Exception as e:
        return f"Error reading CSV file: {e!s}"


def read_json(file_path: str, max_length: int = 10000) -> str:
    """Read a JSON file and return its contents as a pretty-printed string.

    Args:
        file_path: The path to the JSON file to read.
        max_length: The maximum number of characters to return (default=10000).

    Returns:
        The JSON contents as a pretty-printed string.

    """
    try:
        path = Path(file_path).expanduser().resolve()
        if not path.exists():
            return f"Error: File not found: {path}"

        with path.open(encoding="utf-8") as f:
            data = json.load(f)

        output = json.dumps(data, indent=2, ensure_ascii=False)
        if max_length != -1 and len(output) > max_length:
            return (
                output[: max_length // 2]
                + f"\n..._Content truncated to stay below {max_length} characters_...\n"
                + output[-max_length // 2 :]
            )
        return output
    except json.JSONDecodeError as e:
        return f"Error: Invalid JSON in file: {e!s}"
    except Exception as e:
        return f"Error reading JSON file: {e!s}"
