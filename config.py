"""Central place for all tunable settings of the application."""

# ----------------------------
# Export settings
# ----------------------------

# Name of the generated file (also skipped when collecting, so it is never re-exported).
OUTPUT_FILE_NAME = "project_code.txt"

# Ask for confirmation when a project has more files than this.
WARNING_FILE_LIMIT = 2000

# Directories that are never exported.
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

# File names that are never exported.
IGNORE_FILES = {
    OUTPUT_FILE_NAME,
}

# Only files with these extensions are exported.
INCLUDE_EXTENSIONS = {
    ".py", ".js", ".ts", ".tsx", ".jsx",
    ".html", ".css",
    ".json", ".yaml", ".yml", ".toml",
    ".md", ".txt", ".sql", ".xml",
    ".cs", ".csproj", ".sln",
    ".java", ".kt",
    ".cpp", ".c", ".h", ".hpp",
    ".php", ".go", ".rs",
    ".swift", ".dart",
}

# ----------------------------
# UI settings
# ----------------------------

# Maximum number of characters shown in the preview.
# Copying and saving always use the full text.
PREVIEW_LIMIT = 200_000

FONT = "Segoe UI"
CODE_FONT = "Consolas"
