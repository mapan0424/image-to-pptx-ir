"""Dependency-free semantic validation for PPTX-IR documents."""

from dataclasses import asdict, dataclass
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


ALLOWED_TYPES = {
    "text", "rect", "roundRect", "line", "connector", "path",
    "svgIcon", "image", "group",
}
BOX_TYPES = {"text", "rect", "roundRect", "svgIcon", "image", "group"}
LINE_TYPES = {"line", "connector"}
ALLOWED_DASHES = {"solid", "dash", "dot", "dashDot"}
TEXT_REQUIRED = {
    "text", "fontFamily", "fontSize", "fontWeight", "color",
    "wrap", "fit", "margin",
}
CONNECTOR_REQUIRED = {
    "x1", "y1", "x2", "y2", "dash", "beginArrow", "endArrow",
    "direction", "semantic", "mustNotBeSegmented",
}


@dataclass(frozen=True)
class Issue:
    severity: str
    code: str
    path: str
    message: str

    def to_dict(self) -> Dict[str, str]:
        return asdict(self)


@dataclass
class ValidationResult:
    kind: str
    issues: List[Issue]

    @property
    def errors(self) -> List[Issue]:
        return [issue for issue in self.issues if issue.severity == "error"]

    @property
    def warnings(self) -> List[Issue]:
        return [issue for issue in self.issues if issue.severity == "warning"]

    @property
    def valid(self) -> bool:
        return not self.errors

    def to_dict(self) -> Dict[str, Any]:
        return {
            "kind": self.kind,
            "valid": self.valid,
            "errorCount": len(self.errors),
            "warningCount": len(self.warnings),
            "issues": [issue.to_dict() for issue in self.issues],
        }


def _issue(issues: List[Issue], severity: str, code: str, path: str, message: str) -> None:
    issues.append(Issue(severity, code, path, message))


def detect_kind(document: Any) -> str:
    if isinstance(document, dict) and "canvas" in document and "elements" in document:
        return "render"
    if isinstance(document, dict) and "regions" in document:
        return "semantic"
    return "unknown"


def validate_document(document: Any, kind: str = "auto") -> ValidationResult:
    actual_kind = detect_kind(document) if kind == "auto" else kind
    if actual_kind == "render":
        return ValidationResult(actual_kind, _validate_render(document))
    if actual_kind == "semantic":
        return ValidationResult(actual_kind, _validate_semantic(document))
    return ValidationResult("unknown", [Issue(
        "error", "unknown-document", "$",
        "Cannot detect document kind; expected semantic regions or render canvas/elements.",
    )])


def _validate_semantic(document: Any) -> List[Issue]:
    issues: List[Issue] = []
    if not isinstance(document, dict):
        return [Issue("error", "invalid-root", "$", "Document root must be an object.")]
    if not isinstance(document.get("title"), str) or not document.get("title", "").strip():
        _issue(issues, "error", "missing-title", "$.title", "A non-empty title is required.")
    regions = document.get("regions")
    if not isinstance(regions, list) or not regions:
        _issue(issues, "error", "missing-regions", "$.regions", "At least one semantic region is required.")
        return issues
    seen = set()
    for index, region in enumerate(regions):
        path = "$.regions[{}]".format(index)
        if not isinstance(region, dict):
            _issue(issues, "error", "invalid-region", path, "Region must be an object.")
            continue
        for field in ("id", "name", "description"):
            if not isinstance(region.get(field), str) or not region.get(field, "").strip():
                _issue(issues, "error", "missing-region-field", path + "." + field, "A non-empty string is required.")
        region_id = region.get("id")
        if region_id in seen:
            _issue(issues, "error", "duplicate-region-id", path + ".id", "Region id must be unique.")
        if region_id:
            seen.add(region_id)
    return issues


def _flatten_elements(elements: Sequence[Any], prefix: str = "$.elements") -> Iterable[Tuple[Any, str]]:
    for index, element in enumerate(elements):
        path = "{}[{}]".format(prefix, index)
        yield element, path
        if isinstance(element, dict) and isinstance(element.get("children"), list):
            for child in _flatten_elements(element["children"], path + ".children"):
                yield child


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _has_box(element: Dict[str, Any]) -> bool:
    return all(_is_number(element.get(field)) for field in ("x", "y", "w", "h"))


