import pathlib
import sys
import xml.etree.ElementTree as ET

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

from nested_svg.cleanup import collapse_nested_tags


def _normalize(svg_text: str) -> str:
    return ET.tostring(ET.fromstring(svg_text), encoding="unicode")


def test_collapse_merges_nested_text_attributes():
    svg_input = (
        "<svg>"
        "<text x='10' y='20'>"
        "<text fill='red' font-weight='bold'>Label</text>"
        "</text>"
        "</svg>"
    )

    expected = (
        "<svg>"
        "<text x='10' y='20' fill='red' font-weight='bold'>Label</text>"
        "</svg>"
    )

    result = collapse_nested_tags(svg_input)
    assert result == _normalize(expected)


def test_skips_when_parent_has_siblings():
    svg_input = (
        "<svg>"
        "<g id='parent'>"
        "<g id='child'></g>"
        "<circle />"
        "</g>"
        "</svg>"
    )

    result = collapse_nested_tags(svg_input)
    assert result == _normalize(svg_input)


def test_skips_when_parent_has_own_text():
    svg_input = (
        "<svg>"
        "<text data-label='outer'>Outer"
        "<text fill='red'>Inner</text>"
        "</text>"
        "</svg>"
    )

    result = collapse_nested_tags(svg_input)
    assert result == _normalize(svg_input)


def test_multi_level_collapse_preserves_text_and_tail():
    svg_input = (
        "<svg>"
        "<g id='outer'>"
        "<g class='middle'>"
        "<g data-level='inner'>"
        "Lead"
        "<tspan>Span</tspan>"
        "Trail"
        "</g>"
        "</g>"
        "</g>"
        "</svg>"
    )

    expected = (
        "<svg>"
        "<g id='outer' class='middle' data-level='inner'>"
        "Lead"
        "<tspan>Span</tspan>"
        "Trail"
        "</g>"
        "</svg>"
    )

    result = collapse_nested_tags(svg_input)
    assert result == _normalize(expected)
