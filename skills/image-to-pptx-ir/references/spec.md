# PPTX-IR specification

## Contents

- Document structure
- Coordinate model
- Primitives
- Text safety
- Connectors
- Icons and images
- Groups and bounds
- Layering
- Validation rules

## Document structure

Require `canvas`, `elements`, `layerRules`, and `validationRules`. Treat `theme`, `source`, and `version` as recommended metadata.

```json
{
  "version": "0.1",
  "canvas": { "width": 1304, "height": 706, "unit": "px" },
  "theme": { "fontFamily": "Microsoft YaHei" },
  "layerRules": { "background": 0, "texts": 50 },
  "elements": [],
  "validationRules": ["shortTextMustNotWrap"]
}
```

Use the repository's `schemas/render.schema.json` as the canonical machine-readable definition.

## Coordinate model

Use source-image pixels. Require positive canvas dimensions. Use `x/y/w/h` for boxed primitives and `x1/y1/x2/y2` for lines and connectors.

Assign every element a unique stable `id`, allowed `type`, and numeric `zIndex`.

## Primitives

Allow only:

```text
text rect roundRect line connector path svgIcon image group
```

Represent borders explicitly with `stroke`, `strokeWidth`, and `dash`. Use `rect` with `radius: 0` for square frames and `roundRect` for intentional rounded corners.

## Text safety

Require:

```json
{
  "id": "availability_label",
  "type": "text",
  "text": "高可用、高可靠",
  "x": 867,
  "y": 100,
  "w": 170,
  "h": 24,
  "fontFamily": "Microsoft YaHei",
  "fontSize": 16,
  "fontWeight": 700,
  "color": "#222222",
  "align": "center",
  "valign": "middle",
  "wrap": false,
  "fit": "shrink",
  "margin": 0,
  "zIndex": 50
}
```

Keep short labels unwrapped. Prefer separate text boxes over a single multiline pseudo-table. Budget extra width for font substitution.

## Connectors

Require explicit geometry and semantics:

```json
{
  "id": "channel_send",
  "type": "connector",
  "x1": 548,
  "y1": 186,
  "x2": 604,
  "y2": 186,
  "stroke": "#F04A23",
  "strokeWidth": 1.8,
  "dash": "solid",
  "beginArrow": "none",
  "endArrow": "triangle",
  "direction": "left_to_right",
  "semantic": "发送方向",
  "mustNotBeSegmented": true,
  "zIndex": 20
}
```

Use `solid`, `dash`, `dot`, or `dashDot`. Match declared direction to endpoint order. Keep a single arrow in a single connector.

## Icons and images

Bind `svgIcon` using one of:

- `library` plus `icon`;
- SVG `path` data;
- inline `svg`.

Use `image` only for content that is intrinsically raster or cannot reasonably remain editable. Provide its `href` and geometry. Never use a full-slide image as the final editable deliverable.

## Groups and bounds

Require constraints on groups:

```json
{
  "id": "node_a",
  "type": "group",
  "x": 142,
  "y": 142,
  "w": 310,
  "h": 344,
  "zIndex": 10,
  "constraints": {
    "paddingLeft": 18,
    "paddingRight": 18,
    "paddingTop": 12,
    "paddingBottom": 12,
    "childrenMustStayInside": true,
    "clipChildren": false
  }
}
```

For a child with `parentId`, enforce:

```text
child.x >= parent.x + paddingLeft
child.x + child.w <= parent.x + parent.w - paddingRight
child.y >= parent.y + paddingTop
child.y + child.h <= parent.y + parent.h - paddingBottom
```

## Layering

Use a stable layer plan such as:

```json
{
  "background": 0,
  "containerFrames": 10,
  "communicationArrows": 20,
  "innerBoxes": 30,
  "icons": 40,
  "texts": 50,
  "configArrows": 60,
  "debug": 999
}
```

Remove debug elements before delivery. Raise connectors above opaque frames when needed.

## Validation rules

At minimum enforce:

- `childrenMustStayInsideParent`
- `shortTextMustNotWrap`
- `dashMustBePreserved`
- `arrowDirectionMustMatchSource`
- `singleArrowMustNotBeSegmented`

Add task-specific rules whenever a visual distinction carries meaning.
