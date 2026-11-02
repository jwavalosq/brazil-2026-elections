"""Build processed CSVs from TSE open-data ZIPs (no key, no login).

Inputs (data/raw/, downloaded from https://cdn.tse.jus.br/estatistica/sead/odsele/):
  votacao_candidato_munzona_<YEAR>.zip  - candidate votes by municipality/zone
  detalhe_votacao_munzona_<YEAR>.zip     - turnout/abstention/blank/null by municipality/zone
Outputs (data/processed/):
  mun_2026.csv        - one row per municipality x round, Lula/Flavio/other/blank/null/abstention/electorate
  state_2026.csv      - same, aggregated by state (UF) and region
  national_2026.csv   - national totals by round
  decomposition_2026.csv - national + regional vote-transfer decomposition (see notebook 03)
  hist_state.csv      - 1998-2026, decisive-round PT share, winner, turnout, abstention by state/region
  runoff_history.csv  - 1989-2026 round-1 leader vs runoff winner (national; see notebook 02 notes)
Only president (CD_CARGO=1) rows are kept. Files are read in latin-1 with ';' separator,
the TSE standard. Zone-level rows are summed to municipality level.
"""
import zipfile, io, sys
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)

REGION = {}
for uf in ["AC","AM","AP","PA","RO","RR","TO"]: REGION[uf]="North"
for uf in ["AL","BA","CE","MA","PB","PE","PI","RN","SE"]: REGION[uf]="Northeast"
for uf in ["DF","GO","MS","MT"]: REGION[uf]="Center-West"
for uf in ["ES","MG","RJ","SP"]: REGION[uf]="Southeast"
for uf in ["PR","RS","SC"]: REGION[uf]="South"
REGION["ZZ"]="Abroad"  # overseas voting locations (186), not a municipality

def read_zip_csv(zpath, want_cols):
    """Yield dataframes per member file, keeping only want_cols that exist."""
    z = zipfile.ZipFile(zpath)
    frames = []
    for name in z.namelist():
        if not (name.lower().endswith((".csv", ".txt"))):
            continue
        # *_BRASIL.csv duplicates every office (3.2 GB uncompressed in 2026)
        # including the president rows already in *_BR.csv. Exclude it or
        # president votes would be double-counted.
        if name.upper().endswith("_BRASIL.CSV"):
            continue
        with z.open(name) as f:
            raw = f.read()
        try:
            df = pd.read_csv(io.BytesIO(raw), sep=";", encoding="latin-1", low_memory=False,
                             dtype=str, usecols=lambda c: c in want_cols)
        except Exception as e:
            print(f"  skip {name}: {e}", file=sys.stderr); continue
        frames.append(df)
    if not frames:
        raise SystemExit(f"No usable files in {zpath}")
    return pd.concat(frames, ignore_index=True)


def read_brasil_president(zpath, want_cols):
    """1998 only: the ZIP has no *_BR.csv; president rows live in *_BRASIL.csv.
    Read it in chunks and keep only CD_CARGO=1 rows, so the 723 MB file never
    sits in memory whole."""
    z = zipfile.ZipFile(zpath)
    name = [n for n in z.namelist() if n.upper().endswith("_BRASIL.CSV")][0]
    frames = []
    with z.open(name) as f:
        for chunk in pd.read_csv(f, sep=";", encoding="latin-1", low_memory=False,
                                 dtype=str, usecols=lambda c: c in want_cols,
                                 chunksize=200000):
            if "CD_CARGO" in chunk.columns:
                chunk = chunk[chunk["CD_CARGO"].astype(str).str.strip() == "1"]
            if len(chunk):
                frames.append(chunk)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(columns=want_cols)

def to_int(s):
    return pd.to_numeric(s, errors="coerce").fillna(0).astype("int64")

