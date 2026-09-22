# SB-CPD / Teacher Development

Literature review and evidence base for **school-based continuous professional development (SB-CPD)**, organized around:

```
Teacher Professional Knowledge → Teaching Practice → Student Achievement
```

(with **teacher PD/CPD interventions** as a primary empirical entry point where PD is the treatment).

## Layout

- **`academic-papers/`** — one Markdown summary per reviewed paper (substantive source of truth). See [`academic-papers/README.md`](academic-papers/README.md) for the folder taxonomy (categories `01`–`08`).
- **`literature-review/`** — `references.bib`, researcher-written synthesis/outline, and **generated** `literature_review.md`.
- **`academic-papers/pdf/`** — local copies of full papers (Git-ignored).

## Regenerate integrated review

From the repository root:

```bash
python3 scripts/build_literature_review.py
```

## Workflow (short)

1. Read and verify the PDF locally.
2. Add a summary under the appropriate category in `academic-papers/`.
3. Add one BibTeX entry to `literature-review/references.bib`.
4. Run the generator above.
