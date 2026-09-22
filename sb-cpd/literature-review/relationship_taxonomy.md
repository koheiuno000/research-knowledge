# SB-CPD — Approved Effect Summary relationship taxonomy

This file documents the **researcher-approved** relationship labels for **Effect Summary** rows in SB-CPD. The machine-readable list is `relationship_taxonomy.json` (same folder).

## Core pathways (Evidence Map alignment)

These seven relationships match the SB-CPD conceptual evidence pathways used in **Evidence Mapping**:

1. PD → Teacher Knowledge  
2. PD → Teaching Practice  
3. PD → Student Achievement  
4. Teacher Knowledge → Teaching Practice  
5. Teaching Practice → Student Achievement  
6. Teacher Knowledge → Student Achievement  
7. Knowledge → Practice → Achievement  

**Outcome** carries the specific construct (e.g. mathematics achievement, physics achievement, content knowledge test). **Comparison / Arm**, **Time Point**, and **Identification** distinguish separate effect rows under the same relationship.

## Additional approved relationship (cross-program evidence)

8. **PD design characteristic → Program impact**

**Why it exists:** Some papers (e.g. Popova et al. 2022) report **bivariate associations** between **PD design characteristics** and **standardized program-level student test-score impacts** across many evaluated programs. That estimand is **not** the same as **PD → Student Achievement** (causal effect of being assigned to PD on a student’s achievement in one trial).

- Use **PD design characteristic → Program impact** for those cross-study association coefficients.  
- Put the **design characteristic** in **Outcome** (e.g. lesson enactment, no career incentives).  
- Use **Identification:** Cross-study association.  
- **Evidence Mapping** may still record that the paper synthesizes evidence on PD → Student Achievement at the review level.

## Governance

- Do **not** add new relationship labels without researcher approval (update `relationship_taxonomy.json` and this document together).  
- Prefer **Outcome**, **Comparison / Arm**, **Notes**, or **Secondary Relevance** over inventing a new relationship.  
- Unknown labels in paper summaries are **flagged at build time**; they are not silently treated as approved.

Other research areas will define their own taxonomies when developed; SB-CPD labels do not apply repository-wide.
