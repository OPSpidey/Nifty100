import ast
from pathlib import Path


def add_docstrings_to_file(path):

    source = path.read_text(encoding="utf-8")

    lines = source.splitlines()

    tree = ast.parse(source)

    inserts = []

    for node in ast.walk(tree):

        if isinstance(node, ast.FunctionDef):

            if node.name.startswith("_"):
                continue

            if ast.get_docstring(node):
                continue

            line = node.lineno

            indent = len(lines[line - 1]) - len(lines[line - 1].lstrip())

            inserts.append(
                (
                    line,
                    " " * (indent + 4)
                    + f'"""{node.name} function."""'
                )
            )

    for line, text in sorted(inserts, reverse=True):
        lines.insert(line, text)

    path.write_text(
        "\n".join(lines),
        encoding="utf-8"
    )


for file in Path("src").rglob("*.py"):
    add_docstrings_to_file(file)

print("Docstrings added.")