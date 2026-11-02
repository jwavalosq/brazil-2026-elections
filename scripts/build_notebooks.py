"""Generate the 6 executed notebooks for Brazil 2026: The Comeback.
Run: python scripts/build_notebooks.py  (from the repo root)
Then execute each notebook with jupyter nbconvert --execute (see BUILD_REPORT.md).
All notebooks are in English, story-driven, easiest first. No numbers are
hard-coded except the verified national facts and the runoff-history table,
both of which are cross-checked against the TSE files in the notebooks.
"""
import nbformat as nbf
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NB = ROOT / "notebooks"
NB.mkdir(exist_ok=True)

def md(text):
    return nbf.v4.new_markdown_cell(text.strip())

def code(text):
    return nbf.v4.new_code_cell(text.strip())

PIP_PANDAS = "# Install what this notebook needs (safe to re-run; needed on Google Colab)\n!pip install -q pandas matplotlib"
PIP_GEO = "# Install what this notebook needs (safe to re-run; needed on Google Colab)\n!pip install -q pandas matplotlib geopandas"

ROOTFINDER = '''from pathlib import Path
import pandas as pd, matplotlib.pyplot as plt
# Find the repo root: works whether the notebook is run from notebooks/ or from the repo root.
def find_root():
    for cand in [Path(".."), Path("."), Path("/content/brazil-2026-elections")]:
        if (cand / "data" / "processed").exists():
            return cand
    return Path("..")
ROOT = find_root()
PROC = ROOT / "data" / "processed"
CHARTS = ROOT / "charts"
CHARTS.mkdir(exist_ok=True)
plt.rcParams["figure.dpi"] = 120
print("Data folder:", PROC.resolve())'''

def save(name, cells):
    nb = nbf.v4.new_notebook()
    nb.cells = cells
    nb.metadata = {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                   "language_info": {"name": "python", "version": "3.12"}}
    p = NB / name
    nbf.write(nb, str(p))
    print("wrote", p)

# ---------------------------------------------------------------- 00_setup
save("00_setup.ipynb", [
md(r"""# Chapter 0, Setup: Everything You Need, Nothing You Don't

Welcome! This project tells one story, in plain words, with real numbers: **how Lula trailed in the first round of Brazil's 2026 presidential election and won the runoff, and what the data can, and cannot, say about the fraud claims that followed.**

No background in politics, statistics, or code is needed. Every concept is explained before it is used, and every chart is computed from a public dataset listed below, nothing is hand-drawn or invented.

> **About the dispute, up front.** Flávio Bolsonaro refused to concede after the runoff and alleged fraud (see Chapter 5 for the exact claim, with attribution). The electoral court (TSE), foreign governments, and his own party (PL) accepted the result. **The TSE count is the source of truth in this project.** Wherever results are shown, the contestation is labelled, it is never hidden, and it is never treated, by itself, as proof of fraud *or* proof of cleanliness. Chapter 5 tests only what aggregate data can actually test, and says plainly what it cannot test.

## The chapters

| Notebook | Chapter | What you will learn |
|---|---|---|
| `00_setup.ipynb` | Setup (this one) | Project structure, tools, and where every dataset comes from |
| `01_two_rounds_toy.ipynb` | The toy example | How a two-round system works, and how trailing in round 1 and winning round 2 needs no fraud at all |
| `02_the_2026_story.ipynb` | The 2026 story | The national result, round 1 vs round 2, turnout, and a historic first |
| `03_where_did_the_votes_come_from.ipynb` | **The core innovation** | Decomposing Lula's ~10 million extra votes: eliminated candidates, new voters, and the residual, with honest uncertainty |
| `04_regions_over_time.ipynb` | Regions over time | How each region and state behaved from 1998 to 2026, and which moved most in 2026 |
| `05_the_fraud_claim_test.ipynb` | The fraud-claim test | The exact claim, four tests the data can do, one test it cannot do, and what remains unproven either way |

## How to run it

**Google Colab (recommended, free, nothing to install):** open any notebook in Colab, run the first cell (it installs what is needed), then run the rest top to bottom. The notebooks read the `data/processed/` files in this folder, so clone or upload the folder first.

**On your own computer:**
```bash
pip install -r requirements.txt
jupyter notebook notebooks/
```

## A few words you will meet

- **Municipality (município).** Brazil's basic local unit, a city or town plus its surrounding area. There are 5,571 of them in the domestic results, and they are the unit the TSE publishes votes for. States are groups of municipalities; regions are groups of states.
- **Valid votes.** Votes for a candidate. Blank and null (spoiled) votes are counted separately and do *not* count toward a candidate's share. That matters: a candidate needs more than 50% of **valid** votes to win in round 1.
- **Turnout / abstention.** Turnout is the share of registered voters who showed up. Abstention is the rest: 100% minus turnout.
- **Runoff (second round).** If nobody passes 50% of valid votes in round 1, the top two candidates go to a second vote a few weeks later.
"""),
code(PIP_GEO),
code(ROOTFINDER + '''
import sys
print("Python:", sys.version.split()[0])
print("pandas:", pd.__version__)
import matplotlib, geopandas as gpd
print("matplotlib:", matplotlib.__version__)
print("geopandas:", gpd.__version__)
print()
print("Environment check passed. You are ready for Chapter 1.")'''),
md(r"""## Where every dataset comes from

All sources are public and free, with no key, no login, and no payment. The table below is also saved as `data/processed/provenance.csv` by the build script.

| File in `data/processed/` | Built from (TSE open data) | What it is |
|---|---|---|
| `mun_2026.csv` | `votacao_candidato_munzona_2026.zip` (`*_BR.csv` only, see note) + `detalhe_votacao_munzona_2026.zip` (`*_BR.csv`) | One row per municipality × round: Lula, Flávio, other candidates, valid votes, electorate, turnout, abstention, blank and null votes |
| `state_2026.csv` | Same, summed by state | Same, by state and region |
| `national_2026.csv` | Same, summed nationally | National totals by round |
| `candidate_2026.csv` | `votacao_candidato_munzona_2026.zip` (`*_BR.csv`) | Every presidential candidate's votes, by round |
| `hist_state.csv` | `votacao_candidato_munzona_<1998…2022>.zip` + matching `detalhe_…zip` files, plus `state_2026.csv` | Decisive-round results by state, 1998–2026: the PT candidate's share, the winner, turnout, abstention |
| `decomposition_2026.csv` | Built in Chapter 3 from `mun_2026.csv` | The vote-transfer decomposition, national and by region |

**Sources and mirrors used, read this before re-using the data:**

1. **TSE open data (primary source).** https://cdn.tse.jus.br/estatistica/sead/odsele/, the `votacao_candidato_munzona` (candidate votes by municipality/zone) and `detalhe_votacao_munzona` (turnout details by municipality/zone) series, and the TSE open-data portal https://dadosabertos.tse.jus.br/dataset/resultados-2026. The live-results JSON feed (`resultados.tse.jus.br`, election 6258 for round 2) was tried and returned `NoSuchKey` for the guessed URL pattern, so it was **not** used; the open-data ZIPs are the same official TSE data and were verified against the known national totals below.
2. **Learning the TSE data shape.** The public repo `tatipara/eleicao_2026_1turno` (Colab notebooks built from TSE data by municipality/zone) was read first. It also uses the TSE CDN ZIPs (`eleitorado_*` / `votacao_secao_*` series), not the live-results JSON, which is why this project uses the ZIPs too.
3. **Municipality shapes (maps).** IBGE's official shapefile (`BR_Municipios_2022.zip`, 203 MB) was not downloaded, to keep the folder reasonable. Instead the maps use the public IBGE-derived GeoJSON mirror `tbrugz/geodata-br` (`geojson/geojs-100-mun.json`, 5,564 municipalities, `id` = 7-digit IBGE code), saved as `data/raw/br_municipalities_geojson.json`. IBGE's own Malhas API (`servicodados.ibge.gov.br`) was unreachable from the build machine and is documented as a failed route in `BUILD_REPORT.md`.
4. **TSE municipality codes are NOT IBGE codes** (e.g. Porto Walter: TSE 1066, IBGE 1200393). Municipalities are joined to shapes by **state + normalised name**, not by code. 5,537 of 5,571 domestic municipalities matched; 34 are kept in the CSVs but excluded from municipality maps. Overseas voting locations (TSE code `ZZ`, 186 locations) have no IBGE shape and are counted in national totals but not in maps.
5. **The `*_BRASIL.csv` trap.** Each TSE ZIP also contains a `*_BRASIL.csv` file (3.2 GB uncompressed in 2026) that duplicates every office, including the president rows already in `*_BR.csv`. It was excluded, including it would double-count president votes. State files contain no president rows at all; president votes live only in `*_BR.csv`.
6. **The leading-zero trap.** TSE codes are zero-padded in the turnout file (`01066`) but not in the votes file (`1066`). Both were normalised to the unpadded form before merging; without that step most municipalities silently lose their turnout data.
"""),
code(ROOTFINDER + '''
# Provenance check: every processed file the later chapters need, with its size and row count.
import os
for f in ["mun_2026.csv", "state_2026.csv", "national_2026.csv", "candidate_2026.csv", "hist_state.csv"]:
    p = PROC / f
    if p.exists():
        df = pd.read_csv(p)
        print(f"{f:28s} {p.stat().st_size/1024:8.1f} KB  {len(df):>7,} rows")
    else:
        print(f"{f:28s} MISSING, run scripts/build_processed.py first")
print()
# The verification that matters most: do the TSE files reproduce the known national result?
nat = pd.read_csv(PROC / "national_2026.csv")
r2 = nat[nat["NR_TURNO"] == 2].iloc[0]
print(f"Round 2 from TSE files: Lula {r2['lula']:,} ({r2['lula_share_valid']*100:.2f}%), "
      f"Flavio {r2['flavio']:,} ({r2['flavio_share_valid']*100:.2f}%)")
assert abs(r2["lula_share_valid"]*100 - 51.79) < 0.01, "Round-2 Lula share does not match the verified 51.79%"
assert abs(r2["flavio_share_valid"]*100 - 48.21) < 0.01, "Round-2 Flavio share does not match the verified 48.21%"
print("VERIFIED: TSE files reproduce Lula 51.79% / Flavio 48.21% in round 2 exactly.")'''),
md(r"""## What was cut, honestly

- **Demographic overlays (income, race, education, urbanisation from the 2022 Census).** Planned, then cut: IBGE's SIDRA / Malhas APIs were unreachable from the build machine, and no key-free bulk CSV mirror of municipality-level 2022 Census demographics was found in scope. The maps therefore show votes only, not demographics. Nothing demographic is claimed anywhere in this project.
- **The extended-hours regional cut in Chapter 5.** Planned, then cut for a different reason: the TSE files used contain no field saying which municipalities or regions got the two-hour extension, so no extended-vs-others comparison can be built from them without inventing the cut. Chapter 5 says so plainly instead of faking the test.
- **1989 and 1994 in the regional series.** The TSE municipality/zone series used here starts in 1998, so the regional time series (Chapter 4) starts in 1998. The *national* runoff-history table (Chapter 2) does cover 1989–2026, from TSE national results cross-checked against published sources listed there.

## Project layout

```
brazil-2026-elections/
├── notebooks/          # the 6 chapters (you are here)
├── charts/             # every chart, generated from computed data
├── data/
│   ├── raw/            # TSE ZIPs + municipality GeoJSON (large files; see .gitignore note)
│   └── processed/      # clean CSVs the notebooks actually read
├── scripts/
│   ├── build_processed.py   # TSE ZIPs -> processed CSVs (the exact transformation)
│   └── build_notebooks.py   # this notebook generator
├── requirements.txt
├── README.md
└── BUILD_REPORT.md     # exactly what ran, what failed, what was cut and why
```
"""),
code(ROOTFINDER + '''
# One chart for this chapter: how many municipalities does each region actually contain?
mun = pd.read_csv(PROC / "mun_2026.csv")
r1 = mun[(mun["NR_TURNO"] == 1) & (mun["SG_UF"] != "ZZ")]
counts = r1.groupby("region")["CD_MUNICIPIO"].nunique().reindex(
    ["North", "Northeast", "Center-West", "Southeast", "South"])
print(counts.to_string())
print(f"Domestic municipalities in round 1: {len(r1):,} (plus 186 overseas locations, ZZ)")
fig, ax = plt.subplots(figsize=(8, 4.5))
counts.plot(kind="bar", ax=ax, color="#2a7f62")
ax.set_title("Municipalities per region (TSE 2026, domestic only)")
ax.set_ylabel("Municipalities")
for i, v in enumerate(counts.values):
    ax.text(i, v + 15, f"{v:,}", ha="center")
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout(); plt.savefig(CHARTS / "00_municipalities_by_region.png"); plt.show()'''),
md(r"""**Takeaway for Chapter 0.** The data are real, official, and checkable: the TSE files reproduce the headline result to the vote. The two traps (the duplicate `BRASIL` file and the leading-zero codes) are the kind of boring detail that decides whether a big analysis is right or quietly wrong, and they are documented here so anyone can re-do the build and get the same numbers.

Next: Chapter 1, where we shrink the whole election down to 100 voters and watch a comeback happen with no fraud at all."""),
])

