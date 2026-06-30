# Examples

| Example | Purpose | Elements | Deliverables |
| --- | --- | ---: | --- |
| `ai-operations-system` | Featured fidelity fixture | 210 | Reference PNG, semantic JSON, render JSON, editable PPTX, SVG preview, manifest |
| `cluster-communication` | Minimal quick start | 6 | Semantic JSON, render JSON, SVG preview |

The featured example provides the complete conversion evidence chain:

```text
ai-operations-system.reference.png
  → ai-operations-system.semantic.json
  → ai-operations-system.render.json
  → ai-operations-system.editable.pptx
  → ai-operations-system.preview.svg
```

The reference PNG is an organization-neutral, sanitized visual fixture. The PPTX contains native shapes and text plus embedded vector icons; it is not a flattened full-slide screenshot.

Tests verify the reference dimensions, PPTX structure, editable text, embedded media, and removal of brand placeholders.