def _has_line(element: Dict[str, Any]) -> bool:
    return all(_is_number(element.get(field)) for field in ("x1", "y1", "x2", "y2"))


def _validate_render(document: Any) -> List[Issue]:
    issues: List[Issue] = []
    if not isinstance(document, dict):
        return [Issue("error", "invalid-root", "$", "Document root must be an object.")]
    canvas = document.get("canvas")
    if not isinstance(canvas, dict):
        _issue(issues, "error", "missing-canvas", "$.canvas", "Canvas object is required.")
    else:
        for field in ("width", "height"):
            if not _is_number(canvas.get(field)) or canvas[field] <= 0:
                _issue(issues, "error", "invalid-canvas-size", "$.canvas." + field, "Canvas dimension must be positive.")
        if canvas.get("unit") != "px":
            _issue(issues, "error", "invalid-canvas-unit", "$.canvas.unit", "Canvas unit must be 'px'.")

    elements = document.get("elements")
    if not isinstance(elements, list):
        _issue(issues, "error", "missing-elements", "$.elements", "Elements must be an array.")
        return issues
    if not isinstance(document.get("layerRules"), dict):
        _issue(issues, "error", "missing-layer-rules", "$.layerRules", "Layer rules object is required.")
    if not isinstance(document.get("validationRules"), list):
        _issue(issues, "error", "missing-validation-rules", "$.validationRules", "Validation rules array is required.")

    flattened = list(_flatten_elements(elements))
    ids: Dict[str, str] = {}
    by_id: Dict[str, Dict[str, Any]] = {}
    for raw, path in flattened:
        if not isinstance(raw, dict):
            _issue(issues, "error", "invalid-element", path, "Element must be an object.")
            continue
        element = raw
        element_id = element.get("id")
        if not isinstance(element_id, str) or not element_id.strip():
            _issue(issues, "error", "missing-id", path + ".id", "Element id must be a non-empty string.")
        elif element_id in ids:
            _issue(issues, "error", "duplicate-id", path + ".id", "Duplicate id; first seen at {}.".format(ids[element_id]))
        else:
            ids[element_id] = path
            by_id[element_id] = element

        element_type = element.get("type")
        if element_type not in ALLOWED_TYPES:
            _issue(issues, "error", "unsupported-type", path + ".type", "Use a PPTX-IR primitive, not {!r}.".format(element_type))
        if not _is_number(element.get("zIndex")):
            _issue(issues, "error", "missing-z-index", path + ".zIndex", "Numeric zIndex is required.")
        if element_type in BOX_TYPES and not _has_box(element):
            _issue(issues, "error", "missing-box-geometry", path, "Element requires numeric x, y, w, and h.")
        if element_type in LINE_TYPES and not _has_line(element):
            _issue(issues, "error", "missing-line-geometry", path, "Line requires numeric x1, y1, x2, and y2.")
        if element.get("dash") is not None and element.get("dash") not in ALLOWED_DASHES:
            _issue(issues, "error", "invalid-dash", path + ".dash", "Unsupported dash style.")
        if element_type == "text":
            missing = sorted(field for field in TEXT_REQUIRED if field not in element)
            for field in missing:
                _issue(issues, "error", "missing-text-field", path + "." + field, "PowerPoint-safe text field is required.")
            if element.get("wrap") is False and element.get("fit") not in {"shrink", "none"}:
                _issue(issues, "warning", "unsafe-text-fit", path + ".fit", "Non-wrapping text should normally use fit='shrink'.")
        if element_type == "connector":
            for field in sorted(CONNECTOR_REQUIRED):
                if field not in element:
                    _issue(issues, "error", "missing-connector-field", path + "." + field, "Explicit connector semantics are required.")
            if element.get("mustNotBeSegmented") is not True:
                _issue(issues, "warning", "segmentable-connector", path + ".mustNotBeSegmented", "Connectors should remain a single editable line.")
            _validate_direction(element, path, issues)
        if element_type == "svgIcon":
            has_binding = bool(element.get("path")) or bool(element.get("svg")) or (
                bool(element.get("library")) and bool(element.get("icon"))
            )
            if not has_binding:
                _issue(issues, "error", "unbound-icon", path, "SVG icon requires library+icon, path, or inline svg.")
        if element_type == "group" and not isinstance(element.get("constraints"), dict):
            _issue(issues, "error", "missing-group-constraints", path + ".constraints", "Groups require explicit child constraints.")

    _validate_parents(flattened, by_id, issues)
    _validate_nested_children(elements, "$.elements", issues)
    return issues