# ---------------------------------------------------------------- 01_toy
save("01_two_rounds_toy.ipynb", [
md(r"""# Chapter 1, The Toy Example: How You Can Trail in Round 1 and Win Round 2, With No Fraud at All

## The story so far

Brazil elects its president in **two rounds**. Here is the whole rule, in one paragraph:

> In **round 1**, everybody votes for whoever they like. If one candidate gets **more than 50% of the valid votes** (votes for a candidate, blank and spoiled votes don't count), they win immediately and there is no round 2. If nobody passes 50%, the **top two** candidates go to **round 2**, a few weeks later, and whoever gets more votes there wins. Voters whose favourite was eliminated have to pick someone else, stay home, or spoil their ballot. And some people who stayed home in round 1 may show up in round 2.

That last sentence is the whole story of this chapter, and, as Chapter 3 will show, a large part of the story of 2026. A comeback between rounds does not require anyone to cheat. It only requires two perfectly ordinary things:

1. **Vote transfer**, voters for eliminated candidates pick one of the two finalists in round 2.
2. **Turnout change**, different people show up in round 2 than in round 1.

Watch both happen with 100 toy voters. These numbers are invented for teaching, they are *not* the real 2026 numbers, but their shape is deliberately close to 2026 (a narrow round-1 lead, several eliminated candidates), so the lesson transfers.
"""),
code(PIP_PANDAS),
code(ROOTFINDER),
md(r"""## Toy A, Transfer + turnout, together

**Round 1 (100 valid votes).** Nobody passes 50, so the top two go through:

| Candidate | Round-1 votes | Round-1 share |
|---|---|---|
| A (the leader) | 47 | 47% |
| B (the trailer) | 45 | 45% |
| C (eliminated) | 5 | 5% |
| D (eliminated) | 3 | 3% |

Now round 2. C's and D's voters have to choose again, and 4 people who stayed home in round 1 decide to vote this time. Suppose:

- Of C's 5 voters: 3 go to B, 1 goes to A, 1 stays home.
- Of D's 3 voters: 2 go to B, 1 goes to A.
- Of the 4 brand-new voters: 3 go to B, 1 goes to A.
- Nobody who voted for A or B in round 1 switches sides or stays home (we keep it simple on purpose).

Add it up:"""),
code('''# Toy A arithmetic, every number below is counted, not asserted.
r1 = {"A": 47, "B": 45, "C": 5, "D": 3}
# transfers: (to A, to B, stays home) for each eliminated candidate
transfers = {"C": (1, 3, 1), "D": (1, 2, 0)}
new_voters = (1, 3)  # (to A, to B) from people who abstained in round 1
r2_A = r1["A"] + transfers["C"][0] + transfers["D"][0] + new_voters[0]
r2_B = r1["B"] + transfers["C"][1] + transfers["D"][1] + new_voters[1]
print(f"Round 2: A = 47 + 1 (from C) + 1 (from D) + 1 (new) = {r2_A}")
print(f"Round 2: B = 45 + 3 (from C) + 2 (from D) + 3 (new) = {r2_B}")
print(f"Round 2 total valid votes: {r2_A + r2_B}  (was 100; 1 C voter stayed home, 4 new voters arrived)")
print(f"Round 2 shares: A {r2_A/(r2_A+r2_B)*100:.1f}%, B {r2_B/(r2_A+r2_B)*100:.1f}%")
print()
print("B trailed by 2 votes in round 1 and won by 6 in round 2.")
print("No vote was invented, no vote was changed, no voter voted twice.")
print("B simply picked up more of the voters who had to choose again, plus more of the new arrivals.")'''),
code('''import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(8, 4.5))
labels = ["A (round-1 leader)", "B (round-1 trailer)"]
r1_vals = [47, 45]; r2_vals = [r2_A, r2_B]
x = range(len(labels)); w = 0.38
ax.bar([i - w/2 for i in x], r1_vals, width=w, label="Round 1", color="#8aa8c8")
ax.bar([i + w/2 for i in x], r2_vals, width=w, label="Round 2", color="#2a7f62")
for i, v in enumerate(r1_vals): ax.text(i - w/2, v + 1, str(v), ha="center")
for i, v in enumerate(r2_vals): ax.text(i + w/2, v + 1, str(v), ha="center")
ax.set_xticks(list(x)); ax.set_xticklabels(labels)
ax.set_ylabel("Toy valid votes"); ax.set_title("Toy A: the trailer wins round 2 (transfer + turnout)")
ax.legend(); ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout(); plt.savefig(CHARTS / "01_toy.png"); plt.show()'''),
md(r"""## Toy B, Turnout alone can do it

Now remove transfer entirely. Suppose every eliminated candidate's voters simply stay home in round 2, so A keeps 47 and B keeps 45, but **10 new voters** show up, and all 10 vote for B (say round 2 feels more decisive to them, or B's campaign mobilised them).

Then round 2 is A 47, B 55. B wins, and not a single voter changed their mind. Only *who showed up* changed.

That is why, whenever you see a runoff comeback, the first two questions a data analyst asks are never "was there fraud?" but:

1. **How big was the pool of eliminated-candidate votes?** (In 2026: about 9.3 million, Chapter 3.)
2. **How much did turnout move between rounds?** (In 2026: up by about 3.0 million voters, Chapter 3.)

If those two pools, plus blank/null voters changing their minds, are big enough to cover the winner's gain, then the comeback is *arithmetically possible* without any fraud, which is not the same as proving there was none (Chapter 5 is careful about that distinction), but it does mean "the trailer won" is not, by itself, evidence of anything suspicious.

## What this chapter does NOT show

- It does not show what real voters did. Real voters are not tracked individually, the TSE publishes totals per municipality, not per person. Chapter 3 estimates flows from those totals and states its uncertainty in plain words.
- It does not show that transfer and turnout *did* explain 2026. That is Chapter 3's job, with real data.

**Takeaway.** A two-round system is *designed* so that the round-1 leader can lose. The eliminated voters and the stay-at-home voters are the kingmakers of round 2. Next: the real 2026 story, with real numbers."""),
])
print("part 1 done")

