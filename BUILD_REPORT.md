# Build Report — "Brazil 2026: The Comeback"

Built locally on 2026-11-02. **Nothing was published.** No accounts were used, no sign-ins happened, no credentials or tokens were used, no `git push` was run, no remote repository was created, nobody was contacted, and nothing was posted to LinkedIn. Everything below lives only in this folder.

## What ran successfully

Every notebook was executed end to end with `jupyter nbconvert --execute` and finished with **zero cell errors** (final pass, after all patches). All 13 charts were generated from computed data (none hand-drawn, none invented).

| Notebook | Result |
|---|---|
| `00_setup.ipynb` | Environment check passed; TSE files verified to reproduce Lula 51.79% / Flávio 48.21% in round 2. Chart: `charts/00_municipalities_by_region.png`. |
| `01_two_rounds_toy.ipynb` | Toy A: 47 vs 45 in round 1 → 50 vs 53 in round 2 (transfer + turnout). Toy B: turnout alone flips 47 vs 45 to 47 vs 55. Chart: `charts/01_toy.png`. |
| `02_the_2026_story.ipynb` | National totals, 12-candidate round-1 table, state round-2 shares (Lula won 17 of 27 states), runoff-history table 1989–2026. Charts: `charts/02_rounds.png`, `charts/02_state_share.png`. |
| `03_where_did_the_votes_come_from.ipynb` | Decomposition (see below); Lula gained votes in 98.6% of municipalities, median swing +5.13 points; correlations abstention-drop vs gain 0.052, vs swing 0.083. Charts: `charts/03_decomposition.png`, `charts/03_swing_map.png` (5,537 municipalities mapped), `charts/03_abstention_map.png`. Tables saved: `data/processed/decomposition_2026.csv`, `data/processed/mun_swing_2026.csv`. |
| `04_regions_over_time.ipynb` | PT share / turnout by region 1998–2026; 2026 vs own-history table; 2 state flips (AP, TO); largest move DF +4.54 points. Charts: `charts/04_pt_share_region.png`, `charts/04_turnout_region.png`, `charts/04_2026_vs_history.png`, `charts/04_state_map_2026.png`. |
| `05_the_fraud_claim_test.ipynb` | Breadth, feasibility, concentration, and turnout-consistency tests; extended-hours test explicitly not done (see below). Charts: `charts/05_breadth.png`, `charts/05_turnout_scatter.png`. |

## Headline numbers (all from TSE files, cross-checked)

- Round 1: Lula 53,879,538 (45.16%), Flávio Bolsonaro 56,104,503 (47.03%); eliminated candidates 9,316,747 (top: Cury 3,448,569; Renan Santos 2,675,887; Caiado 2,605,148; Zema 326,488; plus 260,655 for six minor candidates).
- Round 2: Lula 64,256,232 (51.79%), Flávio 59,826,041 (48.21%), margin 4,430,191. Electorate 158,745,502; turnout round 1 78.92%, round 2 80.78%; abstention round 2 19.22%.
- Decomposition: Lula gain 10,376,694; Flávio gain 3,721,538; combined 14,098,232 = eliminated pool 9,316,747 + valid increase 4,781,485 (exactly, by definition of valid votes). Valid increase = turnout increase 2,960,239 + blank/null drop 1,816,000 + 5,246 reconciliation residual (0.04% of combined gain). Lula gain / eliminated pool = 111.4%; minimum from non-eliminated sources = 1,059,947. Proportional-split benchmark = 7,300,795; shortfall vs actual = 3,075,899.
- History validation (PT decisive-round share, computed from TSE files, matches published results): 1998 31.71%, 2002 61.27%, 2006 60.83%, 2010 56.05%, 2014 51.64%, 2018 44.87%, 2022 50.90%.
- Regional 2026 PT shares (decisive round): Northeast 69.37%, North 50.01%, Southeast 47.24%, Center-West 39.99%, South 37.42%. Vs mean 1998–2022: Northeast +4.86, Southeast +0.51, North −1.61, Center-West −2.39, South −5.60. Vs 2022: Southeast +1.51, North +1.03, Center-West +0.20, Northeast +0.03, South −0.73.

