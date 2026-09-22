# Loyalka et al. (2019) — Does Teacher Training Actually Work? (China NTTP)

**Primary category:** `07_teacher-pd-interventions`

**Secondary themes:** Teacher knowledge (mathematical knowledge for teaching); teaching practice (student-reported); student mathematics achievement; LMIC / government at-scale PD; null RCT evidence; heterogeneous effects by teacher qualifications

---

## Paper type and design (read first)

| Question | Answer |
|----------|--------|
| **What type of paper is this?** | **Large-scale cluster randomized evaluation** of China’s **National Teacher Training Program (NTTP)** for junior high **mathematics** teachers, with optional **post-training follow-up** and **post-training evaluation** arms. |
| **Unit of analysis** | **Schools** randomized (then second-stage randomization for evaluation); outcomes at **student** and **teacher** level. |
| **Identification** | **Intent-to-treat / average treatment effects** from OLS with **block fixed effects** and baseline controls; **cluster-robust SEs** (school) for student outcomes; **robust SEs** for teacher outcomes (PDF pp. 12–13). Pre-analysis plan registered with 3ie (PDF p. 12). |
| **What claims the design supports** | **Causal ITT effects of PD assignment** on each outcome separately. **Does not** estimate Teacher Knowledge → Teaching Practice, Practice → Achievement, or mediation pathways. Authors discuss “potential mediators” and a “causal chain” qualitatively but **do not** model mediation (PDF pp. 12–13, 21–22). |

---

## Evidence Mapping

| Relationship | Examined? | Evidence Type | Notes |
|---|---|---|---|
| PD → Teacher Knowledge | Yes | RCT (ITT) | **Teacher math knowledge** test (Michigan MKT-based instrument); **null** average effects at endline (Table 5, PDF p. 18). |
| PD → Teaching Practice | Yes | RCT (ITT) | **Student-reported** teacher practice, care, management, communication; **null** average effects (Table 4, PDF pp. 16–17). |
| PD → Student Achievement | Yes | RCT (ITT) | **Student math achievement** tests; **null** average effects at endline (Table 2, PDF pp. 14–15). |
| Teacher Knowledge → Teaching Practice | No | — | Both measured as **separate PD outcomes**; no regression linking knowledge to practice. |
| Teaching Practice → Student Achievement | No | — | Practice is **student report**; achievement is separate outcome; **no** model of practice → achievement. |
| Teacher Knowledge → Student Achievement | No | — | Not estimated. |
| Knowledge → Practice → Achievement pathway | No | — | Separate ATEs on mediators discussed; **no mediation analysis**. |

---

## Effect Summary

Primary endline ITT estimates, covariate-adjusted specification (authors’ main discussion focus; Table 2, 4, 5).

| Relationship | Outcome | Direction | Estimate | Unit | SE | p-value | Significance | Comparison / Arm | Time Point | Sample | Identification | Source | Notes |
|---|---|---:|---|---:|---|---|---|---|---|---|---|---|
| PD → Student Achievement | Student mathematics achievement (normalized test score) | Insignificant | -0.006 | SD | 0.034 | Not reported | Not significant | PD vs Control | Endline | 14599 | Cluster RCT / ITT | Table 2, p. 141 | Panel A, row (1), column (2); cluster-robust SEs |
| PD → Teaching Practice | Student-reported teacher practice index | Insignificant | 0.043 | SD | 0.045 | Not reported | Not significant | PD vs Control | Endline | 14405 | Cluster RCT / ITT | Table 4, p. 144 | Panel A, row (1), column (1); student-reported practice |
| PD → Teacher Knowledge | Teacher math knowledge (MKT-based test summary index) | Insignificant | 0.153 | SD | 0.138 | Not reported | Not significant | PD vs Control | Endline | 293 | Cluster RCT / ITT | Table 5, p. 145 | Panel A, row (1), column (1); heteroskedastic-robust SEs; null after multiple-testing adjustment per table note |

---

## 1. Citation

**Citation key:** `loyalka2019`

**Full citation:** Loyalka, Prashant, Anna Popova, Guirong Li, and Zhaolei Shi. 2019. “Does Teacher Training Actually Work? Evidence from a Large-Scale Randomized Evaluation of a National Teacher Training Program.” *American Economic Journal: Applied Economics* 11 (3): 128–154.