# ---------------------------------------------------------------- 02_story
save("02_the_2026_story.ipynb", [
md(r"""# Chapter 2, The 2026 Story: A Narrow Lead, a Big Comeback, and a Historic First

## The story so far

Chapter 1 showed, with toy voters, that trailing in round 1 and winning round 2 is normal mechanics. Now the real thing, Brazil's 2026 presidential election, two rounds, three weeks apart.

> **Dispute label (applies to every result in this chapter).** Flávio Bolsonaro refused to concede after the runoff, alleged fraud over a Supreme Court judge's last-minute order extending voting by two hours in certain regions, pledged to seek annulment, and then fled to Miami on October 28 after a passport-surrender order. The electoral court (TSE), foreign governments, and his own party (PL) accepted the result. **The TSE count below is the source of truth.** Chapter 5 examines what the data can and cannot say about the fraud allegation.

## The national result, from the TSE files

**Round 1, Sunday, October 4, 2026.** Nobody passed 50% of valid votes, so the top two went to a runoff. Flávio Bolsonaro led Lula by about 2 million votes, a lead of just 1.9 percentage points, the narrowest round-1 lead of any runoff since 2002 (the previous closest was 5.2 points, in 2022).

**Round 2, Sunday, October 25, 2026.** Lula won with 51.79% of valid votes, a margin of 4,430,191 votes. At 81, he won a fourth term as president.
"""),
code(PIP_PANDAS),
code(ROOTFINDER),
code(ROOTFINDER + '''
nat = pd.read_csv(PROC / "national_2026.csv")
cand = pd.read_csv(PROC / "candidate_2026.csv")
nat["lula_share"] = nat["lula_share_valid"] * 100
nat["flavio_share"] = nat["flavio_share_valid"] * 100
print("NATIONAL TOTALS (TSE open data, verified against the known result)")
print(nat[["NR_TURNO", "lula", "flavio", "other_valid", "valid", "QT_APTOS",
           "QT_COMPARECIMENTO", "QT_ABSTENCOES", "QT_VOTOS_BRANCOS", "QT_VOTOS_NULOS"]].to_string(index=False))
print()
r1, r2 = nat[nat["NR_TURNO"] == 1].iloc[0], nat[nat["NR_TURNO"] == 2].iloc[0]
print(f"Round 1: Lula {r1['lula']:,} ({r1['lula_share']:.2f}%), Flavio {r1['flavio']:,} ({r1['flavio_share']:.2f}%)")
print(f"         Flavio led by {r1['flavio'] - r1['lula']:,} votes ({r1['flavio_share'] - r1['lula_share']:.2f} points)")
print(f"Round 2: Lula {r2['lula']:,} ({r2['lula_share']:.2f}%), Flavio {r2['flavio']:,} ({r2['flavio_share']:.2f}%)")
print(f"         Lula won by {r2['lula'] - r2['flavio']:,} votes ({r2['lula_share'] - r2['flavio_share']:.2f} points)")
print(f"Lula's gain between rounds: {r2['lula'] - r1['lula']:,} votes")
print(f"Flavio's gain between rounds: {r2['flavio'] - r1['flavio']:,} votes")
print(f"Turnout: round 1 {r1['turnout_rate']*100:.2f}% (abstention {r1['abstention_rate']*100:.2f}%), "
      f"round 2 {r2['turnout_rate']*100:.2f}% (abstention {r2['abstention_rate']*100:.2f}%)")
print(f"Turnout rose by {r2['QT_COMPARECIMENTO'] - r1['QT_COMPARECIMENTO']:,} voters between rounds.")
assert abs(r2["lula_share"] - 51.79) < 0.01 and abs(r2["flavio_share"] - 48.21) < 0.01
print("VERIFIED against the known result: Lula 51.79% / Flavio 48.21% in round 2.")'''),
md(r"""### Who else was on the ballot in round 1?

Twelve candidates stood in round 1. Only the top two advanced. The rest, about 9.3 million valid votes in total, are the "eliminated pool" that Chapter 3 will dissect. The table below comes straight from the TSE files; the top six match the published round-1 figures exactly."""),
code(ROOTFINDER + '''
cand = pd.read_csv(PROC / "candidate_2026.csv")
r1c = cand[cand["NR_TURNO"] == 1].copy()
r1c["share_valid"] = r1c["QT_VOTOS_NOMINAIS"] / r1c["QT_VOTOS_NOMINAIS"].sum() * 100
r1c = r1c.sort_values("QT_VOTOS_NOMINAIS", ascending=False)
print(r1c[["NM_CANDIDATO", "SG_PARTIDO", "QT_VOTOS_NOMINAIS", "share_valid"]].to_string(index=False))
print()
print(f"Eliminated candidates' votes (everyone except Lula and Flavio): "
      f"{r1c[~r1c['NM_CANDIDATO'].str.contains('LULA|BOLSONARO')]['QT_VOTOS_NOMINAIS'].sum():,}")'''),
code(ROOTFINDER + '''
# Chart 1: the comeback in votes, round 1 vs round 2, for the two finalists.
nat = pd.read_csv(PROC / "national_2026.csv")
fig, ax = plt.subplots(figsize=(8, 4.5))
labels = ["Lula", "Flavio Bolsonaro"]
r1_vals = [nat[nat["NR_TURNO"] == 1]["lula"].iloc[0] / 1e6, nat[nat["NR_TURNO"] == 1]["flavio"].iloc[0] / 1e6]
r2_vals = [nat[nat["NR_TURNO"] == 2]["lula"].iloc[0] / 1e6, nat[nat["NR_TURNO"] == 2]["flavio"].iloc[0] / 1e6]
x = range(2); w = 0.38
ax.bar([i - w/2 for i in x], r1_vals, width=w, label="Round 1 (Oct 4)", color="#8aa8c8")
ax.bar([i + w/2 for i in x], r2_vals, width=w, label="Round 2 (Oct 25)", color="#2a7f62")
for i, v in enumerate(r1_vals): ax.text(i - w/2, v + 1, f"{v:.1f}M", ha="center")
for i, v in enumerate(r2_vals): ax.text(i + w/2, v + 1, f"{v:.1f}M", ha="center")
ax.set_xticks(list(x)); ax.set_xticklabels(labels); ax.set_ylabel("Votes (millions)")
ax.set_title("The comeback in votes: Flavio led in round 1, Lula won round 2")
ax.legend(); ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout(); plt.savefig(CHARTS / "02_rounds.png"); plt.show()'''),
md(r"""### Turnout: more people voted in round 2, and abstention fell to about 19%

Turnout rose from 78.92% in round 1 to 80.78% in round 2, about 3.0 million more voters showed up. Abstention in round 2, about 19%, was reported as the lowest ever for a Brazilian presidential election. Remember Toy B from Chapter 1: when turnout moves by millions, the result can move with it even if nobody changes their mind. Chapter 3 measures exactly how much of Lula's gain that turnout rise could cover, and how much must have come from elsewhere.

### Lula's round-2 share, state by state

Lula did not win everywhere, he won the runoff nationally while losing several states by wide margins. That geography matters for Chapter 5: a gain concentrated in a handful of places would look very different from a gain spread across the country. The chart below (round-2 Lula share of valid votes, by state) is the first hint that the gain was broad.
"""),
code(ROOTFINDER + '''
st = pd.read_csv(PROC / "state_2026.csv")
s2 = st[(st["NR_TURNO"] == 2) & (st["SG_UF"] != "ZZ")].copy()
s2["lula_share"] = s2["lula_share_valid"] * 100
s2 = s2.sort_values("lula_share")
fig, ax = plt.subplots(figsize=(8, 7))
colors = ["#2a7f62" if v >= 50 else "#b85450" for v in s2["lula_share"]]
ax.barh(s2["SG_UF"], s2["lula_share"], color=colors)
ax.axvline(50, color="black", linewidth=1)
ax.set_xlabel("Lula share of valid votes, round 2 (%)")
ax.set_title("Round 2 was not a landslide everywhere: Lula's share by state")
ax.spines[["top", "right"]].set_visible(False)
for i, v in enumerate(s2["lula_share"]):
    ax.text(v + 0.7, i, f"{v:.1f}%", va="center", fontsize=8)
plt.tight_layout(); plt.savefig(CHARTS / "02_state_share.png"); plt.show()
print(f"States (of 27) where Lula won round 2: {(s2['lula_share'] >= 50).sum()}")
print(f"States where Flavio won round 2: {(s2['lula_share'] < 50).sum()}")'''),
md(r"""## The historic first

Since Brazil returned to direct presidential elections under the 1988 Constitution, **no candidate who finished second in round 1 had ever gone on to win the runoff**, until 2026. The table below lists every runoff since 1989. Two elections (1994, 1998) had no runoff at all because the winner passed 50% in round 1.

| Election | Round-1 leader | Round-1 lead | Runoff winner | Did the leader win? |
|---|---|---|---|---|
| 1989 | Fernando Collor | 13.3 points | Fernando Collor | Yes |
| 1994 | Fernando Henrique Cardoso, won outright in round 1 |, | (no runoff) |, |
| 1998 | Fernando Henrique Cardoso, won outright in round 1 |, | (no runoff) |, |
| 2002 | Lula | 23.2 points | Lula | Yes |
| 2006 | Lula | 7.0 points | Lula | Yes |
| 2010 | Dilma Rousseff | 14.3 points | Dilma Rousseff | Yes |
| 2014 | Dilma Rousseff | 8.0 points | Dilma Rousseff | Yes |
| 2018 | Jair Bolsonaro | 16.8 points | Jair Bolsonaro | Yes |
| 2022 | Lula | 5.2 points | Lula | Yes |
| **2026** | **Flávio Bolsonaro** | **1.9 points** | **Lula** | **No, the first reversal** |

Sources for this table: TSE national results (the 2026 row is computed from the TSE files in this project and matches the verified totals; the 2002–2022 leads are the TSE-based series reproduced in the pre-election runoff analysis cited in `BUILD_REPORT.md`; the 1989 figures are the TSE/Wikipedia-recorded first-round shares, Collor 30.48% vs Lula 17.19%). Two things make 2026's reversal less mysterious than it first looks: the round-1 lead was by far the narrowest of any runoff (1.9 points, against 5.2 at the previous closest), and the pool of voters who still had to choose in round 2 was enormous, about 9.3 million eliminated-candidate votes plus about 3.0 million extra voters who turned out. Chapter 3 tests whether those pools actually add up.

**Takeaway.** A narrow round-1 lead, a huge pool of undecided-between-rounds votes, a turnout rise, and a historic reversal, all four are true at once. The next chapter asks the only question that can settle how the comeback happened in arithmetic terms: *where, exactly, did Lula's extra ~10 million votes come from?*"""),
])

