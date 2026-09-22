# Palacios & Rojas-Velásquez (2023) — Impact of Weather Shocks on Educational Outcomes in the Municipalities of Colombia

**Primary category:** `03_droughts-rainfall-and-human-capital`

**Secondary themes:** Colombia; SPI rainfall shocks; municipal fixed effects; NCR; IADR; standardized test scores; mediation (suggestive)

---

## Paper type and design (read first)

| Question | Answer |
|----------|--------|
| **What type of paper is this?** | **Municipal panel fixed-effects** study of **excess and deficit rainfall shocks** (SPI-based) on **net coverage (NCR)**, **dropout (IADR)**, and **standardized test scores**. |
| **Not** | Student-level RCT; **not** pure school-disruption closure study. |
| **Mediation (§5.3)** | Authors treat mediation as **suggestive** under sequential unconfoundedness—**distinct** from **total-effect** FE rows in Tables 2–4. |

---

## 1. Citation

**Citation key:** `palacios2023`

**Full citation:** Palacios, Paola, and Libardo Rojas-Velásquez. 2023. “Impact of Weather Shocks on Educational Outcomes in the Municipalities of Colombia.” *International Journal of Educational Development* 101: 102816.

**BibTeX:** `climate-education/literature-review/references.bib`

**Publication type:** Peer-reviewed journal article.

**DOI / URL:** https://doi.org/10.1016/j.ijedudev.2023.102816

**Country:** Colombia

**Region:** Latin America and Caribbean

**Setting:** **Municipal** panel; **high/middle school** coverage and dropout; **math/reading** municipal test scores; **SPI** excess/deficit rainfall shocks with **lagged** specifications.

**Journal / Series:** *International Journal of Educational Development*, vol. 101, 102816 (2023).

**Data and sample:** **Colombian municipalities** (~**6,300–7,450** obs. per table); **SPI-based** excess/deficit **rainfall shocks**; outcomes **NCR** (net coverage), **IADR** (dropout), municipal **math/reading** scores; **municipal fixed effects** with mechanism controls in preferred columns.

**Core contribution:** **Municipal FE** estimates link **excess rainfall** to **lower coverage**, **higher middle-school dropout**, and **lower test scores** (controlled specs); **deficit rainfall** often **opposite-signed**; **mediation** via income, mortality, and damage is **suggestive** (§5.3).

Verified against local PDF: `academic-papers/pdf/palacios-2023-ijed.pdf`.

---

## 2. Research Question

How do **excess and deficit rainfall shocks** affect **school coverage**, **dropout**, and **academic performance** at the **municipal** level, and through which **economic/health/infrastructure** channels (mediation)?

---

## 3. Evidence Mapping

| Relationship | Examined? | Evidence Type | Notes |
|---|---|---|---|
| Weather Shock → Learning | Yes | Quasi-experimental (FE) | **Math and reading** municipal scores (Table 4). |
| Weather Shock → Schooling | Yes | Quasi-experimental (FE) | **NCR** (coverage) and **IADR** (dropout)—Table 2–3. |
| Weather Shock → School Disruption | Yes | Quasi-experimental (FE) | **School damage** probability as mechanism (Table 6); total effects in main tables. |
| Weather Shock → Household Vulnerability | Yes | Quasi-experimental (FE) | **Income/transfers/agricultural income** mediators (Table 6). |
| Weather Shock → Health & Nutrition | Yes | Quasi-experimental (FE) | **Infant mortality** and disease indicators in mechanism block. |
| School Disruption → Learning | No | — | **Not** separate identified mediation from closures to scores; use **total** rainfall FE effects for learning. |
| Adaptation → Educational Outcomes | No | — | — |

---

## Effect Summary

**Preferred specification:** Tables 2–4 columns **with controls** (mechanisms + covariates)—second column per outcome block in extracted Table 2 / Table 4 grids. SEs in parentheses; municipal FE.

| Relationship | Outcome | Direction | Estimate | Unit | SE | p-value | Significance | Comparison / Arm | Time Point | Sample | Identification | Source | Notes |
|---|---|---:|---|---:|---|---|---|---|---|---|---|---|
| Weather Shock → Schooling | High school NCR | Negative | −0.451 | percentage points | 0.219 | Not reported | p < 0.05 | Excess rainfall shock (lagged spec.) | Municipal panel | 6327 obs. | Municipal FE | Table 2, HS NCR col. with controls | Uncontrolled −1.692*** |
| Weather Shock → Schooling | Middle school NCR | Insignificant | −0.335 | percentage points | 0.271 | Not reported | Not significant | Excess rainfall shock | Municipal panel | 6327 obs. | Municipal FE | Table 2, MS NCR col. with controls | — |
| Weather Shock → Schooling | Middle school IADR | Positive | 0.426 | percentage points | 0.206 | Not reported | p < 0.05 | Excess rainfall shock | Municipal panel | 7452 obs. | Municipal FE | Table 3, MS IADR col. with controls | **Dropout rate** ↑ with excess rain |
| Weather Shock → Learning | Math score | Negative | −2.335 | score points | 0.136 | Not reported | p < 0.01 | Contemporary excess rainfall shock | Municipal panel | 6311 obs. | Municipal FE | Table 4, Math col. with controls | Uncontrolled −3.957*** |
| Weather Shock → Learning | Reading score | Negative | −2.377 | score points | 0.135 | Not reported | p < 0.01 | Contemporary excess rainfall shock | Municipal panel | 6312 obs. | Municipal FE | Table 4, Reading col. with controls | Uncontrolled −4.246*** |

**Examined but omitted from primary rows (Tables 2–4, controlled cols. where noted):** **High school IADR** excess shock **0.340** pp (SE 0.245)—**not significant** (Table 3). **Deficit rainfall** shocks on **NCR/IADR/scores**—**significant** in several specs (often **positive** for coverage/scores); see full tables. **Lagged excess** on math **0.017** (insignificant) and reading **0.115** (insignificant) with controls (Table 4). **Mediation decomposition** (§5.3)—**examined**, reported as **suggestive**, not duplicated as Effect Summary rows.

**Flagged:** Author **SD scalings** in prose (e.g., ~**1.03 SD** math)—derived from reported coefficients, not separate table cells.

---

## 13. Key Takeaway

**Excess rainfall shocks** at the **municipal** level reduce **coverage** and **test scores** and raise **middle-school dropout** in FE specifications with controls; **mediation** results are **suggestive** only.

---

## 14. Relevance to the Climate Change & Education Knowledge Base

**Role classification:** **Core empirical FE** for **rainfall shock → schooling & learning** (Colombia).

**Priority for my review:** **Core**.