def process_year(year):
    vz = RAW / f"votacao_candidato_munzona_{year}.zip"
    dz = RAW / f"detalhe_votacao_munzona_{year}.zip"
    print(f"== {year}: {vz.name} ({vz.stat().st_size/1e6:.1f} MB)")
    vc = ["ANO_ELEICAO","NR_TURNO","SG_UF","CD_MUNICIPIO","NM_MUNICIPIO","CD_CARGO",
          "NR_CANDIDATO","NM_CANDIDATO","SG_PARTIDO","QT_VOTOS_NOMINAIS"]
    df = read_zip_csv(vz, vc)
    df = df[df["CD_CARGO"].astype(str).str.strip() == "1"].copy()
    if year == 1998:
        # No *_BR.csv in the 1998 ZIP (see read_brasil_president), and its
        # QT_VOTOS_NOMINAIS column is all zeros, the real count is in
        # QT_VOTOS_NOMINAIS_VALIDOS (verified against the file's first rows).
        extra = read_brasil_president(vz, vc + ["QT_VOTOS_NOMINAIS_VALIDOS"])
        if "QT_VOTOS_NOMINAIS_VALIDOS" in extra.columns:
            extra["QT_VOTOS_NOMINAIS"] = extra["QT_VOTOS_NOMINAIS_VALIDOS"]
        if len(extra):
            df = pd.concat([df, extra], ignore_index=True)
    df["NR_TURNO"] = to_int(df["NR_TURNO"])
    # TSE codes are zero-padded in detalhe files (e.g. 01066) but not in
    # votacao files (1066). Normalise both to the unpadded form or the merge
    # silently drops most municipalities.
    df["CD_MUNICIPIO"] = df["CD_MUNICIPIO"].astype(str).str.strip().str.lstrip("0").replace("", "0")
    df["QT_VOTOS_NOMINAIS"] = to_int(df["QT_VOTOS_NOMINAIS"])
    df["NM_CANDIDATO"] = df["NM_CANDIDATO"].astype(str).str.strip()
    # municipality x round x candidate
    mun_c = (df.groupby(["SG_UF","CD_MUNICIPIO","NM_MUNICIPIO","NR_TURNO","NM_CANDIDATO","SG_PARTIDO"],
                        as_index=False)["QT_VOTOS_NOMINAIS"].sum())
    # detalhe
    dc = ["NR_TURNO","SG_UF","CD_MUNICIPIO","QT_APTOS","QT_COMPARECIMENTO","QT_ABSTENCOES",
          "QT_VOTOS_BRANCOS","QT_VOTOS_NULOS"]
    dc_full = dc + ["CD_CARGO"]
    det = read_zip_csv(dz, dc_full)
    if "CD_CARGO" in det.columns:
        det = det[det["CD_CARGO"].astype(str).str.strip() == "1"].copy()
    det["NR_TURNO"] = to_int(det["NR_TURNO"])
    det["CD_MUNICIPIO"] = det["CD_MUNICIPIO"].astype(str).str.strip().str.lstrip("0").replace("", "0")
    for c in ["QT_APTOS","QT_COMPARECIMENTO","QT_ABSTENCOES","QT_VOTOS_BRANCOS","QT_VOTOS_NULOS"]:
        det[c] = to_int(det[c])
    mun_d = (det.groupby(["SG_UF","CD_MUNICIPIO","NR_TURNO"], as_index=False)
               [["QT_APTOS","QT_COMPARECIMENTO","QT_ABSTENCOES","QT_VOTOS_BRANCOS","QT_VOTOS_NULOS"]].sum())
    return mun_c, mun_d

