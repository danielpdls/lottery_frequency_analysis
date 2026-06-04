
from __future__ import annotations

from pathlib import Path
import re
import numpy as np
import pandas as pd

DATA_URLS = {
    "mega_millions_ny_open_data": "https://data.ny.gov/api/views/5xaw-6ayf/rows.csv?accessType=DOWNLOAD",
    "powerball_ny_open_data": "https://data.ny.gov/api/views/d6yy-54nr/rows.csv?accessType=DOWNLOAD",
    "melate_pakin_raw": "https://raw.githubusercontent.com/pakinja/pakin/refs/heads/master/Melate.csv",
    "melate_loteria_nacional_resultados": "https://www.loterianacional.gob.mx/Melate/Resultados",
}


def ensure_datetime(df: pd.DataFrame, date_col: str, dayfirst: bool = False) -> pd.DataFrame:
    out = df.copy()
    out[date_col] = pd.to_datetime(out[date_col], errors="coerce", dayfirst=dayfirst)
    return out.dropna(subset=[date_col])


def add_common_features(df: pd.DataFrame, number_cols: list[str]) -> pd.DataFrame:
    out = df.copy()
    nums = out[number_cols].astype(int)
    out["suma"] = nums.sum(axis=1)
    out["promedio"] = nums.mean(axis=1).round(2)
    out["pares"] = (nums % 2 == 0).sum(axis=1)
    out["impares"] = (nums % 2 != 0).sum(axis=1)
    out["consecutivos"] = nums.apply(lambda row: sum(np.diff(sorted(row.values)) == 1), axis=1)
    return out


