# Contributing

Thank you for improving Image to PPTX-IR.

## Development setup

```bash
git clone https://github.com/mapan0424/image-to-pptx-ir.git
cd image-to-pptx-ir
python3 -m pip install -e .
python3 -m unittest discover -s tests -v
```

## Change rules

- Keep the runtime dependency-free unless a dependency unlocks a major capability and is discussed first.
- Preserve Python 3.9 compatibility.
- Add or update a JSON fixture for changes to the IR.
- Add a focused test for every validator rule or CLI behavior.
- Keep `SKILL.md` concise; put detailed guidance in its direct `references/` files.
- Treat `render.json` as the source of truth in reconstruction examples.

## Pull requests

Explain the problem, the IR or behavior change, and how it was verified. Run:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m pptx_ir validate examples/cluster-communication.semantic.json --strict
PYTHONPATH=src python3 -m pptx_ir validate examples/cluster-communication.render.json --strict
```

By contributing, you agree that your contribution is licensed under Apache-2.0.
