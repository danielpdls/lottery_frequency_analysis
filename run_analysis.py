from pathlib import Path
from src.loteria_analysis import load_melate_csv, load_megamillions_csv, load_powerball_generic_csv, analyze_game, save_analysis
import pandas as pd

ROOT = Path(__file__).resolve().parent
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)

melate = load_melate_csv(RAW / "melate_with_recent_official_2026-05-31_partial.csv")
mega = load_megamillions_csv(RAW / "mega_millions_uploaded_2026-02-10.csv")
power = load_powerball_generic_csv(RAW / "powerball_uploaded_2026-02-09.csv")

analyses = [
    analyze_game(melate, "FECHA", ["R1","R2","R3","R4","R5","R6"], ["R7"], game_name="Melate"),
    analyze_game(mega, "FECHA", ["N1","N2","N3","N4","N5"], ["MB"], game_name="Mega Millions"),
    analyze_game(power, "FECHA", ["N1","N2","N3","N4","N5"], ["PB"], game_name="Powerball"),
]

for a in analyses:
    save_analysis(OUT, a)

summary = pd.DataFrame([{
    "juego": a["game"],
    "sorteos_analizados": a["draws_count"],
    "fecha_inicial": a["min_date"],
    "fecha_final": a["max_date"],
    "numero_mas_frecuente_principal": int(a["top_main"].iloc[0]["numero"]),
    "apariciones": int(a["top_main"].iloc[0]["apariciones"]),
} for a in analyses])
summary.to_csv(OUT / "resumen_general.csv", index=False)
print(summary)