def build_2026():
    mun_c, mun_d = process_year(2026)
    # pivot candidates
    piv = mun_c.pivot_table(index=["SG_UF","CD_MUNICIPIO","NM_MUNICIPIO","NR_TURNO"],
                            columns="NM_CANDIDATO", values="QT_VOTOS_NOMINAIS",
                            aggfunc="sum", fill_value=0).reset_index()
    # identify Lula / Flavio columns by name substring
    lula_col = [c for c in piv.columns if "LULA" in str(c).upper()][0]
    flav_col = [c for c in piv.columns if "BOLSONARO" in str(c).upper()]
    flav_col = flav_col[0]
    print(f"Lula column: {lula_col!r}; Flavio column: {flav_col!r}")
    print(f"All 2026 candidates: {sorted([c for c in piv.columns if c not in ['SG_UF','CD_MUNICIPIO','NM_MUNICIPIO','NR_TURNO']])}")
    piv["lula"] = piv[lula_col]; piv["flavio"] = piv[flav_col]
    piv["other_valid"] = piv[[c for c in piv.columns if c not in
        ['SG_UF','CD_MUNICIPIO','NM_MUNICIPIO','NR_TURNO','lula','flavio',lula_col,flav_col]]].sum(axis=1) \
        if len(piv.columns) > 6 else 0
    piv["valid"] = piv["lula"] + piv["flavio"] + piv["other_valid"]
    mun = piv[["SG_UF","CD_MUNICIPIO","NM_MUNICIPIO","NR_TURNO","lula","flavio","other_valid","valid"]].merge(
        mun_d, on=["SG_UF","CD_MUNICIPIO","NR_TURNO"], how="left")
    mun["region"] = mun["SG_UF"].map(REGION)
    mun["lula_share_valid"] = mun["lula"] / mun["valid"].replace(0, pd.NA)
    mun["flavio_share_valid"] = mun["flavio"] / mun["valid"].replace(0, pd.NA)
    mun["abstention_rate"] = mun["QT_ABSTENCOES"] / mun["QT_APTOS"].replace(0, pd.NA)
    mun["turnout_rate"] = mun["QT_COMPARECIMENTO"] / mun["QT_APTOS"].replace(0, pd.NA)

    # --- IBGE crosswalk for maps ---
    # TSE municipality codes are NOT IBGE codes (e.g. Porto Walter: TSE 1066,
    # IBGE 1200393). Join by (state, normalised name) to the IBGE-derived
    # municipality GeoJSON in data/raw. ZZ (abroad) has no IBGE code.
    import json as _json, unicodedata as _ud, re as _re
    UF_IBGE = {"AC":"12","AL":"27","AM":"13","AP":"16","BA":"29","CE":"23","DF":"53",
               "ES":"32","GO":"52","MA":"21","MG":"31","MS":"50","MT":"51","PA":"15",
               "PB":"25","PE":"26","PI":"22","PR":"41","RJ":"33","RN":"24","RO":"11",
               "RR":"14","RS":"43","SC":"42","SE":"28","SP":"35","TO":"17"}
    def _norm(name):
        name = _ud.normalize("NFKD", str(name).upper())
        name = "".join(c for c in name if not _ud.combining(c))
        name = _re.sub(r"[^A-Z0-9 ]", " ", name)
        return _re.sub(r"\s+", " ", name).strip()
    geo = _json.load(open(RAW / "br_municipalities_geojson.json", encoding="utf-8"))
    geo_map = {}
    for feat in geo["features"]:
        ibge = str(feat["properties"]["id"])
        geo_map[(ibge[:2], _norm(feat["properties"]["name"]))] = ibge
    mun["ibge_code"] = mun.apply(
        lambda r: geo_map.get((UF_IBGE.get(r["SG_UF"], ""), _norm(r["NM_MUNICIPIO"]))), axis=1)
    matched = mun[mun["NR_TURNO"] == 1]["ibge_code"].notna().sum()
    domestic = (mun["NR_TURNO"] == 1) & (mun["SG_UF"] != "ZZ")
    print(f"IBGE crosswalk: {matched} of {domestic.sum()} domestic municipalities matched by name+state; "
          f"{domestic.sum() - matched} unmatched (kept in CSVs, excluded from municipality maps)")
    mun.to_csv(OUT / "mun_2026.csv", index=False)
    print(f"mun_2026: {len(mun)} rows, {mun['CD_MUNICIPIO'].nunique()} municipalities")
    # state + national
    agg = {"lula":"sum","flavio":"sum","other_valid":"sum","valid":"sum","QT_APTOS":"sum",
           "QT_COMPARECIMENTO":"sum","QT_ABSTENCOES":"sum","QT_VOTOS_BRANCOS":"sum","QT_VOTOS_NULOS":"sum"}
    st = mun.groupby(["SG_UF","region","NR_TURNO"], as_index=False).agg(agg)
    st["lula_share_valid"] = st["lula"]/st["valid"]; st["flavio_share_valid"] = st["flavio"]/st["valid"]
    st["abstention_rate"] = st["QT_ABSTENCOES"]/st["QT_APTOS"]; st["turnout_rate"] = st["QT_COMPARECIMENTO"]/st["QT_APTOS"]
    st.to_csv(OUT / "state_2026.csv", index=False)
    nat = mun.groupby(["NR_TURNO"], as_index=False).agg(agg)
    nat["lula_share_valid"] = nat["lula"]/nat["valid"]; nat["flavio_share_valid"] = nat["flavio"]/nat["valid"]
    nat["abstention_rate"] = nat["QT_ABSTENCOES"]/nat["QT_APTOS"]; nat["turnout_rate"] = nat["QT_COMPARECIMENTO"]/nat["QT_APTOS"]
    nat.to_csv(OUT / "national_2026.csv", index=False)
    print(nat.to_string())
    return mun, st, nat