**BibTeX:** `sb-cpd/literature-review/references.bib`

**Publication type:** Peer-reviewed journal article (*American Economic Journal: Applied Economics*).

**DOI / URL:** https://doi.org/10.1257/app.20170226 (PDF p. 1).

**Journal / Series:** *American Economic Journal: Applied Economics*, vol. 11, no. 3 (2019).

**Country:** China

**Region:** East Asia and Pacific

**Setting:** Randomized evaluation of the government **National Teacher Training Program (NTTP)**; **300 rural junior high schools** in **94 counties** in **one large province** (province name not stated in main text, PDF p. 7); grades 7–9 **mathematics** teachers; academic year **2015–2016**.

All bibliographic information must be verified against the original paper or another explicitly verified bibliographic source. Do not infer missing metadata.

---

## 2. Research Question

What are the **impacts** of a typical large-scale **national teacher PD program** (and post-training **follow-up** and **content evaluation** interventions) on **student mathematics achievement**, **teacher knowledge**, **teaching-related behaviors**, and related outcomes—and **why** might effects be absent?

---

## 3. Conceptual Focus

- **Teacher PD / CPD intervention** (NTTP + optional follow-up/evaluation)
- **Null experimental evidence** on government at-scale PD in an LMIC context
- **Teacher mathematical knowledge for teaching** (MKT-based test)
- **Student-reported** instructional practice (not observational quality scores)
- **Mechanism / implementation** analysis (content too theoretical; passive delivery)—interpretive, not causal mediation

---

## 4. Teacher Knowledge (Constructs and Measurement)

**Construct (authors’ terminology):** **“Teacher math knowledge”** measured with tests of **“math knowledge for teaching”** developed by researchers at the University of Michigan (**Hill, Rowan, and Ball 2005**, PDF p. 11).

**Interpretation for review:** This aligns with the **mathematical knowledge for teaching (MKT)** tradition. The paper does **not** label constructs as PCK, MCK, or GPK separately, and does **not** report disaggregated MKT subdomains in main tables.

**Measurement:**
- **Instrument:** Standardized mathematics tests for teachers (MKT-based).
- **Timing:** Baseline, midline, endline (PDF p. 11).
- **Scoring:** Normalized using **control-group mean and SD**; effects in **SD units** (PDF p. 11).
- **Items / reliability:** Not clearly reported in main text for the teacher test (psychometric detail given for **student** tests, PDF p. 11).
- **Primary outcome in Table 5:** Summary index labeled **“Teacher math knowledge”** (PDF p. 18).

**Do not conflate with:** Teacher **beliefs/attitudes** (separate columns in Table 5) or **student-reported teaching practice** (Table 4).

---

## 5. Teaching Practice (Constructs and Measurement)

**Measured:** **Yes**, as **secondary/mediator outcomes**—not as a predictor of achievement in a pathway model.

**Method:** **Student survey** reports of teacher behaviors in class (PDF pp. 10–11, 16).

**Dimensions (Table 4, PDF p. 17):**
- Teacher **practice**
- Teacher **care**
- Teacher **management**
- Teacher **communication**

**Construction:** Standard scales from education literature; **GLS-weighted summary indices** (Anderson 2008), normalized to SD units (PDF pp. 10–11).

**Not used for main ITT tables:** Independent **classroom observation** of teaching quality (PD sessions were observed; student classrooms were not scored with a structured observation protocol in main results).

**PD → practice:** Estimated as **separate ITT** on student-reported indices; **null** on average (Table 4).

---

## 6. Student Outcomes

**Subject:** **Mathematics** (junior high, grades 7–9).

**Assessment:** **35-minute** grade-appropriate tests aligned with **national and provincial curricula**; items from standardized curricula; expert content validity; pilot validation (Cronbach’s α ≈ 0.8 for student tests, PDF p. 11). **Vertically scaled**; same form baseline/midline, **different form endline** (PDF p. 11).

**Scoring:** Each wave **normalized** to control-group mean and SD; effects in **SD units** (PDF p. 11).

**Sample:** Primary sample **~16,661 students** (+ spillover sample → **~33,492–33,580** total students cited, PDF pp. 3, 8).

