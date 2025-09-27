# flake8_no_english/checker.py

import ast
import tokenize
import re

NON_ENGLISH_RE = re.compile(r"[^\x00-\x7F]")

class NonEnglishChecker:
    name = "flake8-no-english"
    version = "0.3.0"

    nle001_enabled = True
    nle002_enabled = True

    def __init__(self, tree, filename="(none)"):
        self.tree = tree
        self.filename = filename

    @classmethod
    def add_options(cls, parser):
        # Comment checks (NLE001)
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

        # String checks (NLE002)
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

        # Explicit flags to disable errors separately
        parser.add_option(
            "--disable-nle001",
            action="store_true",
            default=False,
            help="Disable NLE001 error checks (comments)."
        )
        parser.add_option(
            "--disable-nle002",
            action="store_true",
            default=False,
            help="Disable NLE002 error checks (strings)."
        )

    @classmethod
    def parse_options(cls, options):
        if getattr(options, "nle_comments", None) is not None:
            cls.nle001_enabled = options.nle_comments
        if getattr(options, "nle_strings", None) is not None:
            cls.nle002_enabled = options.nle_strings

        # Explicit disable overrides
        if getattr(options, "disable_nle001", False):
            cls.nle001_enabled = False
        if getattr(options, "disable_nle002", False):
            cls.nle002_enabled = False

    def run(self):
        if self.nle001_enabled:
            yield from self._check_comments()
        if self.nle002_enabled:
            yield from self._check_strings()

    def _check_comments(self):
        try:
            with tokenize.open(self.filename) as f:
                tokens = tokenize.generate_tokens(f.readline)
                for tok in tokens:
                    if tok.type == tokenize.COMMENT:
                        comment_text = tok.string
                        if "# noqa" in comment_text:
                            continue
                        if NON_ENGLISH_RE.search(comment_text):
                            yield (
                                tok.start[0],
                                tok.start[1],
                                "NLE001 Non-English text in comment",
                                type(self),
                            )
        except Exception:
            return

    def _check_strings(self):
        try:
            for node in ast.walk(self.tree):
                # Constant string values
                if isinstance(node, ast.Constant) and isinstance(node.value, str):
                    if "# noqa" in node.value:
                        continue
                    if NON_ENGLISH_RE.search(node.value):
                        yield (
                            node.lineno,
                            node.col_offset,
                            "NLE002 Non-English text in string literal",
                            type(self),
                        )

                # Docstrings (Expr nodes with Constant string values)
                elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
                    docstring = node.value.value
                    if isinstance(docstring, str) and NON_ENGLISH_RE.search(docstring):
                        yield (
                            node.lineno,
                            node.col_offset,
                            "NLE002 Non-English text in docstring",
                            type(self),
                        )

                # Function annotations
                elif isinstance(node, ast.arg) and node.annotation:
                    ann_value = getattr(node.annotation, "value", None)
                    if isinstance(ann_value, str) and NON_ENGLISH_RE.search(ann_value):
                        yield (
                            node.lineno,
                            node.col_offset,
                            "NLE002 Non-English text in annotation",
                            type(self),
                        )

                # Keyword arguments
                elif isinstance(node, ast.keyword):
                    if isinstance(node.arg, str) and NON_ENGLISH_RE.search(node.arg):
                        yield (
                            node.lineno,
                            node.col_offset,
                            "NLE002 Non-English text in keyword argument",
                            type(self),
                        )
        except Exception:
            return