def _validate_direction(element: Dict[str, Any], path: str, issues: List[Issue]) -> None:
    if not _has_line(element):
        return
    direction = element.get("direction")
    x1, y1, x2, y2 = (element[field] for field in ("x1", "y1", "x2", "y2"))
    expected: Optional[str] = None
    if abs(x2 - x1) >= abs(y2 - y1):
        expected = "left_to_right" if x2 > x1 else "right_to_left" if x2 < x1 else None
    else:
        expected = "top_to_bottom" if y2 > y1 else "bottom_to_top" if y2 < y1 else None
    aliases = {
        "left-to-right": "left_to_right", "right-to-left": "right_to_left",
        "top-to-bottom": "top_to_bottom", "bottom-to-top": "bottom_to_top",
    }
    normalized = aliases.get(direction, direction)
    if expected and normalized not in {expected, "custom"}:
        _issue(issues, "warning", "direction-mismatch", path + ".direction", "Declared direction does not match connector endpoints (expected {}).".format(expected))


def _validate_parents(
    flattened: Sequence[Tuple[Any, str]],
    by_id: Dict[str, Dict[str, Any]],
    issues: List[Issue],
) -> None:
    for raw, path in flattened:
        if not isinstance(raw, dict) or not raw.get("parentId"):
            continue
        parent = by_id.get(raw["parentId"])
        if parent is None:
            _issue(issues, "error", "missing-parent", path + ".parentId", "Referenced parent does not exist.")
            continue
        constraints = parent.get("constraints", {})
        if not constraints.get("childrenMustStayInside"):
            continue
        if not _has_box(raw) or not _has_box(parent):
            continue
        left = parent["x"] + constraints.get("paddingLeft", 0)
        right = parent["x"] + parent["w"] - constraints.get("paddingRight", 0)
        top = parent["y"] + constraints.get("paddingTop", 0)
        bottom = parent["y"] + parent["h"] - constraints.get("paddingBottom", 0)
        if raw["x"] < left or raw["x"] + raw["w"] > right or raw["y"] < top or raw["y"] + raw["h"] > bottom:
            _issue(issues, "error", "child-out-of-bounds", path, "Child violates the padded bounds of parent {!r}.".format(raw["parentId"]))


def _validate_nested_children(elements: Sequence[Any], prefix: str, issues: List[Issue]) -> None:
    for index, raw_parent in enumerate(elements):
        path = "{}[{}]".format(prefix, index)
        if not isinstance(raw_parent, dict):
            continue
        children = raw_parent.get("children")
        if not isinstance(children, list):
            continue
        constraints = raw_parent.get("constraints", {})
        if constraints.get("childrenMustStayInside") and _has_box(raw_parent):
            left = raw_parent["x"] + constraints.get("paddingLeft", 0)
            right = raw_parent["x"] + raw_parent["w"] - constraints.get("paddingRight", 0)
            top = raw_parent["y"] + constraints.get("paddingTop", 0)
            bottom = raw_parent["y"] + raw_parent["h"] - constraints.get("paddingBottom", 0)
            for child_index, child in enumerate(children):
                child_path = "{}.children[{}]".format(path, child_index)
                if isinstance(child, dict) and _has_box(child):
                    if child["x"] < left or child["x"] + child["w"] > right or child["y"] < top or child["y"] + child["h"] > bottom:
                        _issue(issues, "error", "child-out-of-bounds", child_path, "Nested child violates its group's padded bounds.")
        _validate_nested_children(children, path + ".children", issues)
