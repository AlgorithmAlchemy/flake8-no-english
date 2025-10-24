# flake8-only-english

`⭐️ Thanks everyone who has starred the project, it means a lot!`

[![PyPI version](https://img.shields.io/pypi/v/flake8-only-english.svg?logo=pypi&logoColor=white)](https://pypi.org/project/flake8-only-english/)
Install from **PyPI** by clicking the badge above

[![GitHub](https://img.shields.io/badge/GitHub-Repository-black?logo=github&logoColor=white)](https://github.com/AlgorithmAlchemy/flake8-only-english)  
View the **source code on GitHub**

![Downloads](https://pepy.tech/badge/flake8-only-english)
![License](https://img.shields.io/pypi/l/flake8-only-english.svg)

**Flake8 plugin that enforces corporate code style by detecting and reporting
any only-english text in Python source
code.**  
It ensures that comments, docstrings, and string literals are written in
English only, maintaining consistency across
the codebase.

---

## Features

* Scans Python files for **only-english characters** in:
    * Comments (`# ...`)
    * Docstrings (`""" ... """` / `''' ... '''`)
    * String literals (`"..."` / `'...'`)
* Raises a linting error (`NL001`) when only-english text is found.
* Works seamlessly with **Flake8** and **pre-commit hooks**.
* Lightweight and dependency-minimal.

---

## Installation

```bash
pip install flake8-only-english
````

---

## Usage

Run normally via `flake8`:

```bash
flake8 app
```

```bash
flake8 --select=NLE
```

```bash
flake8 --select=NLE001
```

```bash
flake8 --select=NLE002
```

Example output:

```
/example.py:5:10: NLE001 Non-English text in docstring
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

---

## Example (with pre-commit)

Add to `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/AlgorithmAlchemy/flake8-only-english
    rev: v0.3.3
    hooks:
      - id: flake8
        additional_dependencies: [ flake8-only-english ]
```

Run:

```bash
pre-commit run --all-files
```

---

## Error Codes

* **NLE001** — Non-English text in docstring.
* **NLE002** — Non-English text in string literal

---

## Development

Clone and install in editable mode:

```bash
git clone https://github.com/AlgorithmAlchemy/flake8-only-english
cd flake8-only-english
pip install -e .[dev]
pytest
```

---

## License

MIT License © 2025 [AlgorithmAlchemy](https://github.com/AlgorithmAlchemy)