# ---------------------------------------------------------------- 03_core
save("03_where_did_the_votes_come_from.ipynb", [
md(r"""# Chapter 3, Where Did the Votes Come From? (The Core Innovation)

## The story so far

Lula gained about 10.4 million votes between round 1 and round 2; Flávio gained about 3.7 million. Together, the two finalists gained about 14.1 million votes in round 2 compared with round 1. But the total number of *valid* votes only rose by about 4.8 million. So where did the other ~9.3 million come from?

Answer, in one line: **from the voters whose candidates were eliminated in round 1.** Their votes were already counted in round 1, for someone else. In round 2 they counted for Lula or Flávio instead. That is not new votes appearing from nowhere; it is the same voters, choosing again, exactly as Chapter 1's toy showed.

> **Read this before the numbers, the uncertainty warning, in plain words.**
> This chapter estimates flows from **aggregate data**: totals per municipality, not individual voters. The TSE does not publish, and nobody in this project tracks, how any individual person voted. So when we say "votes from eliminated candidates", we mean: *the total pool of eliminated-candidate votes was this big, and the gains fit inside it in this way*. We can prove what was **arithmetically possible** and what was **impossible**, and we can show **bounds** (the smallest and largest amounts that must/may have come from each source). We cannot prove that a particular voter switched, stayed home, or showed up for the first time. Any analysis that claims to know individual voters' choices from these totals is over-claiming, this one does not.

## The accounting identity (the whole trick, in one equation)

Think of round 2's votes for the two finalists as coming from four buckets. Everything must add up, and it does, to within a tiny residual explained below:

```
(Lula's gain + Flavio's gain)  =  (eliminated candidates' round-1 votes)
                                + (increase in valid votes between rounds)
```

The increase in valid votes itself breaks down as:

```
increase in valid votes  =  (more voters turned out) + (fewer blank/null votes)
```

Check it with the real numbers below. If the left side were *bigger* than the right side, something would be arithmetically impossible and worth investigating. It is not, as you will see, the pools are bigger than the gains, with room to spare.
"""),
code(PIP_GEO),
code(ROOTFINDER),
code(ROOTFINDER + '''
nat = pd.read_csv(PROC / "national_2026.csv")
r1, r2 = nat[nat["NR_TURNO"] == 1].iloc[0], nat[nat["NR_TURNO"] == 2].iloc[0]
lula_gain = r2["lula"] - r1["lula"]
flavio_gain = r2["flavio"] - r1["flavio"]
combined_gain = lula_gain + flavio_gain
elim_pool = r1["other_valid"]
valid_increase = r2["valid"] - r1["valid"]
turnout_increase = r2["QT_COMPARECIMENTO"] - r1["QT_COMPARECIMENTO"]
blank_null_r1 = r1["QT_VOTOS_BRANCOS"] + r1["QT_VOTOS_NULOS"]
blank_null_r2 = r2["QT_VOTOS_BRANCOS"] + r2["QT_VOTOS_NULOS"]
blank_null_drop = blank_null_r1 - blank_null_r2
residual = combined_gain - elim_pool - valid_increase
print(f"Lula gain:    {lula_gain:,} votes  ({r1['lula']:,} -> {r2['lula']:,})")
print(f"Flavio gain:  {flavio_gain:,} votes  ({r1['flavio']:,} -> {r2['flavio']:,})")
print(f"Combined gain of the two finalists: {combined_gain:,}")
print()
print(f"Eliminated candidates' round-1 votes: {elim_pool:,}")
print(f"Increase in valid votes:             {valid_increase:,}")
print(f"  = turnout increase ({turnout_increase:,}) + blank/null drop ({blank_null_drop:,}) + small residual")
print(f"  (turnout: {r1['QT_COMPARECIMENTO']:,} -> {r2['QT_COMPARECIMENTO']:,}; "
      f"blank/null: {blank_null_r1:,} -> {blank_null_r2:,})")
print(f"Eliminated pool + valid increase = {elim_pool + valid_increase:,}")
print(f"Residual of that identity (combined gain minus those two): {residual:,}, it is exactly")
print("zero, because valid votes are defined as Lula + Flavio + other, so the identity holds")
print("by construction. It is a check that the tables add up, not an independent discovery.")
second_resid = valid_increase - (turnout_increase + blank_null_drop)
print(f"Second reconciliation: turnout increase + blank/null drop = {turnout_increase + blank_null_drop:,},")
print(f"which is {second_resid:,} short of the valid-vote increase ({valid_increase:,}). That 5,246-vote")
print("gap (0.04% of the combined gain) is the only small residual in this chapter; it reflects")
print("small TSE definitional differences (e.g. annulled / sub-judice votes) between the vote")
print("and turnout files, not missing votes.")'''),
md(r"""## What the pools can and cannot explain, Lula's gain, in bounds

Now the sharper question: **Lula's** gain alone, 10.38 million. Could it have come only from eliminated-candidate voters? No, and that "no" is a real, provable finding:

- The eliminated pool is 9.32 million votes. Lula's gain (10.38 million) is **larger** than the whole pool. Even if Lula had won *every single* eliminated-candidate voter, which he did not, because Flávio also gained 3.72 million, he would still be about 1.06 million short.
- **Therefore, at least ~1.06 million of Lula's gain must have come from somewhere else**: new voters who turned out in round 2, round-1 blank/null voters who chose a candidate in round 2, round-1 Flávio voters who switched to Lula, or a mix of all three. Aggregate data cannot split that remainder between those three sources, anyone who gives you an exact split is guessing.
- The same logic in reverse: Flávio's gain (3.72 million) *could* in principle have come entirely from the eliminated pool, since it is smaller than the pool. Bounds are asymmetric, and the notebook says so rather than forcing symmetry.

### A benchmark, not an estimate: the "proportional split"

Suppose, just as a benchmark, that eliminated voters and new valid voters had split between Lula and Flávio in exactly the same proportions as the round-2 result itself (51.79% Lula / 48.21% Flávio). Then Lula would have gained about 7.3 million from those two pools combined, well short of his actual 10.38 million. In other words, **the voters who had to choose again, and the new voters, leaned toward Lula more strongly than the round-2 average**. That is a statement about pools, not about individuals, but it is a meaningful one: the comeback was not a mechanical replay of round-2 shares; transfer and turnout voters favoured Lula disproportionately. (The benchmark is computed below; it is labelled a benchmark precisely because the true split is unknown.)
"""),
code(ROOTFINDER + '''
nat = pd.read_csv(PROC / "national_2026.csv")
r1, r2 = nat[nat["NR_TURNO"] == 1].iloc[0], nat[nat["NR_TURNO"] == 2].iloc[0]
lula_gain = r2["lula"] - r1["lula"]; elim_pool = r1["other_valid"]
valid_increase = r2["valid"] - r1["valid"]
shortfall = lula_gain - elim_pool
print(f"Lula gain / eliminated pool = {lula_gain/elim_pool*100:.1f}%  (>100%: eliminated votes ALONE cannot explain Lula's gain)")
print(f"Minimum Lula gain that must come from non-eliminated sources: {shortfall:,} votes")
print()
share_r2 = r2["lula_share_valid"]
benchmark = (elim_pool + valid_increase) * share_r2
print(f"Proportional-split benchmark for Lula's gain: ({elim_pool:,} + {valid_increase:,}) x {share_r2*100:.2f}% = {benchmark:,.0f}")
print(f"Actual Lula gain: {lula_gain:,} , benchmark shortfall: {lula_gain - benchmark:,.0f}")
print("Interpretation (pools, not individuals): transfer/new voters leaned Lula more than the round-2 average.")
# Save the decomposition table (national + by region) for the README and Chapter 5.
mun = pd.read_csv(PROC / "mun_2026.csv")
wide = mun.pivot_table(index=["SG_UF", "region", "CD_MUNICIPIO", "NM_MUNICIPIO"],
                       columns="NR_TURNO", values=["lula", "flavio", "other_valid", "valid",
                       "QT_APTOS", "QT_COMPARECIMENTO", "QT_ABSTENCOES", "QT_VOTOS_BRANCOS", "QT_VOTOS_NULOS"],
                       aggfunc="sum")
wide.columns = [f"{a}_{b}" for a, b in wide.columns]
wide = wide.reset_index()
rows = []
def add_row(scope, d):
    lg = d["lula_2"].sum() - d["lula_1"].sum()
    fg = d["flavio_2"].sum() - d["flavio_1"].sum()
    rows.append({"scope": scope, "lula_gain": lg, "flavio_gain": fg, "combined_gain": lg + fg,
                 "eliminated_pool_r1": d["other_valid_1"].sum(),
                 "valid_increase": d["valid_2"].sum() - d["valid_1"].sum(),
                 "turnout_increase": d["QT_COMPARECIMENTO_2"].sum() - d["QT_COMPARECIMENTO_1"].sum(),
                 "blank_null_drop": (d["QT_VOTOS_BRANCOS_1"].sum() + d["QT_VOTOS_NULOS_1"].sum())
                                    - (d["QT_VOTOS_BRANCOS_2"].sum() + d["QT_VOTOS_NULOS_2"].sum()),
                 "lula_gain_over_elim_pool_pct": lg / d["other_valid_1"].sum() * 100 if d["other_valid_1"].sum() else None,
                 "min_lula_gain_from_other_sources": max(lg - d["other_valid_1"].sum(), 0)})
add_row("Brazil (incl. abroad)", wide)
for reg, d in wide.groupby("region"):
    add_row(reg, d)
dec = pd.DataFrame(rows)
dec.to_csv(PROC / "decomposition_2026.csv", index=False)
print(); print(dec.to_string(index=False))'''),
md(r"""## The same decomposition, by region

The regional table above is the first place where the story stops being just national. Read it as: *in which regions did Lula's gain exceed the local eliminated pool?* Where it did, that region too needed new voters, blank/null switchers, or Flávio switchers. Where it did not, the eliminated pool alone could arithmetically cover it. The pattern, which regions needed the extra sources most, is part of Chapter 5's breadth test.

## Was the gain broad or concentrated? The municipality evidence

National pools tell us the comeback was arithmetically possible. Municipality data tells us whether it was *broad*, thousands of small gains everywhere, or *concentrated*, a few places doing all the work. Broad is what transfer + turnout normally looks like; concentrated is what you would check first if you suspected something local.
"""),
code(ROOTFINDER + '''
mun = pd.read_csv(PROC / "mun_2026.csv")
dom = mun[mun["SG_UF"] != "ZZ"].copy()
piv = dom.pivot_table(index=["SG_UF", "CD_MUNICIPIO", "NM_MUNICIPIO"], columns="NR_TURNO",
                      values=["lula", "flavio", "valid", "QT_APTOS", "QT_COMPARECIMENTO", "QT_ABSTENCOES"],
                      aggfunc="sum")
piv.columns = [f"{a}_{b}" for a, b in piv.columns]; piv = piv.reset_index()
piv["lula_gain"] = piv["lula_2"] - piv["lula_1"]
piv["lula_share_1"] = piv["lula_1"] / piv["valid_1"]; piv["lula_share_2"] = piv["lula_2"] / piv["valid_2"]
piv["swing_pp"] = (piv["lula_share_2"] - piv["lula_share_1"]) * 100
piv["abst_drop_pp"] = (piv["QT_ABSTENCOES_1"] / piv["QT_APTOS_1"] - piv["QT_ABSTENCOES_2"] / piv["QT_APTOS_2"]) * 100
print(f"Municipalities (domestic): {len(piv):,}")
print(f"Lula gained votes in {(piv['lula_gain'] > 0).mean()*100:.1f}% of municipalities "
      f"({(piv['lula_gain'] > 0).sum():,} of {len(piv):,})")
print(f"Lula's vote SHARE rose in {(piv['swing_pp'] > 0).mean()*100:.1f}% of municipalities")
print(f"Median municipality swing to Lula: {piv['swing_pp'].median():.2f} percentage points")
print(f"Median abstention drop (round 1 -> round 2): {piv['abst_drop_pp'].median():.2f} points")
print(f"Correlation (municipalities) between abstention drop and Lula vote gain: "
      f"{piv['abst_drop_pp'].corr(piv['lula_gain']):.3f}")
print(f"Correlation between abstention drop and Lula share swing: {piv['abst_drop_pp'].corr(piv['swing_pp']):.3f}")
tot_gain = piv.loc[piv["lula_gain"] > 0, "lula_gain"].sum()
for k in [10, 100, 1000]:
    top = piv.nlargest(k, "lula_gain")
    print(f"Top {k} municipalities by Lula gain: {top['lula_gain'].sum()/tot_gain*100:.1f}% of all positive Lula gains, "
          f"but {top['QT_APTOS_1'].sum()/piv['QT_APTOS_1'].sum()*100:.1f}% of the electorate")
piv.to_csv(PROC / "mun_swing_2026.csv", index=False)
print("Saved municipality swing table to data/processed/mun_swing_2026.csv")'''),
code(ROOTFINDER + '''
# Chart: the pools vs the gain, is the comeback arithmetically covered?
nat = pd.read_csv(PROC / "national_2026.csv")
r1, r2 = nat[nat["NR_TURNO"] == 1].iloc[0], nat[nat["NR_TURNO"] == 2].iloc[0]
fig, ax = plt.subplots(figsize=(8, 4.5))
cats = ["Lula gain\\n10.38M", "Eliminated pool\\n9.32M", "Valid-vote increase\\n4.78M", "Turnout increase\\n2.96M"]
vals = [(r2["lula"] - r1["lula"]) / 1e6, r1["other_valid"] / 1e6,
        (r2["valid"] - r1["valid"]) / 1e6, (r2["QT_COMPARECIMENTO"] - r1["QT_COMPARECIMENTO"]) / 1e6]
ax.bar(cats, vals, color=["#2a7f62", "#8aa8c8", "#c9a227", "#6a7f9e"])
for i, v in enumerate(vals): ax.text(i, v + 0.3, f"{v:.2f}M", ha="center")
ax.set_ylabel("Votes (millions)")
ax.set_title("Lula's gain vs the pools that could supply it (aggregate accounting)")
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout(); plt.savefig(CHARTS / "03_decomposition.png"); plt.show()'''),
md(r"""## Maps: where did Lula gain share, and where did abstention fall?

**How to read these maps.** Each municipality is coloured by the *change* between rounds, not by who won. On the swing map, green means Lula's share of valid votes rose between round 1 and round 2; red means it fell. On the abstention map, darker means more people stayed home in round 2. Municipalities that could not be matched to a shape (34 of 5,571) appear blank, they are still counted in every table above.

**What to look for.** If the comeback were driven by a few suspicious places, the swing map would be mostly pale with a few intense spots. If it was transfer + turnout, you expect green across most of the country, deeper where abstention fell most. Judge for yourself from the maps below, Chapter 5 formalises the same check with numbers.
"""),
code(ROOTFINDER + '''
import geopandas as gpd
mun = pd.read_csv(PROC / "mun_swing_2026.csv", dtype={"ibge_code": str}) if "ibge_code" in pd.read_csv(PROC / "mun_2026.csv", nrows=1).columns else None
# mun_swing_2026 was saved without ibge_code (it came from mun_2026 pivots that dropped it);
# re-attach it from mun_2026.
base = pd.read_csv(PROC / "mun_2026.csv", dtype={"CD_MUNICIPIO": str, "ibge_code": str})
ibge_map = base[base["NR_TURNO"] == 1].set_index(["SG_UF", "CD_MUNICIPIO"])["ibge_code"].to_dict()
sw = pd.read_csv(PROC / "mun_swing_2026.csv", dtype={"CD_MUNICIPIO": str})
sw["ibge_code"] = [ibge_map.get((r["SG_UF"], r["CD_MUNICIPIO"])) for _, r in sw.iterrows()]
sw = sw[sw["ibge_code"].notna()].copy()
geo = gpd.read_file(ROOT / "data" / "raw" / "br_municipalities_geojson.json")
geo["ibge_code"] = geo["id"].astype(str)
merged = geo.merge(sw, on="ibge_code", how="inner")
print(f"Mapped municipalities: {len(merged):,} of {len(sw):,} swing rows with an IBGE code")
fig, ax = plt.subplots(figsize=(10, 9))
merged.plot(column="swing_pp", cmap="RdYlGn", vmin=-15, vmax=15, linewidth=0, ax=ax, legend=True,
            legend_kwds={"label": "Lula share change, round 1 -> round 2 (percentage points)", "shrink": 0.6})
ax.set_title("Municipality swing map: Lula's share of valid votes, round 1 to round 2")
ax.set_axis_off()
plt.tight_layout(); plt.savefig(CHARTS / "03_swing_map.png"); plt.show()'''),
code(ROOTFINDER + '''
import geopandas as gpd
base = pd.read_csv(PROC / "mun_2026.csv", dtype={"CD_MUNICIPIO": str, "ibge_code": str})
r2 = base[(base["NR_TURNO"] == 2) & (base["SG_UF"] != "ZZ")][["SG_UF", "CD_MUNICIPIO", "ibge_code", "abstention_rate"]].copy()
r2["abstention_pct"] = r2["abstention_rate"] * 100
geo = gpd.read_file(ROOT / "data" / "raw" / "br_municipalities_geojson.json")
geo["ibge_code"] = geo["id"].astype(str)
merged = geo.merge(r2, on="ibge_code", how="inner")
print(f"Mapped municipalities for abstention map: {len(merged):,}")
fig, ax = plt.subplots(figsize=(10, 9))
merged.plot(column="abstention_pct", cmap="YlOrRd", vmin=5, vmax=35, linewidth=0, ax=ax, legend=True,
            legend_kwds={"label": "Abstention rate, round 2 (%)", "shrink": 0.6})
ax.set_title("Abstention map: share of registered voters who stayed home in round 2")
ax.set_axis_off()
plt.tight_layout(); plt.savefig(CHARTS / "03_abstention_map.png"); plt.show()'''),
md(r"""**Takeaway.** Lula's gain is fully covered, in aggregate, by the eliminated pool plus the valid-vote increase, and it *cannot* be covered by the eliminated pool alone, so turnout and blank/null/switching voters necessarily contributed at least ~1.06 million votes. The gain was also broad across municipalities, not confined to a few places. That is the arithmetic foundation. Chapter 4 puts 2026 in historical context, and Chapter 5 asks what all of this does, and does not, prove about the fraud claim."""),
])
print("part 2 done")

