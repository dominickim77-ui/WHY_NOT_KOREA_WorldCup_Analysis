# Data and Fact-check Audit — 2026-11-09

## Files actually inspected
- `WHY_NOT_KOREA_WorldCup_Analysis.ipynb`: 27 cells; pre-existing saved outputs.
- `WHY_NOT_KOREA_Final_Article.md`: published draft supplied in ZIP.
- Pre-existing README and ZIP manifest.

## Verified inside supplied notebook (NOT FIFA independently)
- 2002–2022 Korea: 24 games, 7 wins, 28 GF, 35 GA, 29.17% wins, 1.17 GF/game and 1.46 GA/game.
- Comparison: Argentina 31 games, Brazil 34, Germany 34; rankings and means as shown in README.
- Correlations against Position in saved notebook: goals/game −0.678, conceded/game +0.637.
- The 9/9 validation asserts nine known expected constants; all passed in saved notebook. It cannot establish source authenticity.
- Year-level Korea history is compiled for 1954–2022 while country comparisons and article Fact Sheet use 2002–2022. The year-series plot may not be scoped to article period.

## Blocking issues
1. No original year-specific FIFA CSV ZIP in the submitted ZIP; cannot independently reproduce statistics.
2. Exact original Kaggle dataset URL and license unknown.
3. `.git/` included in upload; not needed in publication package.
4. The `DA 실습/` tree contains unrelated course notebooks and potentially sensitive records; intentionally excluded.
5. Existing charts/ folder referenced by original README was missing in upload; recovered five charts from saved notebook outputs.
6. 2026 World Cup has concluded, but the presented dataset ends with 2022: make scope unambiguous.
7. Current AI writing uses a Fact Sheet in a prompt, rather than indexed retrieval and verifiable evidence.
8. AI model name hard-coded in notebook may not be available; validate current account access at execution time.
9. `Stage` grouping is derived from final Position only; avoid implying verified knockout bracket metadata.
10. Cannot claim news/article was run through an independent official-source verifier.

## Integrity checks to add
- Unique `(Year, Team)` rows, expected year set 2002/06/10/14/18/22, each 32 teams, numeric and nonnegative measures.
- `Win+Draw+Loss == Games Played`, `Goals For - Goals Against == Goal Difference`, without silently correcting failures.
- Check 2022 and 2002 Korea records against FIFA/AFC official source documents and cite page/match IDs.
- Verify all presented chart labels, timeframes, denominator and units.
- Check official W/D/L convention for penalty shoot-outs; avoid inferring actual knockout advancement from `Win` alone.

## Source distinction
- Kaggle World Cup data: source descriptor in notebook, exact link absent.
- FIFA (official reference): https://www.fifa.com/en/articles/world-cup-qatar-2022-surprises-that-shook-the-world
- AFC (historical Korea match record): https://www.the-afc.com/en/national/fifa_world_cup/news/korea_republic_%40the_world_cup.html
- Official 2026 standings with shootout-draw note: https://www.fifa.com/en/articles/final-tournament-standings

External pages above can guide subsequent verification, but this package does not yet contain a completed match-by-match audit.