## Every dataset used, with its URL

| File used in the build | Source | URL / note |
|---|---|---|
| `votacao_candidato_munzona_<1998,2002,2006,2010,2014,2018,2022,2026>.zip` | TSE open data, candidate votes by municipality/zone | https://cdn.tse.jus.br/estatistica/sead/odsele/votacao_candidato_munzona/votacao_candidato_munzona_<YEAR>.zip — president rows only, from `*_BR.csv` (except 1998, see below). **Deleted after processing to keep the folder reasonable** (2.4 GB total); re-downloadable from these URLs. See `data/raw/PROVENANCE.md` for exact sizes. |
| `detalhe_votacao_munzona_<YEAR>.zip` (same years) | TSE open data, turnout details by municipality/zone | https://cdn.tse.jus.br/estatistica/sead/odsele/detalhe_votacao_munzona/detalhe_votacao_munzona_<YEAR>.zip — kept in `data/raw/` (small, ~3–4 MB each). President rows only (`*_BR.csv`, filtered to CD_CARGO=1). |
| `br_municipalities_geojson.json` | Public IBGE-derived mirror `tbrugz/geodata-br` | https://raw.githubusercontent.com/tbrugz/geodata-br/master/geojson/geojs-100-mun.json — 5,564 municipalities, `id` = 7-digit IBGE code. Kept in `data/raw/`. See "Substitutions" for why the official IBGE file/API was not used. |
| Runoff-history leads 2002–2022 (23.2, 7.0, 14.3, 8.0, 16.8, 5.2 points) and 2026 lead 1.9 points | TSE-based series reproduced pre-election | https://forecast.lemillenaire.org/en/brazil/presidential/2026/ ("Benchmarks: runoffs since 2002", source: Superior Electoral Court). Cross-checked against the TSE files for 2026 (lead 1.87 points from 56,104,503 vs 53,879,538 over valid votes). |
| 1989 first-round shares (Collor 30.48%, Lula 17.19%) | TSE / published record | 1989 Brazilian presidential election record (Wikipedia/TSE figures, cross-checked in build research). Used only for the national runoff-history table; 1989 is not in the regional series. |

## Failures, approximations, substitutions, and honest corrections

