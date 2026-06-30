# Visual validation checklist

## Structure

- [ ] Major regions align with the source.
- [ ] Square and rounded frames use the correct primitive.
- [ ] Repeated rows, columns, and spacing are consistent.
- [ ] Mirrored content uses recomputed coordinates.

## Connectors

- [ ] Solid and dashed meanings are preserved.
- [ ] Every arrow points in the source direction.
- [ ] The arrowhead is on the intended endpoint.
- [ ] One continuous arrow remains one connector.
- [ ] Connectors are not hidden by opaque shapes.

## Text

- [ ] Titles and short labels do not wrap.
- [ ] Font family, size, weight, color, and alignment are plausible.
- [ ] Structured multiline content uses intentional line boxes.
- [ ] Native PowerPoint does not introduce new wraps.

## Bounds and layers

- [ ] Children respect parent padding.
- [ ] Shapes, icons, and labels stay within intended containers.
- [ ] z-index matches the visual overlap.
- [ ] Debug marks are absent.

## Delivery

- [ ] Both JSON documents validate.
- [ ] The generated PPTX is editable.
- [ ] A PNG or native render was compared with the source.
- [ ] Every correction is present in `render.json`.
- [ ] Remaining risks are documented.