def analyze_game(
    draws: pd.DataFrame,
    date_col: str,
    main_cols: list[str],
    special_cols: list[str] | None = None,
    top_n: int = 15,
    game_name: str = "Juego",
) -> dict:
    draws = draws.copy()
    draws = draws.sort_values(date_col).reset_index(drop=True)
    draws["draw_index"] = np.arange(len(draws))

    def build_metrics(cols: list[str]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        values = pd.concat([pd.to_numeric(draws[c], errors="coerce") for c in cols], ignore_index=True)
        values = values.dropna().astype(int)
        freq = values.value_counts().sort_index().rename("frecuencia").to_frame()
        freq["proporcion"] = (freq["frecuencia"] / freq["frecuencia"].sum()).round(5)
        freq_reset = freq.reset_index().rename(columns={freq.reset_index().columns[0]: "numero"})

        records = []
        for num in freq_reset["numero"].astype(int):
            mask = False
            for c in cols:
                mask = mask | (draws[c].astype("Int64") == num)

            idxs = draws.loc[mask, "draw_index"].to_numpy()
            dates = draws.loc[mask, date_col].to_numpy()
            gaps = np.diff(idxs)
            records.append({
                "numero": int(num),
                "apariciones": int(len(idxs)),
                "proporcion": round(float(len(idxs) / len(draws)), 5),
                "gap_promedio_sorteos": round(float(np.mean(gaps)), 2) if len(gaps) else np.nan,
                "gap_mediana_sorteos": round(float(np.median(gaps)), 2) if len(gaps) else np.nan,
                "gap_min_sorteos": int(np.min(gaps)) if len(gaps) else np.nan,
                "gap_max_sorteos": int(np.max(gaps)) if len(gaps) else np.nan,
                "ultima_fecha": pd.to_datetime(dates[-1]).date().isoformat() if len(dates) else None,
            })

        metrics = pd.DataFrame(records).sort_values(["apariciones", "gap_promedio_sorteos"], ascending=[False, True])
        return freq_reset, metrics.reset_index(drop=True), metrics.head(top_n).reset_index(drop=True)

    freq_main, metrics_main, top_main = build_metrics(main_cols)
    freq_special = metrics_special = top_special = None
    if special_cols:
        freq_special, metrics_special, top_special = build_metrics(special_cols)

    return {
        "game": game_name,
        "draws_count": len(draws),
        "min_date": pd.to_datetime(draws[date_col]).min().date().isoformat(),
        "max_date": pd.to_datetime(draws[date_col]).max().date().isoformat(),
        "freq_main": freq_main,
        "metrics_main": metrics_main,
        "top_main": top_main,
        "freq_special": freq_special,
        "metrics_special": metrics_special,
        "top_special": top_special,
    }


def save_analysis(outdir: Path, analysis: dict) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    game = analysis["game"].lower().replace(" ", "_")
    analysis["freq_main"].to_csv(outdir / f"{game}_freq_main.csv", index=False)
    analysis["metrics_main"].to_csv(outdir / f"{game}_metrics_main.csv", index=False)
    analysis["top_main"].to_csv(outdir / f"{game}_top_main.csv", index=False)
    if analysis["freq_special"] is not None:
        analysis["freq_special"].to_csv(outdir / f"{game}_freq_special.csv", index=False)
        analysis["metrics_special"].to_csv(outdir / f"{game}_metrics_special.csv", index=False)
        analysis["top_special"].to_csv(outdir / f"{game}_top_special.csv", index=False)


def load_melate_csv(path_or_url: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path_or_url)
    df = ensure_datetime(df, "FECHA", dayfirst=True)
    for c in ["R1", "R2", "R3", "R4", "R5", "R6", "R7"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").astype("Int64")
    cols = ["FECHA", "R1", "R2", "R3", "R4", "R5", "R6", "R7"]
    return df[cols].dropna(subset=["R1", "R2", "R3", "R4", "R5", "R6"])


def load_megamillions_csv(path_or_url: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path_or_url)
    df = ensure_datetime(df, "Draw Date", dayfirst=False)
    nums = df["Winning Numbers"].astype(str).str.split().apply(lambda xs: [int(x) for x in xs] if len(xs) == 5 else [np.nan] * 5)
    nums = pd.DataFrame(nums.tolist(), columns=["N1", "N2", "N3", "N4", "N5"])
    out = pd.concat([df[["Draw Date", "Mega Ball"]].reset_index(drop=True), nums], axis=1).rename(columns={"Draw Date": "FECHA", "Mega Ball": "MB"})
    for c in ["N1", "N2", "N3", "N4", "N5", "MB"]:
        out[c] = pd.to_numeric(out[c], errors="coerce").astype("Int64")
    return out.dropna(subset=["N1", "N2", "N3", "N4", "N5", "MB"])


def load_powerball_generic_csv(path_or_url: str | Path) -> pd.DataFrame:
    # Texas Lottery format from the original project: no header.
    raw = pd.read_csv(path_or_url, header=None)
    if raw.shape[1] == 11:
        raw.columns = ["GAME", "MONTH", "DAY", "YEAR", "N1", "N2", "N3", "N4", "N5", "PB", "POWERPLAY"]
        raw["FECHA"] = pd.to_datetime(raw[["YEAR", "MONTH", "DAY"]].rename(columns={"YEAR": "year", "MONTH": "month", "DAY": "day"}), errors="coerce")
    else:
        # NY Open Data usually has columns: Draw Date, Winning Numbers, Powerball, Multiplier
        raw = pd.read_csv(path_or_url)
        raw = ensure_datetime(raw, "Draw Date", dayfirst=False)
        nums = raw["Winning Numbers"].astype(str).str.split().apply(lambda xs: [int(x) for x in xs] if len(xs) == 5 else [np.nan] * 5)
        nums = pd.DataFrame(nums.tolist(), columns=["N1", "N2", "N3", "N4", "N5"])
        out = pd.concat([raw[["Draw Date", "Powerball"]].reset_index(drop=True), nums], axis=1).rename(columns={"Draw Date": "FECHA", "Powerball": "PB"})
        for c in ["N1", "N2", "N3", "N4", "N5", "PB"]:
            out[c] = pd.to_numeric(out[c], errors="coerce").astype("Int64")
        return out.dropna(subset=["N1", "N2", "N3", "N4", "N5", "PB"])

    raw = raw.dropna(subset=["FECHA"])
    for c in ["N1", "N2", "N3", "N4", "N5", "PB"]:
        raw[c] = pd.to_numeric(raw[c], errors="coerce").astype("Int64")
    return raw[["FECHA", "N1", "N2", "N3", "N4", "N5", "PB"]].dropna(subset=["N1", "N2", "N3", "N4", "N5", "PB"])


def load_with_online_fallback(loader, online_url: str, local_path: str | Path) -> pd.DataFrame:
    try:
        return loader(online_url)
    except Exception as exc:
        print(f"No se pudo cargar la fuente online. Se usará archivo local. Detalle: {exc}")
        return loader(local_path)
