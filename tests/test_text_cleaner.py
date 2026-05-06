import pytest
from backend.services.text_cleaner import clean_text


class TestCleanText:
    def test_removes_extra_spaces(self):
        assert clean_text("hello    world") == "hello world"

    def test_removes_extra_tabs(self):
        assert clean_text("hello\t\tworld") == "hello world"

    def test_collapses_multiple_newlines(self):
        result = clean_text("line1\n\n\nline2")
        assert "\n\n" not in result

    def test_strips_leading_and_trailing_whitespace(self):
        assert clean_text("  hello  ") == "hello"

    def test_removes_table_vertical_borders(self):
        text = "col1 │ col2 │ col3"
        result = clean_text(text)
        assert "│" not in result

    def test_removes_table_horizontal_borders(self):
        text = "─────┼─────"
        result = clean_text(text)
        assert "─" not in result
        assert "┼" not in result

    def test_removes_isolated_page_numbers(self):
        text = "end of paragraph\n42\nnext paragraph"
        result = clean_text(text)
        assert "\n42\n" not in result

    def test_preserves_meaningful_content(self):
        text = "This is important content that should be preserved."
        result = clean_text(text)
        assert "important content" in result

    def test_empty_string_returns_empty(self):
        assert clean_text("") == ""

    def test_unicode_normalization_applied(self):
        # NFKC normalization converts the fi ligature (U+FB01) to "fi"
        result = clean_text("ﬁle")
        assert result == "file"

    def test_single_newline_preserved(self):
        result = clean_text("line1\nline2")
        assert "line1" in result
        assert "line2" in result
