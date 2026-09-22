# Dashboard

**Root hub:** [`index.html`](index.html) — cross-area landing (forest hero, synthesis/textbook pathways, about, thematic explore cards, resources, and browse facets).

It is **generated** from paper summaries under each research area. Do not hand-edit paper counts or evidence in `index.html`.

### Regenerate

Rebuild all thematic areas and the root hub:

```bash
python3 scripts/build_literature_review.py --area all
```

Root hub only:

```bash
python3 scripts/build_dashboard.py
```

### Learning textbook (planned)

When HTML textbook content is added, use this **canonical entry point** at the repository root:

- **File:** `textbook/index.html`
- **Link from dashboard:** `../textbook/index.html`

The root hub generator (`scripts/literature_review/hub_root.py`) activates the Learning Textbook pathway card only when that file exists at build time. Do not add alternate paths or placeholder textbook pages.

Per-area Markdown/HTML workflow details: [`sb-cpd/academic-papers/README.md`](../sb-cpd/academic-papers/README.md).
