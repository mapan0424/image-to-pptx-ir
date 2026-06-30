# Reconstruction workflow

## Contents

- Stage 1: inspect
- Stage 2: model semantics
- Stage 3: author render IR
- Stage 4: validate
- Stage 5: generate PPTX
- Stage 6: regress

## Stage 1: inspect

Record image size, aspect ratio, dominant grid, repeated spacing, fonts, colors, stroke widths, corner radii, arrow styles, icon families, and visible overlaps. Divide the page into regions before measuring local elements.

## Stage 2: model semantics

Create `semantic.json`. Explain the page intent and relationships without pretending this file can render the page. Give regions stable IDs and map them to planned render-element IDs.

## Stage 3: author render IR

Create `render.json` from back to front:

1. canvas and background;
2. major container frames;
3. connectors that should pass behind content;
4. internal cards and shapes;
5. icons;
6. text;
7. foreground connectors and annotations.

Use source pixels. Expand components into primitives. Record uncertainties in a separate risk list rather than silently guessing.

## Stage 4: validate

Run:

```bash
pptx-ir validate semantic.json --strict
pptx-ir validate render.json --strict
pptx-ir preview render.json preview.svg
```

Fix errors in the JSON. Use the SVG only as a quick structural diagnostic; it is not a PowerPoint fidelity oracle.

## Stage 5: generate PPTX

Convert pixel coordinates proportionally to slide inches. Create native text boxes, shapes, and connectors. Insert SVG icons as vectors. Preserve element z-order exactly. Avoid renderer-specific convenience components that cannot round-trip to IR.

## Stage 6: regress

Render the generated slide to PNG. Compare source and output at the same dimensions. Inspect major anchors first, then typography, connectors, icons, and fine spacing. When possible, open in Microsoft PowerPoint and confirm text wrapping, font substitution, dash styles, arrowheads, and SVG behavior.

Change `render.json`, regenerate, and repeat. Do not patch the PPTX manually because that breaks reproducibility.
