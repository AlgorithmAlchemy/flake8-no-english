# flake8_no_english/checker.py

import ast
import tokenize


class NonEnglishChecker:
    name = "flake8-no-english"
    version = "0.4.0"

    nle_comments = True
    nle_strings = True

    def __init__(self, tree, filename="(none)"):
        self.tree = tree
        self.filename = filename

    @classmethod
    def add_options(cls, parser):
        parser.add_option(
            "--nle-comments",
            action="store_true",
            default=None,
            help="Enable non-English detection in comments (NLE001)."
        )
        parser.add_option(
            "--no-nle-comments",
            action="store_false",
            dest="nle_comments",
            help="Disable non-English detection in comments (NLE001)."
        )
        parser.add_option(
            "--nle-strings",
            action="store_true",
            default=None,
            help="Enable non-English detection in string literals (NLE002)."
        )
        parser.add_option(
            "--no-nle-strings",
            action="store_false",
            dest="nle_strings",
            help="Disable non-English detection in string literals (NLE002)."
        )

    @classmethod
    def parse_options(cls, options):
        if options.nle_comments is not None:
            cls.nle_comments = options.nle_comments
        if options.nle_strings is not None:
            cls.nle_strings = options.nle_strings

    def run(self):
        if self.tree is None:
            return

        if self.nle_comments:
            yield from self._check_comments()

        if self.nle_strings:
            yield from self._check_strings()

    def _check_comments(self):
        with open(self.filename, "rb") as f:
            tokens = tokenize.tokenize(f.readline)
            for token in tokens:
                if token.type == tokenize.COMMENT:
                    if self._contains_non_english(token.string):
                        yield token.start[0], token.start[1], "NLE001 Non-English text in comment", type(self)

                elif token.type == tokenize.STRING:
                    # Это docstring, считаем как комментарий
                    if self._is_docstring(token):
                        if self._contains_non_english(token.string):
                            yield token.start[0], token.start[1], "NLE001 Non-English text in docstring", type(self)

    def _check_strings(self):
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Str):
                if not self._is_docstring_node(node):
                    if self._contains_non_english(node.s):
                        yield node.lineno, node.col_offset, "NLE002 Non-English text in string literal", type(self)

    def _is_docstring(self, token):
        """
        Определяет, является ли строка docstring.
        """
        # Проверяем, если это тройные кавычки
        return token.string.startswith('"""') or token.string.startswith("'''")

    def _is_docstring_node(self, node):
        """
        Проверяет, является ли ast.Str узел docstring.
        """
        parent = getattr(node, "parent", None)
        if parent and isinstance(parent, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module)):
            if parent.body and isinstance(parent.body[0], ast.Expr):
                return parent.body[0].value is node
        return False

    def _contains_non_english(self, text):
        # Реализуй логику проверки на non-English символы
        for ch in text:
            if ord(ch) > 127:  # пример: любые не-ASCII символы
                return True
        return False
