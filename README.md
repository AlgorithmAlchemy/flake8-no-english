# flake8-non-english

[![PyPI version](https://img.shields.io/pypi/v/flake8-non-english.svg?logo=pypi&logoColor=white)](https://pypi.org/project/flake8-non-english/)
Install from **PyPI** by clicking the badge above

[![GitHub](https://img.shields.io/badge/GitHub-Repository-black?logo=github&logoColor=white)](https://github.com/AlgorithmAlchemy/flake8-non-english-comments)  
View the **source code on GitHub**

![Downloads](https://pepy.tech/badge/flake8-non-english)
![License](https://img.shields.io/pypi/l/flake8-non-english.svg)

**Flake8 plugin that enforces corporate code style by detecting and reporting any non-English text in Python source code.**  
It ensures that comments, docstrings, and string literals are written in English only, maintaining consistency across the codebase.

---

## Features

* Scans Python files for **non-English characters** in:
  * Comments (`# ...`)
  * Docstrings (`""" ... """` / `''' ... '''`)
  * String literals (`"..."` / `'...'`)
* Raises a linting error (`NL001`) when non-English text is found.
* Works seamlessly with **Flake8** and **pre-commit hooks**.
* Lightweight and dependency-minimal.

---

## Installation

```bash
pip install flake8-non-english
````

---

## Usage

Run normally via `flake8`:

```bash
flake8 /app
```

```bash
flake8 --select=NL
```

Example output:

```
/example.py:5:10: NL001 Non-English text detected in comment or string
```

---

## Example

```python
# This is a valid English comment
def hello():
    """Valid English docstring"""
    msg = "Hello world"
    return msg
```

If non-English text is introduced, it will be flagged:

```python
# Comment with non-English text  # ❌ flagged
def hello():
    """Function description with non-English text"""  # ❌ flagged
    msg = "String with non-English text"  # ❌ flagged
    return "Hello"  # ✅ OK
```

---

## Example (with pre-commit)

Add to `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/AlgorithmAlchemy/flake8-non-english-comments
    rev: v0.1.0
    hooks:
      - id: flake8
        additional_dependencies: [ flake8-non-english ]
```

Run:

```bash
pre-commit run --all-files
```

---

## Error Codes

* **NL001** — Non-English text detected in comment, docstring, or string literal.

---

## Development

Clone and install in editable mode:

```bash
git clone https://github.com/AlgorithmAlchemy/flake8-non-english-comments
cd flake8-non-english-comments
pip install -e .[dev]
pytest
```

---

## License

MIT License © 2025 [AlgorithmAlchemy](https://github.com/AlgorithmAlchemy)