**Other student outcomes:** Dropout, math self-concept, anxiety, motivation, time on math (Table 3)—generally **null**.

---

## 7. Data and Sample

- **Country:** China (rural junior high schools, one large province, 94 counties).
- **Education level:** Junior high (**grades 7–9**).
- **Subject:** **Mathematics** teachers and students.
- **Sample:** **300 schools**; **600 math teachers** (primary + spillover design); **~33,500 students** (PDF pp. 3, 8).
- **Intervention:** 15-day **in-person** NTTP (Nov 2015) + **online** PD; optional **SMS/phone follow-up**; optional **post-training lesson evaluation** (PDF pp. 6–7, 13).
- **Randomization:** Two-stage cluster RCT (Figure 1, PDF p. 9); **100 schools per arm** at first stage; block FE by grade/provider (PDF pp. 8–9).

---

## 8. Methods and Identification

| Element | Detail |
|--------|--------|
| Design | **Cluster randomized trial** (school-level assignment). |
| Estimation | OLS: \(Y_{ij} = \alpha_0 + \alpha_1 D_j + X_{ij}\alpha + \tau_k + \varepsilon_{ij}\) (PDF p. 12). |
| Outcomes | Student achievement, student reports, teacher knowledge/beliefs, spillovers. |
| Controls | Baseline outcome when available; expanded covariate-adjusted specs (PDF p. 13). |
| Inference | School clustering (student outcomes); heteroskedastic-robust SEs (teacher outcomes). |
| Power | MDES **~0.13 SD** (5% level); abstract cites ability to detect **≥0.11 SD** (PDF pp. 3, 9). |

**Claim strength:** **Causal ITT** for **PD → each outcome** under RCT assumptions + low attrition (~8% students endline, PDF p. 12). **Not causal** for relationships among knowledge, practice, and achievement.

---

## 9. Main Findings (Literature-Review Priorities)

### A. Empirical — PD → student mathematics achievement (ITT)

**Endline, covariate-adjusted (Table 2, PDF pp. 14–15):**
- **PD vs control:** **−0.006 SD** (SE 0.034), not significant.
- **PD + follow-up vs control:** **0.005 SD** (SE 0.035), not significant.
- **PD + evaluation vs control:** **0.011 SD** (SE 0.032), not significant.
- Upper bound of 95% CI for PD vs control **~0.061 SD**—authors rule out large positive effects (PDF p. 15).

### B. Empirical — PD → teacher math knowledge (ITT)

**Table 5 (PDF p. 18):** PD vs control coefficient **0.153 SD** (SE 0.138); PD + follow-up **0.222 SD** (SE 0.145)—**not significant** at 10% after multiple-testing adjustment (table note).

### C. Empirical — PD → student-reported teaching practice (ITT)

**Table 4 (PDF p. 17):** PD vs control on **teacher practice** index **0.043 SD** (SE 0.045)—**not significant** (adjusted for multiple testing per note).

### D. Empirical — secondary student outcomes

**Table 3:** No significant impacts on dropout, math anxiety, motivation, time on math (PDF pp. 16–17).

### E. Heterogeneity — PD → achievement (exploratory)

**Table 7 (PDF pp. 19–20):** Significant interactions by **teacher college degree** and **math major**—e.g., PD × college degree **−0.203 SD** on achievement; some **positive** effects for students of **less qualified** teachers (e.g., PD + follow-up **+0.097 SD** for teachers without four-year college, table note). Authors interpret as **substitution away from classroom** during training (PDF pp. 19–21).

### F. Mechanisms (qualitative + descriptive, not causal mediation)

High **participation/attendance** but content **~52% theoretical**; delivery **passive/lecture-heavy**; teachers report difficulty applying content (PDF pp. 21–22). **Not** formal mediation estimates.

### G. Authors’ interpretation

Large-scale **government PD** with typical features (lectures, limited follow-up) **failed to improve** knowledge, practice, or achievement on average; cautionary for billions spent on similar programs (PDF pp. 3–4, 23).

---

## 10. Mechanism / Interpretation

