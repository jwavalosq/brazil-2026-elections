# Data provenance, data/raw/

All sources are public and free, no key, no login, no payment. Built 2026-11-02.

## Files kept here

- `detalhe_votacao_munzona_<1998,2002,2006,2010,2014,2018,2022,2026>.zip`
  TSE open data, turnout details by municipality/zone.
  https://cdn.tse.jus.br/estatistica/sead/odsele/detalhe_votacao_munzona/detalhe_votacao_munzona_<YEAR>.zip
- `br_municipalities_geojson.json`
  Public IBGE-derived municipality shapes, mirror `tbrugz/geodata-br` (5,564 municipalities, `id` = IBGE code).
  https://raw.githubusercontent.com/tbrugz/geodata-br/master/geojson/geojs-100-mun.json
  (Official IBGE shapefile is 203 MB and IBGE's Malhas API was unreachable from the build machine, see BUILD_REPORT.md.)

## Files used in the build but deleted afterwards (re-downloadable)

- `votacao_candidato_munzona_<YEAR>.zip` for 1998, 2002, 2006, 2010, 2014, 2018, 2022, 2026
  TSE open data, candidate votes by municipality/zone. President rows only, from `*_BR.csv`
  (1998: from `*_BRASIL.csv`, chunked, see BUILD_REPORT.md).
  https://cdn.tse.jus.br/estatistica/sead/odsele/votacao_candidato_munzona/votacao_candidato_munzona_<YEAR>.zip
  Approximate compressed sizes: 1998 ~102 MB, 2002 ~115 MB, 2006 ~125 MB, 2010 ~127 MB,
  2014 ~472 MB, 2018 ~378 MB, 2022 ~551 MB, 2026 ~434 MB (total ~2.4 GB).
  Deleted after `scripts/build_processed.py` produced the processed CSVs, to keep the folder
  reasonable. To reproduce the build, re-download these files into this folder and run
  `python scripts/build_processed.py` from the repo root.

## Processed outputs (data/processed/)

Built by `scripts/build_processed.py` from the files above:
`mun_2026.csv`, `state_2026.csv`, `national_2026.csv`, `candidate_2026.csv`,
`hist_state.csv` (1998–2026 by state), `decomposition_2026.csv` and
`mun_swing_2026.csv` (built by notebook 03 from `mun_2026.csv`).

Verification: the TSE files reproduce, to the vote, Lula 53,879,538 / Flávio 56,104,503
in round 1 and Lula 64,256,232 (51.79%) / Flávio 59,826,041 (48.21%) in round 2.
