# nested

## SVG cleanup utility

This project provides a helper for removing redundant nested tags—such as
superfluous `<tspan>` wrappers—from SVG and other XML-based markup.

### Library usage

```python
from svg_cleanup import clean_nested_tags

clean_svg = clean_nested_tags(svg_text)
```

The `clean_nested_tags` function preserves existing markup while flattening
wrappers that do not affect rendering. Running it multiple times produces the
same result, making it safe to integrate into formatting pipelines.

### Command line usage

The module also exposes a small command-line tool:

```bash
python -m svg_cleanup path/to/file.svg
```

By default the cleaned SVG is written to standard output. To update files in
place, pass `--in-place`:

```bash
python -m svg_cleanup --in-place path/to/file.svg
```
