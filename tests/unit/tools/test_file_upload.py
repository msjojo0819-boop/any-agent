import base64
import os
import tempfile

from any_agent.tools.file_upload import (
    get_file_info,
    list_uploaded_files,
    read_file,
    save_file,
    upload_file,
)


def _make_tmpdir() -> str:
    return tempfile.mkdtemp()


def test_upload_file_basic() -> None:
    tmpdir = _make_tmpdir()
    content = base64.b64encode(b"hello world").decode()
    result = upload_file("test.txt", content, upload_dir=tmpdir)
    assert os.path.isfile(result)
    with open(result, "rb") as f:
        assert f.read() == b"hello world"


def test_upload_file_invalid_base64() -> None:
    tmpdir = _make_tmpdir()
    result = upload_file("test.txt", "not-valid-base64!@#$", upload_dir=tmpdir)
    assert "Error" in result


def test_upload_file_empty_name() -> None:
    tmpdir = _make_tmpdir()
    content = base64.b64encode(b"data").decode()
    result = upload_file("", content, upload_dir=tmpdir)
    assert "Error" in result


def test_upload_file_path_traversal() -> None:
    tmpdir = _make_tmpdir()
    content = base64.b64encode(b"data").decode()
    result = upload_file("../../etc/passwd", content, upload_dir=tmpdir)
    assert os.path.dirname(result) == tmpdir


def test_save_file_basic() -> None:
    tmpdir = _make_tmpdir()
    result = save_file("notes.txt", "some notes", upload_dir=tmpdir)
    assert os.path.isfile(result)
    with open(result) as f:
        assert f.read() == "some notes"


def test_save_file_empty_name() -> None:
    tmpdir = _make_tmpdir()
    result = save_file("", "content", upload_dir=tmpdir)
    assert "Error" in result


def test_read_file_text() -> None:
    tmpdir = _make_tmpdir()
    path = os.path.join(tmpdir, "hello.txt")
    with open(path, "w") as f:
        f.write("hello")
    result = read_file(path)
    assert result == "hello"


def test_read_file_binary() -> None:
    tmpdir = _make_tmpdir()
    path = os.path.join(tmpdir, "data.bin")
    raw = bytes(range(256))
    with open(path, "wb") as f:
        f.write(raw)
    result = read_file(path)
    assert base64.b64decode(result) == raw


def test_read_file_not_found() -> None:
    result = read_file("/nonexistent/path/file.txt")
    assert "Error" in result


def test_list_uploaded_files_empty() -> None:
    tmpdir = _make_tmpdir()
    result = list_uploaded_files(upload_dir=tmpdir)
    assert "No uploaded files found" in result


def test_list_uploaded_files_with_files() -> None:
    tmpdir = _make_tmpdir()
    with open(os.path.join(tmpdir, "a.txt"), "w") as f:
        f.write("aaa")
    with open(os.path.join(tmpdir, "b.png"), "wb") as f:
        f.write(b"\x89PNG" + b"\x00" * 100)
    result = list_uploaded_files(upload_dir=tmpdir)
    assert "a.txt" in result
    assert "b.png" in result


def test_get_file_info_basic() -> None:
    tmpdir = _make_tmpdir()
    path = os.path.join(tmpdir, "info.txt")
    with open(path, "w") as f:
        f.write("test content")
    result = get_file_info(path)
    assert "info.txt" in result
    assert "text/plain" in result
    assert "12 bytes" in result


def test_get_file_info_not_found() -> None:
    result = get_file_info("/nonexistent/file.txt")
    assert "Error" in result
