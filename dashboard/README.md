# Dashboard

**Root hub:** [`index.html`](index.html) — cross-area landing (hero, scope strip, featured SB-CPD module, browse links).

It is **generated** from paper summaries under each research area (today: SB-CPD counts and links). Do not hand-edit paper counts or evidence in this file.

### Regenerate (SB-CPD area + root hub)

Either command updates **both** the SB-CPD literature review HTML and the root dashboard:

```bash
python3 scripts/build_literature_review.py
```

Root hub only (same output as the second step above):

```bash
python3 scripts/build_dashboard.py
```

Per-area Markdown/HTML workflow details: [`sb-cpd/academic-papers/README.md`](../sb-cpd/academic-papers/README.md).
