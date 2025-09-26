# flake8_no_english/checker.py

import ast
import tokenize
import re

NON_ENGLISH_RE = re.compile(r"[^\x00-\x7F]")

class NonEnglishChecker:
    name = "flake8-no-english"
    version = "0.2.0"

    nle_comments = True
    nle_strings = False

    def __init__(self, tree, filename="(none)"):
        self.tree = tree
        self.filename = filename

    @classmethod
    def add_options(cls, parser):
        parser.add_option(
            "--nle-comments",
            action="store_true",
            default=True,
            help="Enable non-English detection in comments (default: enabled)",
        )
        parser.add_option(
            "--nle-strings",
            action="store_true",
            default=False,
            help="Enable non-English detection in string literals (default: disabled)",
        )

    @classmethod
    def parse_options(cls, options):
        cls.nle_comments = getattr(options, "nle_comments", True)
        cls.nle_strings = getattr(options, "nle_strings", False)

    def run(self):
        if self.nle_comments:
            yield from self._check_comments()
        if self.nle_strings and self.tree:
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
