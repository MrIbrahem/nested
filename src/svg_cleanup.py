"""Utilities for cleaning redundant nesting from SVG/XML content."""
from __future__ import annotations

import argparse
import re
from typing import Iterable, Optional

from xml.etree import ElementTree as ET


_REDUNDANT_TAGS = {"tspan"}
_XML_DECLARATION_RE = re.compile(r"^\s*(<\?xml[^?]*\?>)\s*")


def _is_effectively_empty(text: Optional[str]) -> bool:
    return text is None or text == "" or text.isspace()


def _local_name(tag: str) -> str:
    if "}" in tag:
        return tag.rsplit("}", 1)[1]
    return tag


def _is_redundant_wrapper(element: ET.Element) -> bool:
    if _local_name(element.tag) not in _REDUNDANT_TAGS:
        return False
    if element.attrib:
        return False
    if not _is_effectively_empty(element.text):
        return False
    if not _is_effectively_empty(element.tail):
        return False
    children = list(element)
    if len(children) != 1:
        return False
    child = children[0]
    if _local_name(child.tag) != _local_name(element.tag):
        return False
    if not _is_effectively_empty(child.tail):
        return False
    return True


def _collapse_children(element: ET.Element) -> None:
    idx = 0
    while idx < len(element):
        child = element[idx]
        _collapse_children(child)
        while _is_redundant_wrapper(child):
            grandchild = child[0]
            child.remove(grandchild)
            if child.text:
                if grandchild.text:
                    grandchild.text = child.text + grandchild.text
                else:
                    grandchild.text = child.text
            if child.tail:
                if grandchild.tail:
                    grandchild.tail = child.tail + grandchild.tail
                else:
                    grandchild.tail = child.tail
            element.remove(child)
            element.insert(idx, grandchild)
            child = grandchild
        idx += 1


def _collapse_root(root: ET.Element) -> ET.Element:
    while _is_redundant_wrapper(root):
        child = root[0]
        root.remove(child)
        root = child
    return root


def clean_nested_tags(svg_text: str) -> str:
    """Return ``svg_text`` with redundant nested tags removed."""
    if not svg_text:
        return svg_text

    decl_match = _XML_DECLARATION_RE.match(svg_text)
    declaration: Optional[str] = None
    if decl_match:
        declaration = decl_match.group(1)

    parser = ET.XMLParser()
    root = ET.fromstring(svg_text, parser=parser)
    _collapse_children(root)
    root = _collapse_root(root)
    cleaned_body = ET.tostring(root, encoding="unicode")

    pieces = []
    if declaration:
        pieces.append(declaration)
    pieces.append(cleaned_body)

    cleaned = "".join(pieces)
    if svg_text.endswith("\n") and not cleaned.endswith("\n"):
        cleaned += "\n"
    return cleaned


def _read_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def _write_file(path: str, content: str) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(content)


def main(argv: Optional[Iterable[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Remove redundant nested SVG tags.")
    parser.add_argument("paths", nargs="+", help="SVG or XML files to clean.")
    parser.add_argument(
        "--in-place",
        action="store_true",
        help="Overwrite each file with the cleaned output instead of writing to stdout.",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    for path in args.paths:
        original = _read_file(path)
        cleaned = clean_nested_tags(original)
        if args.in_place:
            _write_file(path, cleaned)
        else:
            print(cleaned, end="" if cleaned.endswith("\n") else "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