| Type | Content |
|------|---------|
| **Tested statistically** | **PD ITT** on each outcome separately; heterogeneity by teacher qualifications. |
| **Not tested** | Mediation: Knowledge → Practice → Achievement. |
| **Authors’ mechanism narrative** | Overly theoretical content; rote/passive delivery; constraints to implement (PDF pp. 21–22). |

---

## 11. Relevance to My Study

### Directly useful

- **Benchmark null LMIC-relevant RCT** of **government national PD** (cited in Popova et al. and Kozuka discussion)—contrasts with PD that **does** shift practice/knowledge in Ethiopia.
- **Measurement reference:** **MKT-based teacher math knowledge** test (Hill et al.) and **student-reported practice indices** as PD outcome measures—useful for comparing **what “teacher knowledge” and “practice” meant** across studies.
- **Theory of Change caution:** PD can **fail simultaneously** on knowledge, practice, and achievement ITTs—supports careful claims that improving one link implies others.
- **School-based / at-scale PD design:** 15-day centralized training, online supplement, optional follow-up—parallel to features Popova codes on ITTSI.

### Important limits for SB-CPD

- **China**, rural junior high **math** only—not your setting without qualification.
- **Practice** = **student report**, not observer protocol like Kozuka.
- **No pathway estimates**—cannot cite for Knowledge → Practice → Achievement.

### Potential citation use

- Cite for **experimental evidence** that a **large-scale national teacher PD program** (with follow-up/evaluation arms) had **null ITT effects** on **teacher math knowledge for teaching**, **student-reported teaching behaviors**, and **student math achievement** after one year—with **mechanism discussion** of theoretical content and passive delivery.

---

## 12. Limitations (for my use)

- **One province** (unnamed in main text); rural junior high math teachers only.
- **Student-reported** practice may differ from observational practice.
- **Teacher knowledge** measure summary in tables; limited item-level/psychometric reporting in main text.
- **Short run** (~one academic year); authors argue intermediate outcomes should have moved if longer-run gains were likely (PDF pp. 3–4).
- **Spillover / replacement teacher** during 15-day training complicates interpretation of heterogeneity (PDF pp. 4, 19–21).

---

## 13. Page / Table Verification (key claims)

| Claim | Reference |
|--------|-----------|
| RCT design, sample 300 schools, 600 teachers | PDF pp. 3, 7–9; Figure 1 |
| Teacher MKT-based knowledge test | PDF p. 11; Table 5 |
| Student math tests | PDF p. 11; Tables 1–2 |
| Null achievement ITT | Table 2, PDF pp. 14–15 |
| Null teacher knowledge / student-reported practice | Tables 4–5, PDF pp. 17–18 |
| Heterogeneity by teacher qualifications | Table 7, PDF pp. 19–20 |
| Mechanism qualitative analysis | PDF pp. 21–22 |

*(PDF page numbers = journal pages 128–154 ≈ PDF pages 1–27 of file.)*

---

## Researcher Takeaway

**Core contribution:** **Cluster RCT** of China’s **National Teacher Training Program** shows **precise null ITTs** on **student math achievement**, **teacher math knowledge for teaching**, and **student-reported teaching behaviors**, with qualitative evidence that PD was **too theoretical** and **passively delivered**.

**Best use in my literature review:** **Folder 07**—counterpoint **government at-scale PD** that **does not** move knowledge, practice, or achievement jointly; pair with **Popova** (design gaps) and **Kozuka** (positive teacher-side ITTs under different PD model).

**Do not use this paper to claim:** That teacher knowledge **causes** practice or achievement; that **pathway mediation** was tested; or that PD **always** fails (heterogeneity for less qualified teachers; different contexts).

**Priority for my review:** **Core** — landmark **LMIC-relevant** null **PD intervention** RCT with **explicit teacher knowledge measure** and **practice/achievement** outcomes.

---

## 14. Possible Use in Literature Review (Checklist)

- Teacher knowledge: ☑ (MKT-based test as PD outcome)
- Teaching practice: ☑ (student-reported; PD outcome only)
- Student achievement: ☑ (null ITT)
- Teacher PD interventions (folder 07): ☑ (primary)
- Knowledge → Practice (direct): ☐
- Practice → Achievement (direct): ☐
- Knowledge → Achievement (direct): ☐
- LMIC evidence: ☑ (China, government at-scale PD)
- Mathematics education: ☑