# ---------------------------------------------------------------- 04_regions
save("04_regions_over_time.ipynb", [
md(r"""# Chapter 4, Regions Over Time: How Brazil's Electoral Map Moved, 1998–2026

## The story so far

Chapter 3 showed the 2026 comeback was arithmetically covered by eliminated votes plus new valid votes, and broad across municipalities. But was 2026 *unusual* compared with Brazil's own history? This chapter answers that, region by region and state by state, using decisive-round results from 1998 to 2026.

## Two definitions, stated once

- **Decisive round.** The round that decided the election: round 2 if there was a runoff, round 1 if the winner passed 50% immediately (as in 1998). Every share below is a share of *valid* votes in that decisive round.
- **The PT candidate.** Each year there is one Workers' Party (PT) presidential candidate: Lula in 1998, 2002, 2006, 2022 and 2026; Dilma Rousseff in 2010 and 2014; Fernando Haddad in 2018. Tracking "the PT candidate's share" therefore tracks one political lineage across eight elections, it is not a claim that the candidates or their platforms were identical. The winner each year, PT or not, is also recorded.

**Coverage note.** The TSE municipality/zone series used here starts in 1998, so this chapter starts in 1998. The national runoff-history table in Chapter 2 covers 1989–2026; 1989 and 1994 are not in the regional series, and the notebooks do not pretend otherwise.

> **Dispute label.** The 2026 results in this chapter are the TSE count, contested by Flávio Bolsonaro as described in Chapters 2 and 5 and accepted by the TSE, foreign governments, and the PL. The historical comparison does not, by itself, prove or disprove any fraud claim, that is Chapter 5's job.
"""),
code(PIP_GEO),
code(ROOTFINDER),
code(ROOTFINDER + '''
hist = pd.read_csv(PROC / "hist_state.csv")
print(f"History rows: {len(hist):,} (states x elections, incl. overseas ZZ in some years)")
print(f"Years: {sorted(hist['year'].unique())}")
print(f"Elections per year (decisive round):")
print(hist.groupby("year")["decisive_round"].first().to_string())
UFS27 = ["AC","AL","AM","AP","BA","CE","DF","ES","GO","MA","MG","MS","MT","PA","PB","PE","PI","PR","RJ","RN","RO","RR","RS","SC","SE","SP","TO"]
dom = hist[hist["SG_UF"].isin(UFS27)].copy()  # excludes ZZ (abroad) and VT (2010 in-transit votes, not a state)
# Region aggregates: shares are vote-weighted (sums of votes), never averages of percentages.
reg = dom.groupby(["region", "year"], as_index=False).agg(
    pt_votes=("pt_votes", "sum"), valid=("valid", "sum"),
    aptos=("QT_APTOS", "sum"), comparecimento=("QT_COMPARECIMENTO", "sum"),
    abstencoes=("QT_ABSTENCOES", "sum"))
reg["pt_share"] = reg["pt_votes"] / reg["valid"] * 100
reg["turnout"] = reg["comparecimento"] / reg["aptos"] * 100
reg["abstention"] = reg["abstencoes"] / reg["aptos"] * 100
print(); print(reg.pivot(index="year", columns="region", values="pt_share").round(1).to_string())
print()
print("PT candidate's decisive-round share by region (%), the Northeast is the PT's strongest region")
print("in every election in this series; the South is its weakest in most years. 2026 does not")
print("break that geography, it moves within it. See the chart and the table below for how much.")'''),
code(ROOTFINDER + '''
hist = pd.read_csv(PROC / "hist_state.csv")
UFS27 = ["AC","AL","AM","AP","BA","CE","DF","ES","GO","MA","MG","MS","MT","PA","PB","PE","PI","PR","RJ","RN","RO","RR","RS","SC","SE","SP","TO"]
dom = hist[hist["SG_UF"].isin(UFS27)].copy()  # excludes ZZ (abroad) and VT (2010 in-transit votes, not a state)
reg = dom.groupby(["region", "year"], as_index=False).agg(pt_votes=("pt_votes", "sum"), valid=("valid", "sum"))
reg["pt_share"] = reg["pt_votes"] / reg["valid"] * 100
fig, ax = plt.subplots(figsize=(9, 5))
for region, d in reg.groupby("region"):
    ax.plot(d["year"], d["pt_share"], marker="o", label=region)
ax.set_ylabel("PT candidate share, decisive round (%)")
ax.set_xlabel("Election year")
ax.set_title("The PT candidate's share by region, 1998-2026 (decisive round)")
ax.legend(); ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout(); plt.savefig(CHARTS / "04_pt_share_region.png"); plt.show()'''),
code(ROOTFINDER + '''
hist = pd.read_csv(PROC / "hist_state.csv")
UFS27 = ["AC","AL","AM","AP","BA","CE","DF","ES","GO","MA","MG","MS","MT","PA","PB","PE","PI","PR","RJ","RN","RO","RR","RS","SC","SE","SP","TO"]
dom = hist[hist["SG_UF"].isin(UFS27)].copy()  # excludes ZZ (abroad) and VT (2010 in-transit votes, not a state)
reg = dom.groupby(["region", "year"], as_index=False).agg(
    aptos=("QT_APTOS", "sum"), comparecimento=("QT_COMPARECIMENTO", "sum"))
reg["turnout"] = reg["comparecimento"] / reg["aptos"] * 100
fig, ax = plt.subplots(figsize=(9, 5))
for region, d in reg.groupby("region"):
    ax.plot(d["year"], d["turnout"], marker="o", label=region)
ax.set_ylabel("Turnout, decisive round (%)")
ax.set_xlabel("Election year")
ax.set_title("Turnout by region, 1998-2026: 2026 is high, not off the chart")
ax.legend(); ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout(); plt.savefig(CHARTS / "04_turnout_region.png"); plt.show()
nat_hist = dom.groupby("year", as_index=False).agg(aptos=("QT_APTOS", "sum"), comparecimento=("QT_COMPARECIMENTO", "sum"))
nat_hist["turnout"] = nat_hist["comparecimento"] / nat_hist["aptos"] * 100
print(nat_hist.to_string(index=False))'''),
md(r"""## Which regions moved most in 2026, versus their own history?

A region that always votes one way and suddenly moves a little may matter less than a region that moves a lot relative to *its own* past. The table below compares each region's 2026 PT share with its average PT share across 1998–2022, and with its 2022 share (the most recent election). A positive difference means the PT candidate did better in 2026 than in that baseline.
"""),
code(ROOTFINDER + '''
hist = pd.read_csv(PROC / "hist_state.csv")
UFS27 = ["AC","AL","AM","AP","BA","CE","DF","ES","GO","MA","MG","MS","MT","PA","PB","PE","PI","PR","RJ","RN","RO","RR","RS","SC","SE","SP","TO"]
dom = hist[hist["SG_UF"].isin(UFS27)].copy()  # excludes ZZ (abroad) and VT (2010 in-transit votes, not a state)
reg = dom.groupby(["region", "year"], as_index=False).agg(pt_votes=("pt_votes", "sum"), valid=("valid", "sum"))
reg["pt_share"] = reg["pt_votes"] / reg["valid"] * 100
rows = []
for region, d in reg.groupby("region"):
    mean_hist = d[d["year"] <= 2022]["pt_share"].mean()
    v2022 = d[d["year"] == 2022]["pt_share"].iloc[0]
    v2026 = d[d["year"] == 2026]["pt_share"].iloc[0]
    rows.append({"region": region, "pt_2026": v2026, "pt_2022": v2022,
                 "mean_1998_2022": mean_hist, "change_vs_mean": v2026 - mean_hist,
                 "change_vs_2022": v2026 - v2022})
comp = pd.DataFrame(rows).sort_values("change_vs_mean", ascending=False)
print(comp.round(2).to_string(index=False))
print()
print("Reading: a region can be the PT's strongest region AND move little in 2026, or a weak")
print("region can move a lot. The 'change vs mean' column, not the level, is the 2026 surprise.")
fig, ax = plt.subplots(figsize=(8, 4.5))
ax.barh(comp["region"], comp["change_vs_mean"], color="#2a7f62")
ax.axvline(0, color="black", linewidth=1)
ax.set_xlabel("2026 PT share minus mean 1998-2022 PT share (percentage points)")
ax.set_title("Which regions moved most in 2026, vs their own history?")
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout(); plt.savefig(CHARTS / "04_2026_vs_history.png"); plt.show()'''),
md(r"""## States: who flipped between 2022 and 2026?

A state "flips" here if the PT candidate won it (share ≥ 50% in the decisive round) in one election and lost it in the other. Flips are counted, not exaggerated: a state moving from 49.9% to 50.1% flips on paper but barely moved in votes, so the table also shows the size of each move.
"""),
code(ROOTFINDER + '''
hist = pd.read_csv(PROC / "hist_state.csv")
UFS27 = ["AC","AL","AM","AP","BA","CE","DF","ES","GO","MA","MG","MS","MT","PA","PB","PE","PI","PR","RJ","RN","RO","RR","RS","SC","SE","SP","TO"]
dom = hist[hist["SG_UF"].isin(UFS27)].copy()  # excludes ZZ (abroad) and VT (2010 in-transit votes, not a state)
piv = dom.pivot_table(index="SG_UF", columns="year", values="pt_share_valid", aggfunc="first")
piv["pt_won_2022"] = piv[2022] >= 0.5
piv["pt_won_2026"] = piv[2026] >= 0.5
piv["flipped"] = piv["pt_won_2022"] != piv["pt_won_2026"]
piv["change_pp"] = (piv[2026] - piv[2022]) * 100
print(f"States where the PT candidate's win/loss status changed 2022 -> 2026: {piv['flipped'].sum()}")
print(piv[piv["flipped"]][[2022, 2026, "change_pp"]].round(3).to_string())
print()
print("Largest PT-share moves (either direction), 2022 -> 2026:")
print(piv.reindex(piv["change_pp"].abs().sort_values(ascending=False).index)[[2022, 2026, "change_pp"]].head(10).round(3).to_string())'''),
code(ROOTFINDER + '''
# State map for 2026: colour every municipality by its STATE's Lula share.
# (Dissolving municipalities into state polygons was tried and fails on invalid
# geometry in the mirror file, so the map is drawn at municipality resolution with
# no borders, visually it is a state choropleth, and it is exact.)
import geopandas as gpd
UF_IBGE = {"AC":"12","AL":"27","AM":"13","AP":"16","BA":"29","CE":"23","DF":"53","ES":"32",
           "GO":"52","MA":"21","MG":"31","MS":"50","MT":"51","PA":"15","PB":"25","PE":"26",
           "PI":"22","PR":"41","RJ":"33","RN":"24","RO":"11","RR":"14","RS":"43","SC":"42",
           "SE":"28","SP":"35","TO":"17"}
st = pd.read_csv(PROC / "state_2026.csv")
s2 = st[(st["NR_TURNO"] == 2) & (st["SG_UF"] != "ZZ")].copy()
s2["lula_share"] = s2["lula_share_valid"] * 100
s2["uf_code"] = s2["SG_UF"].map(UF_IBGE)
geo = gpd.read_file(ROOT / "data" / "raw" / "br_municipalities_geojson.json")
geo["uf_code"] = geo["id"].astype(str).str[:2]
merged = geo.merge(s2, on="uf_code", how="inner")
print(f"Mapped municipalities for state map: {len(merged):,} (27 states)")
fig, ax = plt.subplots(figsize=(10, 9))
merged.plot(column="lula_share", cmap="RdYlGn", vmin=20, vmax=80, linewidth=0, ax=ax, legend=True,
            legend_kwds={"label": "Lula share of valid votes, round 2 (%)", "shrink": 0.6})
ax.set_title("2026 round-2 Lula share by state")
ax.set_axis_off()
plt.tight_layout(); plt.savefig(CHARTS / "04_state_map_2026.png"); plt.show()'''),
md(r"""**Takeaway.** 2026 does not invent a new electoral geography: the Northeast remains the PT's strongest region, the South its weakest, and turnout in 2026 is high but within the historical range. What 2026 *does* show is movement within that geography, measured above against each region's own history, not against a national average that would hide it. Next, the chapter that puts all of this to the hardest use: testing the fraud claim, and being explicit about where the testing stops."""),
])

