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

## PDFs

PDFs may live under `pdf/` locally. They are not tracked by Git (see repository `.gitignore`).

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