def build_history():
    rows = []
    for year in [1998,2002,2006,2010,2014,2018,2022]:
        mun_c, mun_d = process_year(year)
        # decisive round: 2 if any round-2 president rows, else 1
        dec = 2 if (mun_c["NR_TURNO"] == 2).any() else 1
        c_dec = mun_c[mun_c["NR_TURNO"] == dec]
        # state totals per candidate
        st_c = c_dec.groupby(["SG_UF","NM_CANDIDATO","SG_PARTIDO"], as_index=False)["QT_VOTOS_NOMINAIS"].sum()
        # PT candidate per state = max PT votes (there is one PT presidential candidate per year)
        pt = st_c[st_c["SG_PARTIDO"].astype(str).str.strip() == "PT"]
        pt_state = pt.groupby("SG_UF", as_index=False)["QT_VOTOS_NOMINAIS"].max().rename(columns={"QT_VOTOS_NOMINAIS":"pt_votes"})
        win = st_c.loc[st_c.groupby("SG_UF")["QT_VOTOS_NOMINAIS"].idxmax()][["SG_UF","NM_CANDIDATO","QT_VOTOS_NOMINAIS"]]
        win = win.rename(columns={"NM_CANDIDATO":"winner","QT_VOTOS_NOMINAIS":"winner_votes"})
        valid = st_c.groupby("SG_UF", as_index=False)["QT_VOTOS_NOMINAIS"].sum().rename(columns={"QT_VOTOS_NOMINAIS":"valid"})
        d_dec = mun_d[mun_d["NR_TURNO"] == dec].groupby("SG_UF", as_index=False)[
            ["QT_APTOS","QT_COMPARECIMENTO","QT_ABSTENCOES","QT_VOTOS_BRANCOS","QT_VOTOS_NULOS"]].sum()
        s = valid.merge(pt_state, on="SG_UF", how="left").merge(win, on="SG_UF").merge(d_dec, on="SG_UF")
        s["year"] = year; s["decisive_round"] = dec; s["region"] = s["SG_UF"].map(REGION)
        s["pt_share_valid"] = s["pt_votes"] / s["valid"]
        s["winner_share_valid"] = s["winner_votes"] / s["valid"]
        s["turnout_rate"] = s["QT_COMPARECIMENTO"] / s["QT_APTOS"]
        s["abstention_rate"] = s["QT_ABSTENCOES"] / s["QT_APTOS"]
        rows.append(s)
        print(f"{year}: decisive round {dec}, states {len(s)}, PT national share "
              f"{s['pt_votes'].sum()/s['valid'].sum():.4f}")
    # 2026 from already-built state file (decisive round 2)
    st26 = pd.read_csv(OUT / "state_2026.csv")
    s26 = st26[st26["NR_TURNO"] == 2].copy()
    s26 = s26.rename(columns={"SG_UF":"SG_UF","lula":"pt_votes","valid":"valid"})
    s26["year"] = 2026; s26["decisive_round"] = 2
    s26["winner"] = "LUIZ INÁCIO LULA DA SILVA"; s26["winner_votes"] = s26["pt_votes"]
    s26["pt_share_valid"] = s26["pt_votes"] / s26["valid"]
    s26["winner_share_valid"] = s26["pt_share_valid"]
    rows.append(s26[["SG_UF","region","year","decisive_round","pt_votes","winner","winner_votes","valid",
                     "QT_APTOS","QT_COMPARECIMENTO","QT_ABSTENCOES","QT_VOTOS_BRANCOS","QT_VOTOS_NULOS",
                     "pt_share_valid","winner_share_valid","turnout_rate","abstention_rate"]])
    hist = pd.concat(rows, ignore_index=True)
    hist.to_csv(OUT / "hist_state.csv", index=False)
    print(f"hist_state: {len(hist)} rows")

if __name__ == "__main__":
    build_2026()
    build_history()
    print("DONE")
