"""Render a deterministic SVG diagnostic preview from PPTX-IR."""

from html import escape
from pathlib import Path
import re
from typing import Any, Dict, Iterable, List, Sequence


LUCIDE_ICON_DIR = Path(__file__).resolve().parent / "assets" / "lucide"


def _flatten(elements: Sequence[Dict[str, Any]]) -> Iterable[Dict[str, Any]]:
    for element in elements:
        yield element
        children = element.get("children", [])
        if isinstance(children, list):
            yield from _flatten(children)


def _color(value: Any, fallback: str = "none") -> str:
    return escape(str(value if value not in (None, "") else fallback), quote=True)


def _dash(element: Dict[str, Any]) -> str:
    return {
        "dash": "8 5", "dot": "2 4", "dashDot": "8 4 2 4",
    }.get(element.get("dash"), "")


def _style(element: Dict[str, Any]) -> str:
    bits = [
        "fill:{}".format(_color(element.get("fill"))),
        "stroke:{}".format(_color(element.get("stroke"))),
        "stroke-width:{}".format(element.get("strokeWidth", 0)),
    ]
    dash = _dash(element)
    if dash:
        bits.append("stroke-dasharray:{}".format(dash))
    return ";".join(bits)


def _camel_to_kebab(value: str) -> str:
    value = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", value)
    value = re.sub(r"([A-Z])([A-Z][a-z])", r"\1-\2", value)
    value = re.sub(r"([A-Za-z])([0-9])", r"\1-\2", value)
    return value.lower()


def _svg_inner(svg: str) -> str:
    match = re.search(r"<svg\b[^>]*>(.*)</svg>", svg, flags=re.DOTALL)
    return match.group(1).strip() if match else ""


def _icon_inner(element: Dict[str, Any]) -> str:
    inline_svg = element.get("svg")
    if isinstance(inline_svg, str):
        return _svg_inner(inline_svg) or inline_svg
    if element.get("library", "").lower() == "lucide" and element.get("icon"):
        icon_path = LUCIDE_ICON_DIR / (_camel_to_kebab(str(element["icon"])) + ".svg")
        if icon_path.is_file():
            return _svg_inner(icon_path.read_text(encoding="utf-8"))
    if element.get("path"):
        return '<path d="{}"/>'.format(escape(str(element["path"]), quote=True))
    return ""


def render_svg(document: Dict[str, Any], source_label: str = "render.json") -> str:
    canvas = document["canvas"]
    width, height = canvas["width"], canvas["height"]
    elements = sorted(_flatten(document.get("elements", [])), key=lambda item: item.get("zIndex", 0))
    body: List[str] = []
    connector_marker_needed = False
    for element in elements:
        kind = element.get("type")
        element_id = escape(str(element.get("id", "")), quote=True)
        if kind in {"rect", "roundRect", "group"}:
            radius = element.get("radius", 12 if kind == "roundRect" else 0)
            body.append('<rect id="{}" x="{}" y="{}" width="{}" height="{}" rx="{}" style="{}"/>'.format(
                element_id, element["x"], element["y"], element["w"], element["h"], radius, _style(element)))
        elif kind in {"line", "connector"}:
            marker_start = ""
            marker_end = ""
            if element.get("beginArrow") not in (None, "none"):
                marker_start = ' marker-start="url(#arrow)"'
                connector_marker_needed = True
            if element.get("endArrow") not in (None, "none"):
                marker_end = ' marker-end="url(#arrow)"'
                connector_marker_needed = True
            body.append('<line id="{}" x1="{}" y1="{}" x2="{}" y2="{}" style="{}"{}{} />'.format(
                element_id, element["x1"], element["y1"], element["x2"], element["y2"], _style(element), marker_start, marker_end))
        elif kind == "text":
            anchor = {"center": "middle", "right": "end"}.get(element.get("align"), "start")
            x = element["x"] + (element["w"] / 2 if anchor == "middle" else element["w"] if anchor == "end" else 0)
            font_size = element.get("fontSize", 16)
            line_height = element.get("lineHeight", font_size * 1.25)
            lines = str(element.get("text", "")).splitlines() or [""]
            y = element["y"] + font_size
            tspans = "".join(
                '<tspan x="{}" dy="{}">{}</tspan>'.format(
                    x, 0 if index == 0 else line_height, escape(line)
                )
                for index, line in enumerate(lines)
            )
            body.append('<text id="{}" x="{}" y="{}" text-anchor="{}" font-family="{}" font-size="{}" font-weight="{}" fill="{}">{}</text>'.format(
                element_id, x, y, anchor, escape(str(element.get("fontFamily", "sans-serif")), quote=True),
                font_size, element.get("fontWeight", 400), _color(element.get("color"), "#111111"), tspans))
        elif kind == "svgIcon":
            inner = _icon_inner(element)
            if inner:
                body.append('<g id="{}" transform="translate({} {}) scale({} {})" fill="none" stroke="{}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{}</g>'.format(
                    element_id, element["x"], element["y"], element["w"] / 24,
                    element["h"] / 24, _color(element.get("fill"), "#666"), inner))
            else:
                body.append('<g id="{}"><rect x="{}" y="{}" width="{}" height="{}" rx="3" fill="{}" opacity="0.18"/><text x="{}" y="{}" text-anchor="middle" font-size="{}" fill="{}">◇</text></g>'.format(
                    element_id, element["x"], element["y"], element["w"], element["h"], _color(element.get("fill"), "#666"),
                    element["x"] + element["w"] / 2, element["y"] + element["h"] * 0.78, element["h"] * 0.75, _color(element.get("fill"), "#666")))
        elif kind == "path" and element.get("d"):
            body.append('<path id="{}" d="{}" style="{}"/>'.format(element_id, escape(str(element["d"]), quote=True), _style(element)))
        elif kind == "image":
            href = escape(str(element.get("href", "")), quote=True)
            body.append('<image id="{}" x="{}" y="{}" width="{}" height="{}" href="{}"/>'.format(
                element_id, element["x"], element["y"], element["w"], element["h"], href))
    defs = ""
    if connector_marker_needed:
        defs = '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="context-stroke"/></marker></defs>'
    return '<svg xmlns="http://www.w3.org/2000/svg" width="{}" height="{}" viewBox="0 0 {} {}" role="img" aria-label="Preview of {}"><rect width="100%" height="100%" fill="#ffffff"/>{}{}</svg>\n'.format(
        width, height, width, height, escape(source_label, quote=True), defs, "".join(body))


def write_svg(document: Dict[str, Any], output: Path, source_label: str) -> None:
    output.write_text(render_svg(document, source_label), encoding="utf-8")
