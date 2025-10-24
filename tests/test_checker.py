# tests/test_checker.py
import ast
import os
import tempfile
import textwrap

from flake8_only_english.checker import NonEnglishChecker


def run_checker(code: str, enable_strings: bool = False,
                disable_comments: bool = False):
    """Helper to run the checker on given code string."""
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False,
                                     encoding="utf-8") as tmp:
        tmp.write(code)
        tmp_name = tmp.name

    try:
        with open(tmp_name, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=tmp_name)

        NonEnglishChecker.nle_comments = not disable_comments
        NonEnglishChecker.nle_strings = enable_strings

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
    assert any("NLE001" in r[2] for r in results)


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
    assert any("NLE002" in r[2] for r in results)


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
    assert "NLE001" in results[0][2]


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
    assert any("NLE001" in r[2] for r in results)


def test_english_comment_russian_string():
    code = textwrap.dedent(
        '''
        # This is English comment
        def foo():
            return "Привет"
        '''
    )
    results = run_checker(code, enable_strings=True)
    assert any("NLE002" in r[2] for r in results)
    assert all("NLE001" not in r[2] for r in results)


# Additional tests

def test_non_english_in_function_argument():
    code = textwrap.dedent(
        '''
        def foo(arg="привет"):
            return arg
        '''
    )
    results = run_checker(code, enable_strings=True)
    assert any("NLE002" in r[2] for r in results)


def test_non_english_docstring():
    code = textwrap.dedent(
        '''
        def foo():
            """Non-English docstring: Привет"""
            return 42
        '''
    )
    results = run_checker(code, enable_strings=True)
    assert any("NLE002" in r[2] for r in results)


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
    assert any("NLE002" in r[2] for r in results)


def test_non_english_in_type_annotation():
    code = textwrap.dedent(
        '''
        def foo(arg: "строка"):
            return arg
        '''
    )
    results = run_checker(code, enable_strings=True)
    assert any("NLE002" in r[2] for r in results)


def test_non_english_in_function_call_kwargs():
    code = textwrap.dedent(
        '''
        def foo(**kwargs):
            return kwargs

        foo(ключ="значение")
        '''
    )
    results = run_checker(code, enable_strings=True)
    assert any("NLE002" in r[2] for r in results)


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
    assert any("NLE002" in r[2] for r in results)


def test_non_english_in_comment_and_string():
    code = textwrap.dedent(
        '''
        # Mixed English comment with non-English string
        def foo():
            return "мир"
        '''
    )
    results = run_checker(code, enable_strings=True)
    assert any("NLE001" in r[2] for r in results)
    assert any("NLE002" in r[2] for r in results)


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
    assert any("NLE001" in r[2] for r in results)


def test_string_check_disabled():
    code = textwrap.dedent(
        '''
        def foo():
            return "Привет"
        '''
    )
    results = run_checker(code, enable_strings=False)
    assert all("NLE002" not in r[2] for r in results)


def test_one_line_docstring():
    code = textwrap.dedent(
        '''
        def foo():
            """Привет"""
            return 42
        '''
    )
    results = run_checker(code, enable_strings=True)
    assert any("NLE002" in r[2] for r in results)


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
    assert any("NLE001" in r[2] for r in results)


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


def test_unicode_escape_in_string():
    code = 'def foo(): return "\\u041f\\u0440\\u0438\\u0432\\u0435\\u0442"'
    results = run_checker(code, enable_strings=True)
    assert any("NLE002" in r[2] for r in results)


def test_raw_string_with_non_english():
    code = r'def foo(): return r"Привет\nмир"'
    results = run_checker(code, enable_strings=True)
    assert any("NLE002" in r[2] for r in results)


def test_fstring_only_english():
    code = 'def foo(): return f"Hello {42}"'
    results = run_checker(code, enable_strings=True)
    assert results == []


def test_non_english_with_noqa():
    code = '# Привет мир  # noqa\n'
    results = run_checker(code)
    assert results == []  # noqa должен отключать


def test_mixed_alphabet_comment():
    code = '# HelloПриветWorld\n'
    results = run_checker(code)
    assert any("NLE001" in r[2] for r in results)


def test_async_function_with_non_english_docstring():
    code = textwrap.dedent('''
        async def foo():
            """Докстрока"""
            return 42
    ''')
    results = run_checker(code, enable_strings=True)
    assert any("NLE002" in r[2] for r in results)


def test_comment_with_multiple_noqa():
    code = '# Привет мир  # noqa # noqa\n'
    results = run_checker(code)
    assert results == []


def test_string_with_noqa():
    code = 'def foo(): return "Привет"  # noqa\n'
    results = run_checker(code, enable_strings=True)
    assert results == []


def test_fstring_with_multiple_non_english_segments():
    code = 'def foo(): return f"Hello {42} Привет мир"'
    results = run_checker(code, enable_strings=True)
    assert any("NLE002" in r[2] for r in results)


def test_docstring_with_html_and_non_english():
    code = textwrap.dedent(
        '''
        def foo():
            """
            <p>Привет мир</p>
            """
            return 42
        '''
    )
    results = run_checker(code, enable_strings=True)
    assert any("NLE002" in r[2] for r in results)


def test_binary_file_with_no_code():
    with tempfile.NamedTemporaryFile("wb", delete=False) as tmp:
        tmp.write(b"\xFF\xFE\x00\x01")
        tmp_name = tmp.name

    try:
        checker = NonEnglishChecker(tree=None, filename=tmp_name)
        results = list(checker.run())
        assert results == []
    finally:
        os.remove(tmp_name)


