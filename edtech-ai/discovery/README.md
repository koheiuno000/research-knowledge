# EdTech–AI discovery data

This directory holds **machine-retrieved candidate metadata**, separate from reviewed paper summaries in `academic-papers/`.

| Path | Purpose |
|------|---------|
| `schema/` | JSON Schema + **schema-only** example (not real evidence) |
| `screening/decisions.yaml` | Human include/exclude overlay (never overwritten by fetch) |
| `screening/foundational_exceptions.yaml` | Pre-window papers approved manually (`foundational_exception` + justification) |
| `data/` | Generated candidate bundles (gitignored by default) |

Run the prototype fetcher:

```bash
# Rolling 10-year window ending on search date (Sep 2026 example → 2016-09-23 .. 2026-09-23):
python3 scripts/edtech_ai_discovery/fetch_candidates.py --search-date 2026-09-23 --max-per-query 3 --mailto you@example.com --write-html
```

See [`../DESIGN.md`](../DESIGN.md) for architecture and integration plan.
