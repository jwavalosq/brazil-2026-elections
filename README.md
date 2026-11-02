# Brazil 2026: The Comeback, How Lula Won the Runoff, and What the Data Says About the Fraud Claims

**Flávio Bolsonaro led the first round. Lula won the runoff. That had never happened before in Brazil's post-1989 democracy, and it did not require inventing a single vote to explain.**

This is a data story told in six chapters, written for anyone, no background in politics, statistics, or code needed. Every concept is explained in plain words before it is used, and every chart is computed from public TSE (Superior Electoral Court) data.

> **About the dispute, up front.** Flávio Bolsonaro refused to concede after the runoff, alleged fraud over a Supreme Court judge's last-minute order extending voting by two hours in certain regions, pledged to seek annulment, and then fled to Miami on October 28, 2026, after a passport-surrender order. The electoral court (TSE), foreign governments, and his own party (PL) accepted the result. **The TSE count is the source of truth in this project.** The contestation is labelled wherever results are shown, never hidden, and never treated, by itself, as proof of fraud *or* proof of cleanliness. Chapter 5 tests only what aggregate data can actually test, and says plainly what it cannot test.

## The story in one paragraph

Brazil elects its president in two rounds: if nobody passes 50% of valid votes in round 1, the top two go to a runoff. On October 4, 2026, Flávio Bolsonaro led Lula by about 2 million votes (47.03% vs 45.16%). Three weeks later, on October 25, Lula won with 51.79% (64,256,232 votes) to Flávio's 48.21% (59,826,041), a margin of 4,430,191. At 81, Lula won a fourth term, and became the first candidate since 1989 to finish second in round 1 and win the runoff. This project asks where his extra ~10.4 million votes came from, how each region behaved compared with its own history since 1998, and what the data can and cannot say about the fraud claim.

## The six chapters

| Notebook | Chapter | What you will learn |
|---|---|---|
| `notebooks/00_setup.ipynb` | Setup | Project structure, tools, and where every dataset comes from, with verification |
| `notebooks/01_two_rounds_toy.ipynb` | The toy example | How a two-round system works, with 100 toy voters: transfer + turnout alone can flip a result |
| `notebooks/02_the_2026_story.ipynb` | The 2026 story | The national result, round 1 vs round 2, turnout, and the historic first |
| `notebooks/03_where_did_the_votes_come_from.ipynb` | **The core innovation** | Decomposing Lula's ~10 million extra votes, with honest uncertainty and municipality maps |
| `notebooks/04_regions_over_time.ipynb` | Regions over time | How each region and state behaved from 1998 to 2026, and which moved most in 2026 |
| `notebooks/05_the_fraud_claim_test.ipynb` | The fraud-claim test | The exact claim, four tests the data can do, one test it cannot do, and what remains unproven |

## How to run it

**Option A, Google Colab (recommended, free, nothing to install on your computer):**
1. Upload or clone this folder, open any notebook in Colab.
2. Run the first cell, it installs everything the notebook needs.
3. Run the rest of the cells top to bottom.

**Option B, On your own computer:**
```bash
pip install -r requirements.txt
jupyter notebook notebooks/
```

All notebooks were executed end to end locally with zero cell errors (see `BUILD_REPORT.md`).

## What the data shows, the headline findings

### The comeback, in arithmetic (Chapter 3)

- Lula gained **+10,376,694** votes between rounds; Flávio gained +3,721,538. Together: +14,098,232.
- Eliminated candidates' round-1 votes: **9,316,747**. Valid-vote increase: +4,781,485 (turnout +2,960,239, blank/null drop 1,816,000, plus a 5,246-vote reconciliation residual).
- Combined gains = eliminated pool + valid-vote increase, exactly. The comeback is fully covered, in aggregate, by those pools.
- **But eliminated votes alone cannot explain Lula's gain:** his gain is **111.4%** of the whole eliminated pool, so at least **1,059,947** votes must have come from new voters, round-1 blank/null voters choosing a candidate, or Flávio switchers. Aggregate data cannot split that remainder, and this project does not pretend to.
- Benchmark, not estimate: if transfer and new voters had split like the round-2 result itself (51.79/48.21), Lula would have gained only ~7.30 million. He actually gained 10.38 million, so transfer/new voters leaned Lula more than the round-2 average.
- Breadth: Lula gained votes in **98.6%** of municipalities (5,491 of 5,571); median municipality swing +5.13 points. His vote *share* rose in 99.9% of municipalities, but that figure is partly mechanical (eliminated votes leave the round-2 denominator), the vote-gain figure is the stronger signal, and Chapter 5 says so.

