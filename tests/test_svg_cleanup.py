import os
import subprocess
import sys
from pathlib import Path

import pytest

from svg_cleanup import clean_nested_tags


@pytest.mark.parametrize(
    "source, expected",
    [
        (
            "<svg><text><tspan>Label</tspan></text></svg>",
            "<svg><text><tspan>Label</tspan></text></svg>",
        ),
        (
            "<svg><text><tspan><tspan>Label</tspan></tspan></text></svg>",
            "<svg><text><tspan>Label</tspan></text></svg>",
        ),
        (
            "<svg><text><tspan><tspan><tspan fill=\"red\">Hi</tspan></tspan></tspan></text></svg>",
            "<svg><text><tspan fill=\"red\">Hi</tspan></text></svg>",
        ),
        (
            "<?xml version=\"1.0\" encoding=\"UTF-8\"?><tspan><tspan>Word</tspan></tspan>",
            "<?xml version=\"1.0\" encoding=\"UTF-8\"?><tspan>Word</tspan>",
        ),
        (
            "<svg>\n  <text>\n    <tspan><tspan> Hi </tspan></tspan>\n  </text>\n</svg>\n",
            "<svg>\n  <text>\n    <tspan> Hi </tspan>\n  </text>\n</svg>\n",
        ),
    ],
)
def test_clean_nested_tags(source: str, expected: str) -> None:
    assert clean_nested_tags(source) == expected


def test_preserves_outer_with_attributes() -> None:
    source = "<svg><text><tspan class=\"keep\"><tspan>Hi</tspan></tspan></text></svg>"
    assert clean_nested_tags(source) == source


def test_preserves_when_parent_has_text() -> None:
    source = "<svg><text><tspan>prefix<tspan>Inner</tspan></tspan></text></svg>"
    assert clean_nested_tags(source) == source


def test_idempotent() -> None:
    source = "<svg><text><tspan><tspan>Word</tspan></tspan></text></svg>"
    once = clean_nested_tags(source)
    twice = clean_nested_tags(once)
    assert once == twice


def test_cli_in_place(tmp_path: Path) -> None:
    source = "<svg><text><tspan><tspan>Label</tspan></tspan></text></svg>"
    target = tmp_path / "sample.svg"
    target.write_text(source, encoding="utf-8")

    env = os.environ.copy()
    src_path = Path(__file__).resolve().parents[1] / "src"
    pythonpath = env.get("PYTHONPATH")
    env["PYTHONPATH"] = (
        f"{src_path}{os.pathsep}{pythonpath}" if pythonpath else str(src_path)
    )

    completed = subprocess.run(
        [sys.executable, "-m", "svg_cleanup", "--in-place", str(target)],
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )
    assert completed.stdout == ""
    assert target.read_text(encoding="utf-8") == "<svg><text><tspan>Label</tspan></text></svg>"


def test_cli_stdout(tmp_path: Path) -> None:
    source = "<svg><text><tspan><tspan>Label</tspan></tspan></text></svg>\n"
    target = tmp_path / "sample.svg"
    target.write_text(source, encoding="utf-8")

    env = os.environ.copy()
    src_path = Path(__file__).resolve().parents[1] / "src"
    pythonpath = env.get("PYTHONPATH")
    env["PYTHONPATH"] = (
        f"{src_path}{os.pathsep}{pythonpath}" if pythonpath else str(src_path)
    )

    completed = subprocess.run(
        [sys.executable, "-m", "svg_cleanup", str(target)],
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )
    assert completed.stdout == "<svg><text><tspan>Label</tspan></text></svg>\n"
    # File should remain untouched without --in-place
    assert target.read_text(encoding="utf-8") == source
