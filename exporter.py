"""Core logic: finding project files, reading them and building the export text."""

from pathlib import Path

from config import (
    IGNORE_DIRS,
    IGNORE_FILES,
    INCLUDE_EXTENSIONS,
    OUTPUT_FILE_NAME,
    WARNING_FILE_LIMIT,
)

# Encodings tried in order when reading a file.
ENCODINGS = ("utf-8", "utf-8-sig", "cp1250", "latin-1")


def should_ignore(relative_path: Path) -> bool:
    """True if any part of the path (relative to the project root) is an ignored directory."""
    return any(part in IGNORE_DIRS for part in relative_path.parts)


def read_file(file: Path) -> str:
    """Reads a text file, trying several encodings before giving up."""
    for encoding in ENCODINGS:
        try:
            return file.read_text(encoding=encoding)
        except (UnicodeDecodeError, OSError):
            continue

    return "[The file could not be read]"


def format_header(relative_path) -> str:
    """Header printed above every file in the export."""
    line = "=" * 60
    return f"{line}\n{relative_path}\n{line}\n\n"


def collect_files(folder):
    """Yields (relative_path, content) for every file that should be exported."""
    root = Path(folder)

    for file in sorted(root.rglob("*")):
        if not file.is_file():
            continue

        if file.name in IGNORE_FILES:
            continue

        # Check the path relative to the root, so that a project living inside
        # e.g. "C:\\build\\app" is not ignored entirely.
        if should_ignore(file.relative_to(root)):
            continue

        if file.suffix.lower() not in INCLUDE_EXTENSIONS:
            continue

        yield file.relative_to(root), read_file(file)


def files_to_text(files) -> str:
    """Joins (relative_path, content) pairs into the final export text."""
    parts = []

    for relative_path, content in files:
        parts.append(format_header(relative_path))
        parts.append(content)
        parts.append("\n\n\n")

    return "".join(parts)


def default_output_path(folder) -> Path:
    """Default location of the exported file: inside the project folder."""
    return Path(folder) / OUTPUT_FILE_NAME


def save_text(path, text: str) -> Path:
    """Writes the export text to the given file path and returns that path."""
    output_file = Path(path)
    output_file.write_text(text, encoding="utf-8")

    return output_file


def analyze_project(folder):
    """
    Quickly counts files and directories.

    Returns:
        (files_count, directories_count, limit_exceeded)
    """
    root = Path(folder)

    files = 0
    directories = 0

    for item in root.rglob("*"):
        if should_ignore(item.relative_to(root)):
            continue

        if item.is_dir():
            directories += 1

        elif item.is_file():
            files += 1

            # Stop counting once the warning limit is exceeded.
            if files > WARNING_FILE_LIMIT:
                return files, directories, True

    return files, directories, False
