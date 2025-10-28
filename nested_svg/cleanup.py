"""Helpers for simplifying nested SVG markup."""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET

_XML_DECLARATION_PATTERN = re.compile(r"^\s*<\?xml[^?]*\?>", re.IGNORECASE)


def collapse_nested_tags(svg_text: str) -> str:
    """Collapse redundant nested SVG tags while preserving formatting.

    The function keeps the XML declaration (if present) and attempts to
    preserve whitespace by respecting existing ``text`` and ``tail`` values.
    """

    if not svg_text:
        return svg_text

    xml_declaration, body = _split_xml_declaration(svg_text)
    leading_ws, core = _split_leading_whitespace(body)
    if not core.strip():
        return svg_text
    try:
        root = ET.fromstring(core)
    except ET.ParseError:
        return svg_text
    _collapse_element(root)
    serialized = leading_ws + _serialize_xml(root)
    result = f"{xml_declaration}{serialized}"
    if svg_text.endswith("\n") and not result.endswith("\n"):
        result += "\n"
    return result


def _split_xml_declaration(svg_text: str) -> tuple[str, str]:
    match = _XML_DECLARATION_PATTERN.match(svg_text)
    if not match:
        return "", svg_text
    decl = match.group(0)
    rest = svg_text[match.end():]
    return decl, rest


def _split_leading_whitespace(text: str) -> tuple[str, str]:
    stripped = text.lstrip()
    prefix_length = len(text) - len(stripped)
    return text[:prefix_length], text[prefix_length:]


def _collapse_element(element: ET.Element) -> None:
    """Recursively collapse nested elements that share the same tag."""

    index = 0
    while index < len(element):
        child = element[index]
        _collapse_element(child)
        if _is_collapsible_pair(element, child):
            _merge_child_into_parent(element, child, index)
            # Do not increment index to re-evaluate the element now at this slot.
            continue
        index += 1


def _is_collapsible_pair(parent: ET.Element, child: ET.Element) -> bool:
    if parent.tag != child.tag:
        return False
    if len(parent) != 1:
        return False
    if child.tail and child.tail.strip():
        return False
    if parent.text and parent.text.strip():
        return False
    return True


def _merge_child_into_parent(parent: ET.Element, child: ET.Element, index: int) -> None:
    merged_attributes = dict(parent.attrib)
    merged_attributes.update(child.attrib)

    parent.attrib.clear()
    parent.attrib.update(merged_attributes)

    grandchildren = list(child)
    child_text = child.text or ""
    parent.remove(child)

    if grandchildren:
        if child_text.strip():
            parent.text = (parent.text or "") + child_text
        elif child_text:
            parent.text = child_text

    for offset, grandchild in enumerate(grandchildren):
        parent.insert(index + offset, grandchild)

    if not grandchildren:
        parent.text = (parent.text or "") + child_text
        if child.tail:
            parent.text = (parent.text or "") + child.tail
    else:
        if child.tail:
            last_inserted = parent[index + len(grandchildren) - 1]
            if last_inserted.tail and last_inserted.tail.strip():
                last_inserted.tail += child.tail
            else:
                last_inserted.tail = child.tail


def _serialize_xml(root: ET.Element) -> str:
    return ET.tostring(root, encoding="unicode")
