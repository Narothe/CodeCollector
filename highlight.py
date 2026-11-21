"""Syntax highlighting of the preview text (powered by Pygments)."""

import customtkinter as ctk
from pygments import lex
from pygments.lexers import TextLexer, get_lexer_for_filename
from pygments.token import Token
from pygments.util import ClassNotFound

from config import PREVIEW_LIMIT
from exporter import format_header

# Colors per token type as (light theme, dark theme).
# Token types not listed here inherit the color of their nearest listed parent.
SYNTAX_COLORS = {
    Token.Comment: ("#6a737d", "#6a9955"),
    Token.Keyword: ("#af00db", "#c586c0"),
    Token.Keyword.Constant: ("#0000ff", "#569cd6"),
    Token.Operator.Word: ("#af00db", "#c586c0"),
    Token.Literal.String: ("#a31515", "#ce9178"),
    Token.Literal.Number: ("#098658", "#b5cea8"),
    Token.Name.Function: ("#795e26", "#dcdcaa"),
    Token.Name.Class: ("#267f99", "#4ec9b0"),
    Token.Name.Decorator: ("#795e26", "#dcdcaa"),
    Token.Name.Builtin: ("#0070c1", "#4fc1ff"),
    Token.Name.Tag: ("#800000", "#569cd6"),
    Token.Name.Attribute: ("#e50000", "#9cdcfe"),
    Token.Name.Exception: ("#267f99", "#4ec9b0"),
    Token.Operator: ("#5a5a5a", "#d4d4d4"),
    Token.Generic.Heading: ("#0070c1", "#569cd6"),
}

# Color of the file name headers and of the "truncated" note.
HEADER_COLOR = ("#0b5cad", "#6cb6ff")
HEADER_TAG = "header"


def _tag_for(token_type):
    """Returns the tag name for a token type, or None if it should stay uncolored."""
    # Walk up the token hierarchy until a colored type is found.
    while token_type not in SYNTAX_COLORS:
        if token_type is Token:
            return None
        token_type = token_type.parent

    return str(token_type)


def _lexer_for(file_name, content):
    """Picks a Pygments lexer by file name; plain text if the language is unknown."""
    try:
        return get_lexer_for_filename(str(file_name), content, stripnl=False)
    except ClassNotFound:
        return TextLexer(stripnl=False)


def _configure_tags(text_widget):
    """Registers one tk tag per color, matching the current light/dark theme."""
    index = 0 if ctk.get_appearance_mode() == "Light" else 1

    for token_type, colors in SYNTAX_COLORS.items():
        text_widget.tag_configure(str(token_type), foreground=colors[index])

    text_widget.tag_configure(HEADER_TAG, foreground=HEADER_COLOR[index])


def fill_preview(textbox, files):
    """
    Inserts the files into a CTkTextbox with syntax colors.

    The preview is truncated at PREVIEW_LIMIT characters to keep the window fast.
    """
    # The underlying tk.Text is much faster for many small inserts.
    widget = textbox._textbox
    _configure_tags(widget)

    used = 0
    truncated = False

    for relative_path, content in files:
        header = format_header(relative_path)
        widget.insert("end", header, HEADER_TAG)
        used += len(header)

        budget = PREVIEW_LIMIT - used
        if budget <= 0:
            truncated = True
            break

        # Cut the content before lexing, so huge files are not processed needlessly.
        if len(content) > budget:
            content = content[:budget]
            truncated = True

        for token_type, value in lex(content, _lexer_for(relative_path, content)):
            widget.insert("end", value, _tag_for(token_type))

        widget.insert("end", "\n\n\n")
        used += len(content) + 3

        if truncated:
            break

    if truncated:
        widget.insert(
            "end",
            "... preview truncated. Copy and Save include the full text.",
            HEADER_TAG,
        )
