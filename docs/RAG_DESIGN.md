# RAG Design — planned, not yet implemented

## Evidence sources
- S1: Year-specific FIFA country-summary CSV, with SHA-256 and columns.
- S2: Official FIFA/AFC match and standings pages: URL + retrieved passage + date + edition.
- S3: Computed Fact Sheet generated from clean source data and formulas.

## Example fact entry
```json
{
  "fact_id": "F-001",
  "claim": "In the 2002–2022 dataset South Korea played 24 matches",
  "value": 24,
  "unit": "matches",
  "period": "2002-2022",
  "formula": "sum(Games Played) for Country=South Korea",
  "source_ids": ["SRC-WC-2002", "SRC-WC-2006", "SRC-WC-2010", "SRC-WC-2014", "SRC-WC-2018", "SRC-WC-2022"],
  "verification_status": "not_independently_verified"
}
```

## Practical workflow
1. Ingest source files; record original hashes, validate schema and write facts.
2. Preserve typed numeric facts in JSON or SQLite. Index human text documents only if retrieval is needed.
3. Retrieve evidence IDs by question and supply only those facts and excerpts to LLM.
4. Require factual claims to cite real `F-...` or document passage IDs. The model may not invent IDs.
5. Separate deterministic number/formula validation from LLM linguistic review.
6. If a source is missing, contradictory, out-of-scope or insufficient, return HOLD / 확인 불가.
7. Edit and approve manually before publishing.

## Tests
- Answerable: 'What were South Korea’s games, wins, GF and GA for 2002–2022?'
- Scope: 'Why did Korea not win in 2026?' -> out of dataset scope; HOLD.
- Unsupported: 'Which tactic caused a loss?' -> no match-level tactical evidence; HOLD.
- Citation integrity: fictitious `F-999` -> ERROR.
- Numeric consistency: fabricated 26 games -> ERROR.
- Semantics: citation points to correct source but source does not support assertion -> editor HOLD.

Embedding stores or LangChain are *optional* until many longer documents are ingested; a structured fact table and exact search are preferable for numeric claims.
