import pytest
import tempfile
import textwrap
import ast

from flake8_non_english_comments.checker import NonEnglishChecker


def run_checker(code: str, enable_strings: bool = False, disable_comments: bool = False):
    """Helper to run the checker on given code string."""
    with tempfile.NamedTemporaryFile("w+", suffix=".py", delete=False) as tmp:
        tmp.write(code)
        tmp.flush()
        tree = ast.parse(code, filename=tmp.name)

        checker = NonEnglishChecker(tree=tree, filename=tmp.name)
        # simulate options parsing
        checker.nl_comments = not disable_comments
        checker.nl_strings = enable_strings

        return list(checker.run())


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
        # Привет мир
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
    assert results == []  # strings check is disabled by default


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
        # Привет
        def foo():
            return "ok"
        """
    )
    results = run_checker(code, disable_comments=True)
    assert results == []  # no errors since comments check disabled
