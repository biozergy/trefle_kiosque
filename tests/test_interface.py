import ast
from pathlib import Path


def test_parse_interface_file():
    p = Path(__file__).parent.parent / "interface_ultrasimple.py"
    assert p.exists(), f"Expected file {p} to exist"
    text = p.read_text(encoding="utf-8")
    # Ensure file is syntactically valid Python
    ast.parse(text)


def test_contains_expected_controls():
    p = Path(__file__).parent.parent / "interface_ultrasimple.py"
    text = p.read_text(encoding="utf-8")
    # basic sanity checks looking for the new controls and helpers we added
    assert "hauteur_dome" in text
    assert "choisir_script" in text
