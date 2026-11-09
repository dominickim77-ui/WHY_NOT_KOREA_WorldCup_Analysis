# Improvement Plan

## P0 — source integrity and reproducibility
- [ ] Locate and license-check original Kaggle archive matching saved notebook output (23 year CSVs plus summary filename).
- [ ] Save SHA-256 for every input, and make a `data/README.md` with URLs, date, version and definitions.
- [ ] Implement data checks and run with all six 2002–2022 tournaments; investigate failed assertions rather than rewriting originals.
- [ ] Confirm representative Korean 2002/2010/2022 match records with FIFA official documentation.

## P1 — statistical nuance and visualizations
- [ ] Separate historical 1954–2022 trend from core 2002–2022 analyses; fix titles.
- [ ] Report each nation’s participation years and match denominators on charts.
- [ ] Separate `Position` categories from actual bracket stages; explicitly specify team-edition count as unit.
- [ ] Add 2002 versus 2006–2022 within-Korea year-level decomposition with careful small sample warnings.
- [ ] Show attack (GF/game) vs defense (GA/game) quadrant chart, with one dot per team-edition (not just four aggregates).
- [ ] Add an uncertainty-aware comparison: per-tournament distributions and leave-one-tournament-out sensitivity, NOT confidence claims based on independence of games.
- [ ] Acknowledge selection bias: top-finishers play more matches and goals contribute mechanically to final rank.
- [ ] Put labels, direct values, color semantics, source, period and denominator on chart exports.

## P2 — evidence-linked RAG
- [ ] Add fact IDs `F-001`, etc, with formula, source rows and file SHA.
- [ ] Store official source excerpts with citations (document URL, publish/access date, passage).
- [ ] Retrieve top-k actual evidence passages; generation must cite returned IDs.
- [ ] Build deterministic validation of numeric claims, citations and explicit `HOLD` for unsupported claims.
- [ ] Test answerable and unanswerable questions; log retrieval coverage and final editor review.

## P3 — presentation and project portfolio
- [ ] README status table, architecture diagram and evidence checklist, before/after charts.
- [ ] Optional Streamlit/Plotly dashboard (year/country selector, official data notes, Fact Sheet, draft article, editorial status).
- [ ] English file/folder names, Korean editorial prose; tests and requirements pinning.
- [ ] Do not overwrite current original without backup and review.
