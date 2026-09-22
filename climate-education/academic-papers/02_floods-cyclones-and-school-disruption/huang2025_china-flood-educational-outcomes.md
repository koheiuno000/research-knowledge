# Huang & Dong (2025) — When the Levee Breaks: The Impact of Floods on Educational Outcomes in China

**Primary category:** `02_floods-cyclones-and-school-disruption`

**Secondary themes:** China; flood exposure share ages 0–15; 2015 census; county FE; 1998 Yangtze flood DiD; rural heterogeneity

---

## Paper type and design (read first)

| Question | Answer |
|----------|--------|
| **What type of paper is this?** | **Quasi-experimental** study of **childhood flood exposure** on **years of education** and **high-school entry**, using **2015 census** microdata and **1998** severe-flood **difference-in-differences**. |
| **Not** | Standardized **test-score / learning** outcomes in main attainment tables—**do not** map attainment or HS entry to **Weather Shock → Learning**. |
| **Main shock measure** | **Share of years ages 0–15** living in a **flooded county** (`Exp`). |
| **Fixed effects** | County FE, province × birth-year FE, county linear cohort trends; SEs clustered at **county**. |

---

## 1. Citation

**Citation key:** `huang2025`

**Full citation:** Huang, Zenghe, and Xiaofang Dong. 2025. “When the Levee Breaks: The Impact of Floods on Educational Outcomes in China.” *Journal of Development Economics* 174: 103450.

**BibTeX:** `climate-education/literature-review/references.bib`

**Publication type:** Peer-reviewed journal article.

**DOI / URL:** https://doi.org/10.1016/j.jdeveco.2025.103450

**Country:** China

**Region:** East Asia and Pacific

**Setting:** **2015 population census** (non-migrants aged **15–30**); county-level **flood exposure** histories; rural/urban split; **1998** flood cohort DiD (Table 10).

**Journal / Series:** *Journal of Development Economics*, vol. 174, 103450 (2025).

**Data and sample:** **2015 China census** microdata (non-migrants aged **15–30**); **county-level** flood exposure as share of years **0–15** flooded (e.g., Table 3 rural **n = 223,146**); subsamples for **rural/urban**, flood-risk groups, and **1998** cohort DiD (Table 10 rural **n = 91,235**). **No standardized test-score / learning** outcome in primary attainment specifications.

**Core contribution:** **County FE** evidence that **childhood flood exposure** reduces **years of education** (large rural effects; **1998** rural DiD **−0.155** years in Table 10) and **high-school entry** in high-risk areas; **expenditure** heterogeneity (Table 5) supports **household** channels—not learning tests.

Verified against local PDF: `academic-papers/pdf/huang-2025-jde.pdf`.

---

## 2. Research Question

How does **early-life flood exposure** affect **educational attainment** and **high-school entry**, and how do **1998** severe floods and **flood-risk heterogeneity** shape those effects?

---

## 3. Evidence Mapping

| Relationship | Examined? | Evidence Type | Notes |
|---|---|---|---|
| Weather Shock → Learning | No | — | Main outcomes are **years of education** and **HS entry dummy**—**schooling**, not learning tests. |
| Weather Shock → Schooling | Yes | Quasi-experimental | Table 3, Table 10, heterogeneity tables. |
| Weather Shock → School Disruption | Yes | Quasi-experimental / descriptive | Flood exposure and policy/dam heterogeneity (Table 4); reduced-form schooling focus. |
| Weather Shock → Household Vulnerability | Yes | Quasi-experimental | Expenditure mechanisms (Table 5)—**distal** channel, separate from schooling rows. |
| Weather Shock → Health & Nutrition | No | — | Not primary outcomes. |
| School Disruption → Learning | No | — | — |
| Adaptation → Educational Outcomes | Yes | Quasi-experimental | Flood **policy/dams/detention basins** interactions (Table 4)—**mitigation heterogeneity**, not randomized adaptation. |

---

## Effect Summary

**Primary schooling outcomes only** (Table 3 unless noted). Robust SEs in parentheses (county-clustered). Significance from table stars.

| Relationship | Outcome | Direction | Estimate | Unit | SE | p-value | Significance | Comparison / Arm | Time Point | Sample | Identification | Source | Notes |
|---|---|---:|---|---:|---|---|---|---|---|---|---|---|
| Weather Shock → Schooling | Years of education | Negative | −0.786 | years | 0.257 | Not reported | p < 0.01 | +1 pp in flood exposure share (ages 0–15) | 2015 census cross-section | 223,146 (rural Panel A) | County FE + province×year FE + county trends | Table 3 Panel A, col. (1) | Full rural sample |
| Weather Shock → Schooling | Whether to enter high school | Insignificant | −0.051 | prob. (marginal) | 0.045 | Not reported | Not significant | +1 pp exposure share | 2015 census | 223,146 (rural) | Same as col. (1) | Table 3 Panel A, col. (2) | Dummy = 1 if enrolled in HS |
| Weather Shock → Schooling | Years of education | Negative | −1.433 | years | 0.444 | Not reported | p < 0.01 | +1 pp exposure share | 2015 census | 133,178 (high flood risk) | Same FE structure | Table 3 Panel A, col. (5) | High flood-risk subsample |
| Weather Shock → Schooling | Whether to enter high school | Negative | −0.254 | prob. (marginal) | 0.078 | Not reported | p < 0.01 | +1 pp exposure share | 2015 census | 133,178 (high flood risk) | Same FE structure | Table 3 Panel A, col. (6) | **Schooling** outcome (HS entry) |
| Weather Shock → Schooling | Years of education | Negative | −0.155 | years | 0.064 | Not reported | p < 0.05 | 1998-affected × cohorts 1983–1996 | Rural 1998 DiD | 91,235 | County FE + province×year FE | Table 10 Panel A, col. (1) | Abstract rounds to **0.16 years**; table **−0.155** |

**Examined, not primary Effect Summary rows:** **Urban Panel B** Table 3 col. (1) years of education **−0.365** (SE 0.330)—**insignificant**. **Low flood-risk** rural cols. (3)–(4): attainment **−0.446** (SE 0.313, insignificant), HS entry **0.063** (insignificant). **1998 DiD** urban cols. and **0–6 vs 7–15** cohort splits (Table 10)—reported in paper; only primary rural total-cohort row above unless extended pass added.

**Flagged (derived, not table cells):** Implied **mean-exposure** effect (~**−0.21 years** using mean `Exp` ≈ 0.268). Abstract **~0.16 years** for 1998 rural rounds Table 10 **−0.155\*\***.

**Learning outcomes:** Paper **does not** estimate **test scores** or comparable **learning** measures for main attainment tables—omission from Effect Summary **does not** imply learning was unaffected, only **not analyzed** as such.

---

## 13. Key Takeaway

**Childhood flood exposure** substantially lowers **years of education** (especially **high-risk rural** areas); **1998** cohort DiD corroborates long-run **schooling** losses. **Do not** classify attainment/HS entry under **Learning**.

---

## 14. Relevance to the Climate Change & Education Knowledge Base

**Role classification:** **Core empirical QE** for **flood → schooling** (China, census scale).

**Priority for my review:** **Core**.
