# Academic Papers Workspace

Focused workspace for summarizing papers for a literature review on teacher professional knowledge, teaching practice, student achievement, and teacher professional development (including mathematics education and LMIC contexts).

## Classification system

Each paper gets **one** Markdown summary in **one primary folder**. Do not duplicate summaries across folders. Record secondary relevance inside the summary file.

Classify by the relationship the paper **actually estimates**, not merely by which variables it measures. In particular, a PD intervention study that reports effects on knowledge, practice, and achievement **does not** by itself identify causal links among knowledge, practice, and achievement unless those links are **separately and directly estimated**.

Similarly, if teaching practice improves under an intervention while student achievement does not, that pattern **does not** establish that teaching practice has no causal effect on achievement.

### A. Construct / relationship literature (folders 01–06)

Conceptual pathway:

```
Teacher Knowledge
        ↓
Teaching Practice
        ↓
Student Achievement
```

| Folder | Use when the paper **primarily** … |
|--------|-------------------------------------|
| `01_teacher-knowledge/` | Addresses **teacher knowledge itself**: concepts, definitions, measurement, dimensions, or descriptive evidence. |
| `02_teaching-practice/` | Addresses **teaching practice itself**: concepts, measurement, classroom observation, instructional quality, active learning, learner-centered instruction, etc. |
| `03_student-achievement/` | Addresses **student achievement itself** or its measurement, when the paper does **not** primarily estimate one of the relationships in 04–06. |
| `04_knowledge-to-practice/` | **Directly examines** Teacher Knowledge → Teaching Practice (causal or associational, as reported). |
| `05_practice-to-achievement/` | **Directly examines** Teaching Practice → Student Achievement. |
| `06_knowledge-to-achievement/` | **Directly examines** Teacher Knowledge → Student Achievement. |

Folders **04–06** are reserved for studies that **directly estimate** the corresponding arrow—not for intervention studies that only move multiple outcomes in parallel.

### B. Teacher PD intervention literature (folder 07)

```
                 ┌→ Teacher Knowledge
                 │
Teacher PD ──────┼→ Teaching Practice
                 │
                 └→ Student Achievement
```

| Folder | Use when … |
|--------|------------|
| `07_teacher-pd-interventions/` | **Teacher PD or CPD is the treatment/exposure** of primary interest. The design evaluates the **effect of PD**, even if the study also measures knowledge, practice, and student outcomes. Typical estimates: PD → knowledge, PD → practice, PD → achievement. |

Intervention studies belong here when PD is the main empirical focus. They should **not** be filed under 04–06 **unless** the paper’s primary contribution is a direct estimate of knowledge → practice, practice → achievement, or knowledge → achievement (unusual for pure PD RCTs).

### C. Reviews and cross-study synthesis (folder 08)

| Folder | Use when … |
|--------|------------|
| `08_reviews-and-synthesis/` | The paper’s **main contribution** is to **review, synthesize, taxonomize, or conceptually organize evidence** across **multiple studies or programs**—not to evaluate **one** specific PD intervention or to **directly estimate one arrow** in the Teacher Knowledge → Teaching Practice → Student Achievement chain. |

Typical examples: structured literature reviews, cross-study comparisons of program design, survey instruments that code many PD programs, associational analyses across impact evaluations, or conceptual frameworks for PD design backed by synthesis of existing studies.

Papers here **may** include the authors’ own empirical cross-study analyses (e.g., regressions across evaluated programs). They should **not** be classified under `07_teacher-pd-interventions` merely because they **summarize or discuss** causal impact evaluations of PD. Folder **07** is for studies whose primary design evaluates **a specific PD program or intervention**; folder **08** is for **evidence about the broader literature or program landscape**.

## PDFs

PDFs may live under `pdf/` locally. They are not tracked by Git (see repository `.gitignore`).

## Reference management

> **One summarized paper = one verified BibTeX entry.**

Evidence chain:

```
Original PDF (local only)
        ↓
Paper summary (.md)
        ↓
BibTeX entry (references.bib)
        ↓
Literature synthesis / manuscript
```

1. Store the original PDF locally in `academic-papers/pdf/`.
2. Create one Markdown summary using `paper_summary_template.md`.
3. Assign one stable **citation key:** `firstauthorYEAR` (e.g. `kozuka2025`; use `firstauthorYEARa` / `b` if needed).
4. Add exactly **one** corresponding BibTeX entry to `literature-review/references.bib` (master database—no per-paper `.bib` files).
5. Verify bibliographic metadata against the original PDF (or other explicitly verified source) before adding it.
6. Never invent missing bibliographic information.
7. If metadata is uncertain, omit the BibTeX field and flag it in the paper summary.
8. Use the same citation key in the paper summary, `references.bib`, literature synthesis, and manuscript.

`references.bib` should list papers that are part of this literature-review **evidence base**, not every source merely cited inside another paper.

### Future paper processing

```
PDF
  ↓
Structured paper summary (academic-papers/<category>/*.md)
  ↓
Evidence Mapping
  ↓
Effect Summary (quantitative estimates, when applicable)
  ↓
Primary category (folder)
  ↓
BibTeX entry (literature-review/references.bib)
  ↓
Researcher verification
  ↓
Generate integrated literature review
  ↓
Commit
```

1. **Individual paper summaries** under `academic-papers/` are the **substantive source of truth** (findings, Evidence Mapping, Effect Summary, interpretation).

### Evidence Mapping vs Effect Summary

- **Evidence Mapping** records whether each conceptual relationship was **examined** and what **type of evidence** applies (RCT, association, synthesis, etc.). It does not store point estimates.
- **Effect Summary** records **structured quantitative results** for estimated relationships: direction (using the controlled vocabulary below), estimate, unit, reported SE/p-value/significance, comparison/arm, time point, effect-specific sample, identification, and source (table/page).
- **Direction rule:** statistically insignificant coefficients are **`Insignificant`**, not Positive/Negative, regardless of sign. **Direction does not imply causality**—interpret with **Identification** (e.g. RCT/ITT vs cross-study association).
- **p-value vs Significance:** **p-value** = exact numerical p-value if reported, else `Not reported` (never calculated from SEs/CIs/stars). **Significance** = reported conclusion or threshold (including stars/notes). Example: `Not reported` + `p < 0.05` is valid when only stars are given.
- **Relationship labels:** use the estimand the row represents (e.g. Popova bivariate regressions → `PD design characteristic → Program impact`, distinct from intervention ITT rows under `PD → Student Achievement`).
- **Approved taxonomy (SB-CPD):** `../literature-review/relationship_taxonomy.json` (documented in `relationship_taxonomy.md`). Build tools flag Effect Summary relationships not in that list; unknown labels are **not** auto-approved.
2. **`literature-review/references.bib`** is the **bibliographic source of truth**.
3. **`literature-review/literature_review.md`** is a **generated, derived** evidence dashboard—do **not** manually maintain paper-level findings there.
4. **`literature-review/literature_synthesis.md`** is a separate, **researcher-written** narrative synthesis (not generated).

Rebuild the integrated page after updating summaries or adding papers:

```bash
python3 scripts/build_literature_review.py
```

## Workflow

1. Identify a potentially important paper.
2. Decide whether it is **Core**, **Supporting**, or **Optional**.
3. Assign **one primary folder** using the rules above.
4. Read the paper.
5. Create one Markdown summary using `paper_summary_template.md` (including **Evidence Mapping**).
6. Record only findings actually supported by the paper.
7. Add the paper to `../literature-review/key_papers.md`.
8. Periodically synthesize findings in `../literature-review/literature_synthesis.md`.
9. Use the synthesis—not isolated paper summaries—to draft `../literature-review/literature_review_outline.md` and eventually the manuscript.

## Important principle

> Do not cite a paper in the manuscript based only on an AI-generated summary. Verify the relevant claim against the original paper before citation.
