# Research Knowledge Base

Personal research workspace for structured literature review, evidence mapping, and synthesis across several education research areas.

## Research areas

| Folder | Focus |
|--------|--------|
| [`sb-cpd/`](sb-cpd/) | School-based CPD, teacher professional knowledge, teaching practice, and student achievement |
| [`preschool-impact/`](preschool-impact/) | Preschool and early childhood education impact evidence |
| [`edtech-ai/`](edtech-ai/) | Educational technology and AI in education |
| [`skills-tvet/`](skills-tvet/) | Skills development and TVET |
| [`climate-education/`](climate-education/) | Climate change and education |

Each area follows the same layout:

```
<area>/
├── academic-papers/    # Paper summaries (substantive source of truth)
├── literature-review/  # references.bib, synthesis, generated dashboards
└── README.md
```

## How evidence is organized

- **Paper summaries** under `<area>/academic-papers/` are the substantive records (findings, Evidence Mapping, interpretation).
- **`references.bib`** in each area’s `literature-review/` folder is the bibliographic source of truth for that area’s evidence base (no repository-wide master bibliography yet).
- **Generated dashboards** (e.g. `literature_review.md`) integrate summaries; regenerate with scripts—do not hand-edit paper-level findings there.
- **PDFs** stay **local-only** under `<area>/academic-papers/pdf/` and are not tracked by Git.

## Scripts and dashboard

- **`scripts/`** — build tools (today: SB-CPD literature review generator).
- **`dashboard/`** — reserved for future cross-domain views and search/filtering.

### Regenerate SB-CPD literature review

```bash
python3 scripts/build_literature_review.py
```

Writes `sb-cpd/literature-review/literature_review.md` from `sb-cpd/academic-papers/`.

## Future direction

Summaries may eventually carry richer metadata (research area, topics, geography, methods, evidence relationships). A paper can be relevant to more than one area; the layout is not limited to one topic per paper.