### Regions over time (Chapter 4)

- The Northeast remains the PT's strongest region (69.37% in 2026, essentially unchanged from 69.34% in 2022) and is the region furthest **above** its own 1998–2022 mean (+4.86 points).
- The South is the weakest (37.42%) and furthest **below** its own mean (−5.60 points). The Southeast rose most versus 2022 (+1.51 points, to 47.24%); the North rose to 50.01%; the Center-West was flat (39.99%).
- Only **2 states flipped** between 2022 and 2026 (PT win/loss status): Amapá to the PT (48.6% → 52.9%) and Tocantins away from the PT (51.4% → 48.6%). The largest single-state move was the Federal District (+4.54 points, still a PT loss).
- Turnout in 2026 (80.78% nationally in round 2) is high but within the historical range; it is not off the chart.

### The fraud-claim test, honestly (Chapter 5)

| What was tested | Result |
|---|---|
| Was the gain broad across municipalities and regions? | Yes, most municipalities, all five regions |
| Was the gain arithmetically possible from eliminated votes + new valid votes? | Yes, pools cover the gains exactly |
| Was the gain concentrated in a few big places? | No dramatic concentration, top 100 municipalities: 45.2% of gains vs 38.7% of electorate, modestly above, not a multiple |
| Did gains track where turnout rose? | Only weakly, correlations 0.05 (votes) and 0.08 (share); aggregate turnout rose, but local geography does not strongly predict gains |
| Did extended-hours regions behave differently? | **Cannot be tested from these files**, TSE files contain no voting-hours or extension field, so no such comparison is presented |

**What this does and does not prove.** The comeback adds up, happened almost everywhere rather than in a few places, and looks like what happens when millions of voters have to choose again and millions more show up. But vote totals alone cannot prove an election was clean, and they cannot prove fraud either, small-scale or local irregularities would not necessarily move national totals, and the specific two-hour-extension question cannot even be tested from these files. Both over-claims ("the data proves it was clean" and "the data proves it was fraud") go beyond what municipality totals can say, and this project makes neither.

## A warning about the decomposition, read before quoting it

Chapter 3 estimates flows from **aggregate data**: totals per municipality, not individual voters. It can prove what was arithmetically possible and impossible, and it can give bounds. It **cannot** track individual voters, and it does not claim to know how any particular person voted. Any exact split of Lula's gain into "X votes from candidate Y's voters" would be a guess, not a measurement, you will not find one here.

## Data sources (all public and free, no key, no login)

- **TSE open data**, candidate votes by municipality/zone (`votacao_candidato_munzona`) and turnout details (`detalhe_votacao_munzona`), 1998–2026: https://cdn.tse.jus.br/estatistica/sead/odsele/ and https://dadosabertos.tse.jus.br/dataset/resultados-2026
- **Municipality shapes**, IBGE-derived GeoJSON mirror `tbrugz/geodata-br` (`geojs-100-mun.json`), used because IBGE's own Malhas API was unreachable from the build machine and the official shapefile is 203 MB (see `BUILD_REPORT.md`)
- **Runoff-history cross-checks**, TSE national results; 2002–2022 round-1 leads via the TSE-based series reproduced in the pre-election runoff analysis cited in `BUILD_REPORT.md`; 1989 first-round shares (Collor 30.48% vs Lula 17.19%)

See `BUILD_REPORT.md` for exactly which files were used, what ran, what failed or was approximated, and what was cut and why. See `data/raw/PROVENANCE.md` for the per-file source list.

## What was cut, honestly

- **2022 Census demographic overlays** (income, race, education, urbanisation): cut, IBGE's SIDRA/Malhas APIs were unreachable from the build machine and no key-free bulk mirror was found in scope. Maps show votes only.
- **Extended-hours regional comparison**: cut, no extension field exists in the TSE files used; inventing the cut would be fabricating the test.
- **1989/1994 in the regional series**: the TSE municipality/zone series starts in 1998, so Chapter 4 starts in 1998. The national runoff-history table (Chapter 2) covers 1989–2026.

## License and honesty note

All data used here is public. No numbers in this project are invented: every chart is computed from the datasets above, and anything that could not be reproduced is documented in `BUILD_REPORT.md`. This project was built locally only, nothing was published, pushed, posted, or signed in to anywhere.
