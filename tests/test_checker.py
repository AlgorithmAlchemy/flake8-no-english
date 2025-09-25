# tests/test_checker.py
import pytest
import tempfile
import textwrap
import ast
import os

from flake8_no_english.checker import NonEnglishChecker


def run_checker(code: str, enable_strings: bool = False, disable_comments: bool = False):
    """Helper to run the checker on given code string."""
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as tmp:
        tmp.write(code)
        tmp_name = tmp.name

    try:
        with open(tmp_name, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=tmp_name)

        NonEnglishChecker.nl_comments = not disable_comments
        NonEnglishChecker.nl_strings = enable_strings

        checker = NonEnglishChecker(tree=tree, filename=tmp_name)
        return list(checker.run())

    finally:
        os.remove(tmp_name)


def test_no_violations():
    code = textwrap.dedent(
        """
        # English only
        def foo():
            return "Hello"
        """
    )
    results = run_checker(code)
    assert results == []


def test_non_english_in_comment():
    code = textwrap.dedent(
        """
        # Non-English comment: Привет мир
        def foo():
            return 42
        """
    )
    results = run_checker(code)
    assert any("NL001" in r[2] for r in results)


def test_non_english_in_string_disabled_by_default():
    code = textwrap.dedent(
        '''
        def foo():
            return "привет"
        '''
    )
    results = run_checker(code)
    assert results == []


def test_non_english_in_string_enabled():
    code = textwrap.dedent(
        '''
        def foo():
            return "привет"
        '''
    )
    results = run_checker(code, enable_strings=True)
    assert any("NL002" in r[2] for r in results)


def test_disable_comment_check():
    code = textwrap.dedent(
        """
        # Non-English comment
        def foo():
            return "ok"
        """
    )
    results = run_checker(code, disable_comments=True)
    assert results == []


def test_multiple_non_english_comments():
    code = textwrap.dedent(
        """
        # Non-English comment one
        # Non-English comment two
        def foo():
            return 42
        """
    )
    results = run_checker(code)
    assert len(results) == 2


def test_empty_file():
    code = ""
    results = run_checker(code)
    assert results == []


def test_multiple_non_english_words_in_one_comment():
    code = textwrap.dedent(
        """
        # Multiple non-English words: Привет мир тест
        def foo():
            return 42
        """
    )
    results = run_checker(code)
    assert len(results) == 1
    assert "NL001" in results[0][2]


def test_multiline_comment():
    code = textwrap.dedent(
        '''
        """
        Multi-line non-English
        comment here
        """
        def foo():
            return 42
        '''
    )
    results = run_checker(code)
    assert any("NL001" in r[2] for r in results)


def test_english_comment_russian_string():
    code = textwrap.dedent(
        '''
        # This is English comment
        def foo():
            return "Привет"
        '''
    )
    results = run_checker(code, enable_strings=True)
    assert any("NL002" in r[2] for r in results)
    assert all("NL001" not in r[2] for r in results)


# Additional tests

def test_non_english_in_function_argument():
    code = textwrap.dedent(
        '''
        def foo(arg="привет"):
            return arg
        '''
    )
    results = run_checker(code, enable_strings=True)
    assert any("NL002" in r[2] for r in results)


def test_non_english_docstring():
    code = textwrap.dedent(
        '''
        def foo():
            """Non-English docstring: Привет"""
            return 42
        '''
    )
    results = run_checker(code, enable_strings=True)
    assert any("NL002" in r[2] for r in results)


def test_multiline_non_english_docstring():
    code = textwrap.dedent(
        '''
        def foo():
            """
            Multi-line
            non-English docstring here
            """
            return 42
        '''
    )
    results = run_checker(code, enable_strings=True)
    assert any("NL002" in r[2] for r in results)


def test_non_english_in_type_annotation():
    code = textwrap.dedent(
        '''
        def foo(arg: "строка"):
            return arg
        '''
    )
    results = run_checker(code, enable_strings=True)
    assert any("NL002" in r[2] for r in results)


def test_non_english_in_function_call_kwargs():
    code = textwrap.dedent(
        '''
        def foo(**kwargs):
            return kwargs

        foo(ключ="значение")
        '''
    )
    results = run_checker(code, enable_strings=True)
    assert any("NL002" in r[2] for r in results)


def test_english_only_comment_and_string():
    code = textwrap.dedent(
        '''
        # This is a comment
        def foo():
            return "Hello world"
        '''
    )
    results = run_checker(code, enable_strings=True)
    assert results == []


def test_non_english_in_fstring():
    code = textwrap.dedent(
        '''
        def foo():
            return f"Привет {42}"
        '''
    )
    results = run_checker(code, enable_strings=True)
    assert any("NL002" in r[2] for r in results)


def test_non_english_in_comment_and_string():
    code = textwrap.dedent(
        '''
        # Mixed English comment with non-English string
        def foo():
            return "мир"
        '''
    )
    results = run_checker(code, enable_strings=True)
    assert any("NL001" in r[2] for r in results)
    assert any("NL002" in r[2] for r in results)


def test_empty_comment():
    code = textwrap.dedent(
        '''
        #
        def foo():
            return "Hello"
        '''
    )
    results = run_checker(code)
    assert results == []


def test_non_english_spanish_comment():
    code = textwrap.dedent(
        '''
        # Hola mundo
        def foo():
            return 42
        '''
    )
    results = run_checker(code)
    assert any("NL001" in r[2] for r in results)


def test_string_check_disabled():
    code = textwrap.dedent(
        '''
        def foo():
            return "Привет"
        '''
    )
    results = run_checker(code, enable_strings=False)
    assert all("NL002" not in r[2] for r in results)


def test_one_line_docstring():
    code = textwrap.dedent(
        '''
        def foo():
            """Привет"""
            return 42
        '''
    )
    results = run_checker(code, enable_strings=True)
    assert any("NL002" in r[2] for r in results)


def test_unreadable_file(monkeypatch):
    def fake_open(*args, **kwargs):
        raise OSError("Cannot open file")
    monkeypatch.setattr("builtins.open", fake_open)

    code = ""
    results = run_checker(code)
    assert results == []


def test_binary_file():
    with tempfile.NamedTemporaryFile("wb", delete=False) as tmp:
        tmp.write(b"\x00\xFF\x00\xFF")
        tmp_name = tmp.name

    try:
        checker = NonEnglishChecker(tree=None, filename=tmp_name)
        results = list(checker.run())
        assert results == []
    finally:
        os.remove(tmp_name)



def test_emoji_in_comment():
    code = textwrap.dedent(
        '''
        # Hello 🌍
        def foo():
            return "Hello"
        '''
    )
    results = run_checker(code)
    assert any("NL001" in r[2] for r in results)


def test_disable_all_checks():
    code = textwrap.dedent(
        '''
        # Привет мир
        def foo():
            return "привет"
        '''
    )
    results = run_checker(code, enable_strings=False, disable_comments=True)
    assert results == []