1. **Live-results JSON feed not used.** The guessed URL pattern for `resultados.tse.jus.br` (election 6258, round 2) returned `NoSuchKey` from the TSE results bucket. The project therefore uses the TSE open-data ZIPs, which are the same official data — verified by exact reproduction of all four headline national totals (both candidates, both rounds, to the vote).
2. **tatipara repo uses ZIPs, not JSON.** Reading `tatipara/eleicao_2026_1turno` (Colab notebooks, TSE data by municipality/zone) showed it also uses TSE CDN ZIPs (`eleitorado_*` / `votacao_secao_*` series), not the live-results JSON. This project's ZIP approach follows that precedent.
3. **The `*_BRASIL.csv` trap (would have double-counted everything).** Each TSE ZIP contains a `*_BRASIL.csv` file (3.2 GB uncompressed in 2026) duplicating every office, including president rows already in `*_BR.csv`. It was excluded in `scripts/build_processed.py`. State files contain no president rows; president votes live only in `*_BR.csv` (except 1998, below).
4. **The leading-zero trap (would have silently dropped turnout data).** TSE municipality codes are zero-padded in turnout files (`01066`) but not in votes files (`1066`). Both were normalised to the unpadded form before merging. Without this, the first build produced a wrong electorate (141.8M instead of 158.7M) and wrong turnout; after normalisation, turnout round 2 is exactly 80.78%, matching the reported figure.
5. **1998 is structurally different.** The 1998 ZIP has no `*_BR.csv`; president rows live only in `*_BRASIL.csv` (723 MB uncompressed), read in chunks with only president rows kept. Its `QT_VOTOS_NOMINAIS` column is all zeros; the real count is `QT_VOTOS_NOMINAIS_VALIDOS` (verified from the file's first rows: e.g. Ciro Gomes 173 valid votes in Acrelândia zone 8 vs 0 in the nominal column). The build uses the valid column for 1998 only. Result validates: FHC 35,936,382 (53.06%), Lula 21,475,211 (31.71%).
6. **TSE codes are not IBGE codes.** Join to shapes is by state + normalised name (accents stripped, upper-cased), not by code. 5,537 of 5,571 domestic municipalities matched; 34 unmatched are kept in CSVs and excluded from municipality maps only. Overseas locations (`ZZ`, 186) have no shape and are excluded from maps but included in national totals.
7. **IBGE official shapes/API not used.** The official municipality shapefile (`BR_Municipios_2022.zip`) is 203 MB and was not downloaded, to keep the folder reasonable. IBGE's Malhas API (`servicodados.ibge.gov.br`) was unreachable from the build machine (proxy tunnel established, then no response). Substitution: the `tbrugz/geodata-br` GeoJSON mirror (IBGE-derived, public). State-map dissolving of that file fails on invalid geometry (TopologyException), so Chapter 4 colours municipalities by their state's share instead of dissolving — visually a state choropleth, and exact.
8. **2010 has a `VT` code.** The 2010 history file contains `VT` (voto em trânsito, in-transit votes) in addition to the 27 states and `ZZ`. Chapter 4 filters explicitly to the 27 states, so `VT` cannot leak into state/region analysis. (Its region is unmapped, so vote-weighted region groupings would have dropped it anyway; the explicit filter removes all doubt.)
9. **Turnout correlation corrected during the build.** The first draft of Chapter 5 described the municipality abstention-drop correlation as "substantial". The computed values are 0.052 (vs Lula vote gain) and 0.083 (vs share swing) — weak. Chapter 5 was corrected to "weak / mixed" before delivery, and the final balance table says so. Similarly, the 99.9% share-rise figure is flagged as partly mechanical (eliminated votes leave the round-2 denominator); the 98.6% vote-gain figure is presented as the stronger breadth signal.
10. **Residual clarified during the build.** The first draft described "a few thousand votes" as the residual of the combined-gain identity. In fact that identity holds exactly (0) by definition of valid votes; the 5,246-vote gap (0.04% of combined gain) is in the second reconciliation (turnout increase + blank/null drop vs valid increase). Chapter 3 now prints both explicitly.
11. **Environment note.** The working virtualenv lives outside the repo at `~/.venvs/elections` (pandas 3.1.0, geopandas 1.2.0, matplotlib 3.11.2, Python 3.12), following the previous build's convention because `/tmp` is a 512 MB tmpfs. The repo itself contains no virtualenv. On Colab, each notebook's first cell installs what it needs.

## What was cut and why

- **2022 Census demographic overlays** (income, race, education, urbanisation by municipality): cut. IBGE SIDRA/Malhas APIs were unreachable from the build machine, and no key-free bulk CSV mirror of municipality-level 2022 Census demographics was found in scope. No demographic claim appears anywhere in the project.
- **Extended-hours regional comparison**: cut, not faked. The TSE files used contain no voting-hours or extension-region field, and no public municipality-level extension list was found in them. Chapter 5 states this plainly and presents no extended-vs-others comparison.
- **1989/1994 regional series**: cut by data availability. The TSE municipality/zone series used starts in 1998, so Chapter 4 starts in 1998. The national runoff-history table (Chapter 2) covers 1989–2026.
- **Raw votacao ZIPs deleted after processing**: cut for size (2.4 GB total). Processed CSVs, the build script, and the exact download URLs in `data/raw/PROVENANCE.md` reproduce them. Detalhe ZIPs and the GeoJSON were kept.

## What still needs the user

**Nothing except a publishing decision, if one is ever wanted.** This build was explicitly local-only: no GitHub repo was created, nothing was pushed, and nothing was posted. If publishing is wanted later, it needs the user's explicit go-ahead and a way to create the repo — the folder is ready as-is (no virtualenv inside, `.gitignore` excludes large raw files), but the raw votacao ZIPs would need re-downloading first if a fully reproducible published repo is wanted.
