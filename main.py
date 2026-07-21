from pathlib import Path

# Folders Skipped
IGNORE_DIRS = {
    ".git",
    ".idea",
    ".vscode",
    "__pycache__",
    "venv",
    ".venv",
    "node_modules",
    "dist",
    "build",
}

# Skipped files
IGNORE_FILES = {
    "project_code.txt",
}

# File extensions to include
INCLUDE_EXTENSIONS = {
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".html",
    ".css",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".md",
    ".txt",
    ".sql",
    ".xml",
    ".cs",
    ".csproj",
    ".sln",
    ".java",
    ".kt",
    ".cpp",
    ".c",
    ".h",
    ".hpp",
    ".php",
    ".go",
    ".rs",
    ".swift",
    ".dart",
}


def should_ignore(path: Path) -> bool:
    """Checks whether the file is located in the excluded directory."""
    return any(part in IGNORE_DIRS for part in path.parts)


def read_file(file: Path) -> str:
    """It tries to read the file using different encodings."""
    encodings = ["utf-8", "utf-8-sig", "cp1250", "latin-1"]

    for encoding in encodings:
        try:
            return file.read_text(encoding=encoding)
        except Exception:
            pass

    return "[The file could not be read]"


def main():
    print("=== Project Code Exporter ===\n")

    while True:
        path = input("Enter the path to the project: ").strip().strip('"')

        root = Path(path)

        if root.exists() and root.is_dir():
            break

        print("The specified path does not exist.\n")

    output_file = root / "project_code.txt"

    with output_file.open("w", encoding="utf-8") as output:

        for file in sorted(root.rglob("*")):

            if not file.is_file():
                continue

            if file.name in IGNORE_FILES:
                continue

            if should_ignore(file):
                continue

            if file.suffix.lower() not in INCLUDE_EXTENSIONS:
                continue

            relative = file.relative_to(root)

            output.write("=" * 60 + "\n")
            output.write(f"{relative}\n")
            output.write("=" * 60 + "\n\n")

            output.write(read_file(file))
            output.write("\n\n\n")

    print("\nDone!")
    print(f"The file was saved as:\n{output_file}")


if __name__ == "__main__":
    main()