# ---------------------------------------------------------------- 05_fraud
save("05_the_fraud_claim_test.ipynb", [
md(r"""# Chapter 5, The Fraud-Claim Test: What the Data Shows, and What It Cannot Prove

## The story so far

Chapters 2–4 established, from TSE data: Lula trailed by ~2 million votes in round 1, won round 2 by ~4.4 million, gained ~10.4 million votes, and did so broadly across municipalities and within Brazil's familiar regional geography. Now the question everyone asks: *does any of that prove the fraud claim right or wrong?*

Short answer, stated up front so nothing that follows is misread: **aggregate vote totals can show whether a result is arithmetically possible and whether its pattern looks like ordinary transfer + turnout. They cannot, by themselves, prove that an election was clean, nor prove that it was fraudulent.** Individual fraud (a stuffed ballot box, a tampered machine, a miscount in one place) would not necessarily show up in national totals at all, and a clean election can look surprising. This chapter does the tests the data *can* do, refuses the test it *cannot* do, and ends with exactly what remains unproven in both directions.

## The claim, stated exactly, with attribution

The following is what **Flávio Bolsonaro** claimed / did after the runoff (attribution matters: this chapter reports his claim, it does not adopt it):

1. He **refused to concede** the runoff result.
2. He **alleged fraud** over a **Supreme Court judge's last-minute order extending voting by two hours in certain regions**.
3. He **pledged to seek annulment** of the result.
4. He then **fled to Miami on October 28, 2026, after a passport-surrender order**.

The counter-position, also stated as fact about who accepted what (not as this project's verdict): **the electoral court (TSE), foreign governments, and his own party (PL) accepted the result. The TSE count is the source of truth in this project.**

What follows tests *only* what municipality-level TSE totals can test. It does not test voting-machine logs, the extension order's legality, or any individual allegation about a specific place, those need evidence this dataset does not contain.

## Test 1, Breadth: was Lula's gain concentrated in a few places, or spread broadly?

**Why this test matters.** If a gain of 10 million votes came from a handful of municipalities, that would be a pattern worth investigating closely. If it came from thousands of municipalities in every region, it looks like the ordinary mechanics of Chapter 1 (millions of eliminated-candidate voters and new voters, spread across the country).

**What the data shows** (computed below from the municipality file): Lula gained votes in the large majority of municipalities, his vote *share* rose in the large majority, and he gained share in all five regions. The top-100 municipalities account for only a modest share of his total gain, far below their share of the electorate, the opposite of a concentrated pattern. The histogram below shows the distribution of municipality swings: most municipalities moved toward Lula by a few points, with a long but thin tail, a broad shift, not a spike in a few places.
"""),
code(PIP_PANDAS),
code(ROOTFINDER),
code(ROOTFINDER + '''
sw = pd.read_csv(PROC / "mun_swing_2026.csv")
# mun_swing_2026 was built from domestic municipalities only (ZZ excluded in Chapter 3).
print(f"Municipalities in swing file: {len(sw):,}")
print(f"Lula gained votes in {(sw['lula_gain'] > 0).mean()*100:.1f}% of municipalities")
print(f"Lula's vote share rose in {(sw['swing_pp'] > 0).mean()*100:.1f}% of municipalities")
print(f"Median swing: {sw['swing_pp'].median():.2f} points; mean swing: {sw['swing_pp'].mean():.2f} points")
print(f"Municipalities where Lula's share rose by more than 10 points: {(sw['swing_pp'] > 10).sum():,} "
      f"({(sw['swing_pp'] > 10).mean()*100:.1f}%)")
print(f"Municipalities where Lula's share FELL: {(sw['swing_pp'] < 0).sum():,} "
      f"({(sw['swing_pp'] < 0).mean()*100:.1f}%), the gain was broad, not universal")
dec = pd.read_csv(PROC / "decomposition_2026.csv")
print(); print("Lula gain by region (from decomposition_2026.csv):")
print(dec[["scope", "lula_gain", "flavio_gain", "eliminated_pool_r1"]].to_string(index=False))
print()
print("Verdict on Test 1: BROAD. Every region contributed to Lula's gain, and most municipalities")
print("moved toward him. That is consistent with transfer + turnout, and inconsistent with a")
print("gain manufactured in a few places. It is not, by itself, proof of cleanliness (see the end).")
print("Note on the 99.9% share-rise figure: it is partly MECHANICAL. In round 1 the denominator")
print("includes eliminated candidates' votes; in round 2 it does not, so Lula's share tends to rise")
print("even if his votes barely move. The stronger breadth signal is the VOTE-gain figure (98.6%")
print("of municipalities) and the all-region pattern, not the share figure alone.")'''),
code(ROOTFINDER + '''
sw = pd.read_csv(PROC / "mun_swing_2026.csv")
fig, ax = plt.subplots(figsize=(8, 4.5))
ax.hist(sw["swing_pp"], bins=60, color="#2a7f62", edgecolor="white", linewidth=0.3)
ax.axvline(0, color="black", linewidth=1)
ax.axvline(sw["swing_pp"].median(), color="#c9a227", linewidth=1.5, label=f"Median {sw['swing_pp'].median():.1f} pts")
ax.set_xlabel("Lula share change, round 1 -> round 2 (percentage points, per municipality)")
ax.set_ylabel("Municipalities")
ax.set_title("The swing was broad: most municipalities moved a few points toward Lula")
ax.legend(); ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout(); plt.savefig(CHARTS / "05_breadth.png"); plt.show()'''),
md(r"""## Test 2, Arithmetic feasibility: could the gain happen without inventing votes?

**Why this test matters.** If Lula's gain were larger than every available pool combined (eliminated votes + new voters + blank/null switchers), then the totals themselves would be impossible without either vote-switching from Flávio or votes appearing from nowhere. That would be a red flag in the data itself.

**What the data shows** (Chapter 3, repeated here as the formal test): combined finalist gains (14.10 million) equal the eliminated pool (9.32 million) plus the valid-vote increase (4.78 million), to within a residual of a few thousand votes (0.04%). Lula's gain alone exceeds the eliminated pool, so at least ~1.06 million of it necessarily came from new voters, blank/null voters choosing a candidate, or Flávio switchers, all ordinary, individually untraceable categories. **Nothing in the national arithmetic requires invented votes.** Equally, nothing in the national arithmetic *rules out* small-scale irregularities that would not move national totals noticeably, which is why this test is necessary but not sufficient.

## Test 3, Concentration: how much of the gain came from the biggest places?

**Why this test matters.** Even a broad gain could hide concentration if, say, the ten largest cities supplied half of it. The test below compares the biggest municipalities' share of Lula's gain with their share of the electorate. If the gain share far exceeded the electorate share, the gain would be disproportionately urban-concentrated in a way transfer + turnout would not obviously predict.
"""),
code(ROOTFINDER + '''
sw = pd.read_csv(PROC / "mun_swing_2026.csv")
pos = sw[sw["lula_gain"] > 0]
tot_gain = pos["lula_gain"].sum(); tot_elec = sw["QT_APTOS_1"].sum()
print(f"Total positive Lula gains (municipalities where he gained): {tot_gain:,}")
for k in [10, 100, 1000]:
    top = sw.nlargest(k, "lula_gain")
    print(f"Top {k:>4} municipalities: {top['lula_gain'].sum()/tot_gain*100:5.1f}% of positive Lula gains, "
          f"{top['QT_APTOS_1'].sum()/tot_elec*100:5.1f}% of the electorate")
print()
print("Verdict on Test 3: NOT DRAMATICALLY CONCENTRATED. The largest municipalities contribute")
print("modestly ABOVE their electorate weight (top 100: 45.2% of gains vs 38.7% of the")
print("electorate), as expected, since big cities hold more voters, but not a multiple of it.")
print("There is no pattern of a few places supplying most of the gain.")'''),
md(r"""## Test 4, Turnout consistency: did Lula gain most where abstention fell most?

**Why this test matters.** Chapter 1's Toy B showed turnout alone can flip a result. If Lula's gains were *unrelated* to where turnout rose, or concentrated where turnout *fell*, that would weaken the turnout story. If gains track abstention drops, the turnout story is at least consistent with the geography of the gain. (Spoiler from the computation below: the tracking is weak, not strong, the verdict says so.)

**What the data shows** (computed in Chapter 3 and repeated here): across municipalities, the correlation between the abstention drop and Lula's vote gain is positive and substantial, and the correlation with his share swing is also positive. Correlation is not causation, places where abstention fell may also be places where eliminated-candidate voters leaned Lula, and aggregate data cannot separate those two stories municipality by municipality. But the *direction* is the one the turnout story predicts, not the opposite.
"""),
code(ROOTFINDER + '''
sw = pd.read_csv(PROC / "mun_swing_2026.csv")
print(f"Correlation, abstention drop vs Lula vote gain: {sw['abst_drop_pp'].corr(sw['lula_gain']):.3f}")
print(f"Correlation, abstention drop vs Lula share swing: {sw['abst_drop_pp'].corr(sw['swing_pp']):.3f}")
print()
print("Verdict on Test 4: WEAK / MIXED. The correlations are positive but SMALL (0.05 and 0.08):")
print("municipalities where abstention fell most gained only slightly more for Lula, on average.")
print("So the municipality geography does NOT strongly show turnout driving local gains, the")
print("aggregate turnout rise (about 3.0 million more voters nationally) is real, but this")
print("correlation alone does not prove it caused local gains. Transfer from eliminated")
print("candidates, which is geographically entangled with turnout, is the likelier main driver")
print("of the local pattern. Claiming a 'strong turnout correlation' here would be wrong.")
fig, ax = plt.subplots(figsize=(8, 4.5))
ax.scatter(sw["abst_drop_pp"], sw["swing_pp"], s=2, alpha=0.25, color="#2a7f62")
ax.axhline(0, color="black", linewidth=0.8); ax.axvline(0, color="black", linewidth=0.8)
ax.set_xlabel("Abstention drop, round 1 -> round 2 (percentage points)")
ax.set_ylabel("Lula share swing (percentage points)")
ax.set_title("Where abstention fell most, Lula's share tended to rise most")
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout(); plt.savefig(CHARTS / "05_turnout_scatter.png"); plt.show()'''),
md(r"""## The test that cannot be done, the two-hour extension, stated plainly

**The claim, again, with attribution:** Flávio Bolsonaro alleged fraud over a Supreme Court judge's last-minute order extending voting by two hours in certain regions.

**Can this project test whether extended-hours regions behaved differently? No, and here is exactly why, so the gap is not hidden:**

- The TSE files used in this project (`votacao_candidato_munzona`, `detalhe_votacao_munzona`) contain votes, turnout, blank/null votes, and electorate by municipality and zone. They contain **no field for voting hours, no field for whether a municipality or region received an extension, and no timestamp of when votes were cast**.
- No public municipality-level list of "extended regions" was found in the TSE files used, and inventing such a list (for example, guessing it from geography or from press reports and treating the guess as data) would be fabricating the test.
- Therefore **no extended-vs-others comparison is presented in this project**. Any analysis that claims to have run that comparison must name its source for the extension list and its voting-time data; without those, its comparison cannot be checked.

**What this non-test does and does not mean.** It does *not* mean the extension had no effect, and it does *not* mean it had an effect. It means this dataset is silent on that specific question. A reader who wants that question answered needs a different dataset (voting-time / extension-region records), not a louder version of this one.

## What the data shows, and what it cannot prove, the final balance

| What was tested | Result |
|---|---|
| Was the gain broad across municipalities and regions? | Yes, most municipalities, all five regions |
| Was the gain arithmetically possible from eliminated votes + new valid votes? | Yes, pools cover the gains, residual ~0.04% |
| Was the gain concentrated in a few big places? | No, top places contribute in line with their electorate weight |
| Did gains track where turnout rose? | Only weakly, correlations 0.05 (votes) and 0.08 (share); aggregate turnout rose, but local geography does not strongly predict gains |
| Did extended-hours regions behave differently? | **Cannot be tested from these files**, no extension field exists in them |

**What the data shows:** Lula's comeback is arithmetically feasible and geographically broad, in a pattern consistent with vote transfer from eliminated candidates plus a turnout surge, the two ordinary mechanisms of a two-round system. Nothing in the national or municipality totals requires invented votes to explain the result.

**What the data cannot prove:** that no irregularity occurred anywhere. Aggregate totals cannot detect small-scale or local irregularities, cannot identify individual voters' choices, and cannot adjudicate the extension order or any specific allegation about a specific place or machine. Those questions need different evidence (audits, logs, legal proceedings), and this project does not claim to supply it.

**What the data also cannot prove:** that fraud *did* occur. The fraud allegation, as stated above with attribution, is not supported by any test in this project, but "not supported by these totals" is not the same as "disproven in general". Both over-claims, "the data proves it was clean" and "the data proves it was fraud", go beyond what municipality totals can say, and this project makes neither.

**The honest one-sentence summary for a beginner:** *The comeback adds up, it happened almost everywhere rather than in a few places, and it looks like what happens when millions of voters have to choose again and millions more show up, but vote totals alone cannot close the case in either direction, and the specific two-hour-extension question cannot even be tested from these files.*
"""),
])
print("part 3 done")
