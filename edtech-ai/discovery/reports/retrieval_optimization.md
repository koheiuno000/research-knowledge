# EdTech–AI discovery retrieval optimization (2026-09-23)

Diagnostic engineering report — not reviewed evidence.

## Phase 1 — Root-cause analysis (measured / code-supported)

### Process state

- **No `fetch_candidates.py` process** was running at inspection time (`pgrep` empty).
- The long `--resume --paginate --request-delay 1.25` run was **interrupted** (~28 min). It wrote **35** raw snapshots under `data/raw/20260923T011345/` but **did not finish**; `query_manifest.json` was never created because the prior implementation only persisted the manifest at **end of run**.
- On-disk bundle remains the **second partial live run**: **146** unique candidates (`candidates_openalex.json`, `generated_at` 2026-09-23T00:03:09Z), **51** failed query slots, **1** truncated query (Nature `adaptive learning randomized` 200/368).

### Planned workload

| Metric | Value |
|--------|------:|
| Enabled sources | 17 |
| Track A queries | 4 |
| Track B queries | 4 |
| **Unique search strings** | 8 |
| Legacy slots (source×track×query) | **136** |
| Work units (source×unique query) | **136** |
| Extra HTTP pages (from raw `meta.count` > 200) | **+1** (estimated **137** HTTP calls for full backfill) |

Track A and Track B use **disjoint** OpenAlex search strings (no cross-track deduplication opportunity without changing query text).

### Recorded API snapshots (`data/raw/`)

- **135** query snapshot files across sessions; **2** with `meta.count` > 200.
- `meta.count` over snapshots: min **0**, median **1**, max **368**.

### Bottleneck factors (ordered by impact)

1. **Sequential pacing** — `--request-delay 1.25` adds ≥ **170 s** sleep alone for 136 work units (code: sleep after every page and after failures).
2. **Transient API errors** — first full run: **121/136** failures (503/504); second run: **51** failures (429/DNS). Each failure triggers up to **6** retries with backoff up to **45 s** (`openalex_get`, 90 s timeout per attempt).
3. **End-only checkpointing** — interrupted runs lose in-memory manifest progress; resume must re-infer from bundle + raw (expensive, error-prone).
4. **Pagination** — only **one** query required a second page in observed data; not the dominant cost today.
5. **Local processing** — keyword flags and JSON writes are negligible vs network.

**Conclusion:** Slowdown is **API latency + conservative pacing + retry storms on failed queries**, not local CPU or `--max-per-query 200` truncation (truncation affects **completeness**, not runtime, except when `--paginate` multiplies pages).

## Phase 2 — Strategy comparison

| Approach | HTTP calls (estimate) | Completeness vs current queries | Notes |
|----------|----------------------:|----------------------------------|-------|
| **A. Per-track keyword searches (legacy loop)** | 136 (+ pages) | Baseline | Same OpenAlex `search` strings as `tracks.yaml`. |
| **B. Consolidated search + local track classification** | **136** (+ pages) | **Equivalent** with current config | 8 unique strings × 17 sources; tracks share no duplicate strings, so **no call reduction** unless queries are merged (would change search semantics). Implemented as **work units**: one fetch, classify Track A/B locally. |
| **C. Source+date filter only + local keywords** | 17 × (pages per source) | **Risky** | High-volume sources (AER, Nature) could require **thousands** of pages; unacceptable without volume caps. Not recommended. |

**Recommendation:** **B (work-unit architecture)** for maintainability and identical coverage, plus **checkpoints**, **incremental `from_updated_date`**, and **tunable pacing** — not because it reduces 136 calls today.

## Phase 3 — Historical vs incremental (implemented)

| Mode | CLI | Behavior |
|------|-----|----------|
| **Historical backfill** | `--mode backfill` (default) | Fixed publication window; resumable manifest; exit **1** if any work unit ≠ `complete`. |
| **Incremental update** | `--mode incremental` | Requires `manifest.last_complete_run_at`; adds OpenAlex `from_updated_date` with overlap (default **7** days); same search strings and whitelist. Catches **newly indexed/updated** metadata, not “new publication date” alone. |

## Phase 4 — Reliability / observability (implemented)

- Per–work-unit manifest checkpoint (`query_manifest.json`) after each success/failure.
- Optional `candidates_openalex.checkpoint.json` on resume (`--checkpoint-bundle`, default on with `--resume`).
- Atomic bundle write (`persist.atomic_write_json`).
- Structured `FETCH …` / `SUMMARY …` progress lines.
- `run_complete` flag on manifest; `last_complete_run_at` only when all work units `complete`.
- Audit generation remains separate: `generate_audit_report.py`.

## Phase 5 — Benchmark (offline)

| Metric | Before (legacy design) | After (work units + checkpoints) |
|--------|------------------------|----------------------------------|
| Work units / HTTP (estimated) | 136 (+1 page) | **136 (+1 page)** — **no reduction** |
| Live elapsed time | Not re-run (user: no concurrent live fetch) | N/A |
| Unique candidates | 146 (partial bundle) | Unchanged until next completed backfill |

**Unit tests:** 24 passed (`python3 -m unittest scripts.edtech_ai_discovery.test_discovery`).

## Commands (researcher)

```bash
# Plan / estimate (offline)
python3 scripts/edtech_ai_discovery/benchmark_retrieval_plan.py
python3 scripts/edtech_ai_discovery/fetch_candidates.py --dry-run --search-date 2026-09-23

# Historical backfill (resumable; use polite pool via git user.email or OPENALEX_MAILTO)
python3 scripts/edtech_ai_discovery/fetch_candidates.py \
  --mode backfill \
  --search-date 2026-09-23 \
  --max-per-query 200 \
  --paginate \
  --audit \
  --resume \
  --request-delay 0.5

# Incremental (after one fully complete backfill)
python3 scripts/edtech_ai_discovery/fetch_candidates.py \
  --mode incremental \
  --search-date 2026-09-23 \
  --max-per-query 200 \
  --paginate \
  --audit \
  --resume

# Audit only (no HTTP)
python3 scripts/edtech_ai_discovery/generate_audit_report.py \
  --baseline edtech-ai/discovery/data/backups/pre_resume_20260923T011319Z/candidates_openalex.json
```

## Remaining risks

- **Incomplete backfill** until all 136 work units are `complete` in the manifest.
- **Incremental** cannot run until `last_complete_run_at` is set.
- **Consolidating** the 8 search strings into fewer OpenAlex queries would speed up but **changes reproducible baseline** — document any future change explicitly.
- **429** errors: prefer `OPENALEX_MAILTO` / git email and avoid stacking high delay with aggressive retry loops.
