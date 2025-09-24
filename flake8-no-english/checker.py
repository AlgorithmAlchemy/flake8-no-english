import ast
import tokenize
import re

# Regex for non-ASCII characters (non-English)
NON_ENGLISH_RE = re.compile(r"[^\x00-\x7F]")


class NonEnglishChecker:
    name = "flake8-non-english-comments"
    version = "0.1.0"

    def __init__(self, tree, filename="(none)"):
        self.tree = tree
        self.filename = filename

    @classmethod
    def add_options(cls, parser):
        parser.add_option(
            "--nl-comments",
            action="store_true",
            default=True,
            help="Enable non-English detection in comments (default: enabled)",
        )
        parser.add_option(
            "--nl-strings",
            action="store_true",
            default=False,
            help="Enable non-English detection in string literals (default: disabled)",
        )

    @classmethod
    def parse_options(cls, options):
        cls.nl_comments = getattr(options, "nl_comments", True)
        cls.nl_strings = getattr(options, "nl_strings", False)

    def run(self):
        if self.nl_comments:
            yield from self._check_comments()
        if self.nl_strings:
            yield from self._check_strings()

    def _check_comments(self):
        try:
            with tokenize.open(self.filename) as f:
                for tok in tokenize.generate_tokens(f.readline):
                    if tok.type == tokenize.COMMENT and NON_ENGLISH_RE.search(tok.string):
                        yield (
                            tok.start[0],
                            tok.start[1],
                            "NL001 Non-English text in comment",
                            type(self),
                        )
        except Exception:
            return

    def _check_strings(self):
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                if NON_ENGLISH_RE.search(node.value):
                    yield (
                        node.lineno,
                        node.col_offset,
                        "NL002 Non-English text in string literal",
                        type(self),
                    )
