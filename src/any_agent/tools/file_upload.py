import base64
import mimetypes
import os
import tempfile
from pathlib import Path

_DEFAULT_UPLOAD_DIR = os.path.join(tempfile.gettempdir(), "any_agent_uploads")

_MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024  # 50 MB


def _get_upload_dir(upload_dir: str | None = None) -> Path:
    resolved = upload_dir or os.environ.get("ANY_AGENT_UPLOAD_DIR") or _DEFAULT_UPLOAD_DIR
    directory = Path(resolved)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def upload_file(
    file_name: str, content_base64: str, upload_dir: str | None = None
) -> str:
    """Save a base64-encoded file to the upload directory.

    Args:
        file_name: The name for the saved file (e.g. "report.pdf").
        content_base64: The file content encoded as a base64 string.
        upload_dir: Optional directory to save the file to. Defaults to a temp directory or ANY_AGENT_UPLOAD_DIR env var.

    Returns:
        The absolute path of the saved file, or an error message.

    """
    try:
        file_bytes = base64.b64decode(content_base64, validate=True)
    except Exception:
        return "Error: invalid base64 content."

    if len(file_bytes) > _MAX_FILE_SIZE_BYTES:
        return f"Error: file exceeds maximum size of {_MAX_FILE_SIZE_BYTES // (1024 * 1024)} MB."

    safe_name = Path(file_name).name
    if not safe_name:
        return "Error: invalid file name."

    directory = _get_upload_dir(upload_dir)
    dest = directory / safe_name
    dest.write_bytes(file_bytes)
    return str(dest)


def save_file(file_name: str, text_content: str, upload_dir: str | None = None) -> str:
    """Save text content to a file in the upload directory.

    Args:
        file_name: The name for the saved file (e.g. "notes.txt").
        text_content: The text content to write to the file.
        upload_dir: Optional directory to save the file to. Defaults to a temp directory or ANY_AGENT_UPLOAD_DIR env var.

    Returns:
        The absolute path of the saved file, or an error message.

    """
    safe_name = Path(file_name).name
    if not safe_name:
        return "Error: invalid file name."

    directory = _get_upload_dir(upload_dir)
    dest = directory / safe_name
    dest.write_text(text_content, encoding="utf-8")
    return str(dest)


def read_file(file_path: str) -> str:
    """Read the contents of a file and return it as a string.

    Args:
        file_path: The absolute path to the file to read.

    Returns:
        The file contents as a string, or an error message.

    """
    path = Path(file_path)
    if not path.is_file():
        return f"Error: file not found at {file_path}."

    if path.stat().st_size > _MAX_FILE_SIZE_BYTES:
        return f"Error: file exceeds maximum readable size of {_MAX_FILE_SIZE_BYTES // (1024 * 1024)} MB."

    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        raw = path.read_bytes()
        return base64.b64encode(raw).decode("ascii")


def list_uploaded_files(upload_dir: str | None = None) -> str:
    """List all files in the upload directory.

    Args:
        upload_dir: Optional directory to list. Defaults to a temp directory or ANY_AGENT_UPLOAD_DIR env var.

    Returns:
        A newline-separated list of file names with sizes, or a message if the directory is empty.

    """
    directory = _get_upload_dir(upload_dir)
    files = sorted(directory.iterdir())
    if not files:
        return "No uploaded files found."

    lines = []
    for f in files:
        if f.is_file():
            size = f.stat().st_size
            mime = mimetypes.guess_type(f.name)[0] or "unknown"
            if size < 1024:
                size_str = f"{size} B"
            elif size < 1024 * 1024:
                size_str = f"{size / 1024:.1f} KB"
            else:
                size_str = f"{size / (1024 * 1024):.1f} MB"
            lines.append(f"{f.name} ({mime}, {size_str})")
    return "\n".join(lines) if lines else "No uploaded files found."


def get_file_info(file_path: str) -> str:
    """Get metadata about a file including size, type, and path.

    Args:
        file_path: The absolute path to the file.

    Returns:
        A string with file metadata, or an error message if the file is not found.

    """
    path = Path(file_path)
    if not path.is_file():
        return f"Error: file not found at {file_path}."

    stat = path.stat()
    mime = mimetypes.guess_type(path.name)[0] or "unknown"
    return (
        f"Name: {path.name}\nPath: {path}\nSize: {stat.st_size} bytes\nType: {mime}\n"
    )
