---
name: image-to-pptx-ir
description: Parse PowerPoint slide screenshots, design images, or visual references into semantic JSON and a deterministic PPTX-IR/render JSON, then guide generation and visual regression of editable PPTX files. Use for image-to-PowerPoint reconstruction, screenshot-to-editable-slide work, PPTX layout extraction, render JSON creation, or fidelity debugging involving arrows, dashes, text wrapping, icon bindings, layers, and parent-child bounds.
---

# Image to PPTX-IR

Convert a visual slide reference into an executable intermediate representation before generating PowerPoint. Preserve editability, geometry, and rendering intent.

## Enforce the pipeline

Use this sequence:

```text
reference image
  → semantic.json
  → render.json (PPTX-IR)
  → validate
  → editable PPTX
  → native render / PNG regression
  → update render.json
```

Do not bypass the IR by generating PPTX or HTML directly from the image. Treat `render.json` as the single source of truth; write every correction back to it.

## Read the right references

- Read [references/spec.md](references/spec.md) before authoring or changing Render JSON.
- Read [references/workflow.md](references/workflow.md) when executing the full image-to-PPTX workflow.
- Read [references/visual-validation.md](references/visual-validation.md) before final delivery or when fidelity stalls.

The repository containing this skill also provides canonical schemas in `schemas/`, examples in `examples/`, and the `pptx-ir` validation/preview CLI.

## Parse the source image

1. Record the source pixel dimensions. Keep source pixels as the IR coordinate system.
2. Divide the page into regions before resolving individual elements: title, labels, major panels, connectors, footer/configuration, legend, and decoration.
3. Create `semantic.json` with the page intent, key messages, regions, and region-to-element mapping.
4. Create `render.json` using only these primitives:
   - `text`
   - `rect`
   - `roundRect`
   - `line`
   - `connector`
   - `path`
   - `svgIcon`
   - `image`
   - `group`
5. Expand vague components such as `card`, `flow`, `channelRow`, `smartArt`, or generic `icon` into primitives.
6. Assign stable, semantic IDs and explicit z-indices.

## Preserve PowerPoint behavior

For text:

- Specify font family, size, weight, color, alignment, wrapping, fit, margin, and box geometry.
- Set short labels and titles to `wrap: false` and usually `fit: shrink`.
- Allow 20–30% horizontal safety space where exact font metrics are unavailable.
- Split structured multiline content into separate text elements.

For connectors:

- Use `connector`, not a generic line, for arrows.
- Specify endpoints, dash style, arrowheads, declared direction, semantic purpose, and `mustNotBeSegmented`.
- Keep each visually continuous arrow as one element.
- Place arrows above frames that would otherwise cover them.

For icons:

- Bind `svgIcon` to a named library icon, SVG path, or inline SVG.
- Do not improvise an icon from unrelated primitive shapes unless the source itself is geometric.

For containers:

- Specify padding and whether children must remain inside.
- Use `parentId` or nested `children` consistently.
- Recompute mirrored coordinates; do not blindly copy them.

## Validate before rendering

Run the repository CLI when available:

```bash
pptx-ir validate semantic.json --strict
pptx-ir validate render.json --strict
pptx-ir preview render.json preview.svg
```

Resolve every error. Review warnings as likely fidelity defects. In addition, check:

- unique IDs and legal primitive types;
- positive canvas and element geometry;
- child bounds including parent padding;
- connector direction versus endpoints;
- solid/dash preservation and arrowhead end;
- text wrapping and font substitution risk;
- source-order-independent z-index behavior.

## Generate and regress the PPTX

Map source pixels to the target slide:

```text
ppt_x = image_x / image_width  * slide_width_inches
ppt_y = image_y / image_height * slide_height_inches
ppt_w = image_w / image_width  * slide_width_inches
ppt_h = image_h / image_height * slide_height_inches
```

Create text as editable text boxes, shapes and connectors as native PowerPoint elements, and complex icons as SVG. Render the PPTX to PNG and compare it with the source. Also inspect it in Microsoft PowerPoint when native fidelity matters; a server or LibreOffice render is not conclusive.

Iterate by changing only `render.json`, regenerating, and rerunning validation. Never hide a structural defect with a flattened full-slide screenshot.

## Deliver

For an image-to-JSON request, deliver:

1. `semantic.json`
2. `render.json`
3. validation results
4. known rendering risks

For an image-to-PPTX request, additionally deliver:

1. editable `.pptx`
2. preview render
3. source-of-truth `render.json`
4. fixed issues and remaining risks

Reject final output that has incorrect arrow direction, lost dash styles, unexplained image flattening, obvious child overflow, or automatic wrapping of short labels.