def test_cyrillic_comment_inside_function():
    code = textwrap.dedent(
        '''
        def foo():
            # Привет внутри функции
            return 42
        '''
    )
    results = run_checker(code)
    assert any("NLE001" in r[2] for r in results)


def test_class_docstring_with_non_english():
    code = textwrap.dedent(
        '''
        class Foo:
            """Класс с docstring на русском"""
            def method(self):
                return 42
        '''
    )
    results = run_checker(code, enable_strings=True)
    assert any("NLE002" in r[2] for r in results)


def test_non_english_in_list_comprehension():
    code = textwrap.dedent(
        '''
        def foo():
            return [f"Привет {i}" for i in range(3)]
        '''
    )
    results = run_checker(code, enable_strings=True)
    assert any("NLE002" in r[2] for r in results)


def test_empty_docstring():
    code = textwrap.dedent(
        '''
        def foo():
            """ """
            return 42
        '''
    )
    results = run_checker(code, enable_strings=True)
    assert results == []


# tests/test_checker.py

def test_detection_various_non_english_languages():
    words = [
        "Привет", "こんにちは", "안녕하세요", "你好", "שלום", "مرحبا", "नमस्ते",
        "γειά", "Здраво",
        "Բարեւ", "გამარჯობა", "ሰላም", "வணக்கம்", "ನಮಸ್ಕಾರ", "ഹലോ",
        "ਸਤ ਸ੍ਰੀ ਅਕਾਲ",
        "สวัสดี", "Xin chào", "Γειά", "Добрый", "Сәлем", "Здравейте",
        "שלום עולם",
        "مرحبا بالعالم", "नमस्ते दुनिया", "γειά σου κόσμε", "Привіт світ",
        "Hej världen",
        "Grüß Gott", "Cześć świecie", "Bună ziua", "Olá mundo",
        "Sziasztok világ", "Merhaba dünya",
        "Xin chào thế giới", "Olá mundo inteiro", "Ahoj světe"
    ]

    code_lines = [f'def foo_{i}(): return "{word}"' for i, word in
                  enumerate(words, start=1)]
    code = "\n".join(code_lines)

    results = run_checker(code, enable_strings=True)

    detected_words = set()
    for result in results:
        line_no = result[0]
        if line_no - 1 < len(words):
            detected_words.add(words[line_no - 1])

    missing_words = [(i + 1, word) for i, word in enumerate(words) if
                     word not in detected_words]

    assert not missing_words, f"Missing detections for: {missing_words}"


def test_nle001_disabled():
    code = textwrap.dedent(
        '''
        # Привет мир
        def foo():
            return "ok"
        '''
    )
    NonEnglishChecker.nle001_enabled = False
    NonEnglishChecker.nle002_enabled = True
    results = run_checker(code, enable_strings=False)
    assert all("NLE001" not in r[2] for r in results)


def test_nle002_disabled():
    code = textwrap.dedent(
        '''
        # English comment
        def foo():
            return "привет"
        '''
    )
    NonEnglishChecker.nle001_enabled = True
    NonEnglishChecker.nle002_enabled = False
    results = run_checker(code, enable_strings=True)
    assert all("NLE002" not in r[2] for r in results)


def test_both_nle001_and_nle002_disabled():
    code = textwrap.dedent(
        '''
        # Привет мир
        def foo():
            return "привет"
        '''
    )
    NonEnglishChecker.nle001_enabled = False
    NonEnglishChecker.nle002_enabled = False
    results = run_checker(code, enable_strings=True)
    assert results == []


def test_both_nle_enabled_explicitly():
    code = textwrap.dedent(
        '''
        # Привет мир
        def foo():
            return "привет"
        '''
    )
    NonEnglishChecker.nle001_enabled = False
    NonEnglishChecker.nle002_enabled = False

    NonEnglishChecker.parse_options(
        type("Options", (),
             {"nle_comments": True, "nle_strings": True,
              "disable_nle001": False, "disable_nle002": False})()
    )

    results = run_checker(code, enable_strings=True)
    assert any("NLE001" in r[2] for r in results)
    assert any("NLE002" in r[2] for r in results)


def test_disable_flags_override():
    code = textwrap.dedent(
        '''
        # Привет мир
        def foo():
            return "привет"
        '''
    )
    NonEnglishChecker.nle001_enabled = True
    NonEnglishChecker.nle002_enabled = True

    NonEnglishChecker.parse_options(
        type("Options", (),
             {"nle_comments": True, "nle_strings": True,
              "disable_nle001": True, "disable_nle002": True})()
    )

    results = run_checker(code, enable_strings=True)
    assert results == []


def test_disable_flags_have_priority_over_enable():
    code = textwrap.dedent(
        '''
        # Привет мир
        def foo():
            return "привет"
        '''
    )
    NonEnglishChecker.nle001_enabled = False
    NonEnglishChecker.nle002_enabled = False

    NonEnglishChecker.parse_options(
        type("Options", (),
             {"nle_comments": True, "nle_strings": True,
              "disable_nle001": True, "disable_nle002": False})()
    )

    results = run_checker(code, enable_strings=True)
    assert all("NLE001" not in r[2] for r in results)
    assert any("NLE002" in r[2] for r in results)


def test_default_behavior():
    code = textwrap.dedent(
        '''
        # Привет мир
        def foo():
            return "привет"
        '''
    )
    NonEnglishChecker.nle001_enabled = True
    NonEnglishChecker.nle002_enabled = False
    results = run_checker(code, enable_strings=False)
    assert any("NLE001" in r[2] for r in results)
    assert all("NLE002" not in r[2] for r in results)
