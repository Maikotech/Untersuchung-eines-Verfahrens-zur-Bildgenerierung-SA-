from datetime import date
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
Messzeit = 2   #Messdauer (max. 12h)
CSV_akt = r"C:\U_M\Studienarbeit\Jetson_Data\bf16\Systemmonitor_Jetson_2026-10-07.csv"

def lese_jetson_csv(dateipfad):
    df = pd.read_csv(
        dateipfad,
        sep=";",
        decimal=","
    )

     # Ungültige Werte entfernen
    df = df.dropna(
        subset=[
            "Zeit", "CPU[%]", "RAM_MB", "GPU[%]", "GPU_TEMP_C"
        ]
    )

    return df

# Statistische Kennzahlen berechnen

def berechne_statistik(df):

    messwerte = [
        "CPU[%]",
        "RAM_MB",
        "GPU[%]",
        "GPU_TEMP_C",
    ]
    #Alle werte in numerische Werte konvertieren
    for spalte in messwerte:
        df[spalte] = pd.to_numeric(
            df[spalte],
            errors="coerce"
        )

    anzahl_vorher = len(df)
    
    df = df.dropna(
        subset=messwerte
    )
    
    anzahl_nachher = len(df)
    
    print(
        f"Ungültige Messpunkte entfernt: "
        f"{anzahl_vorher - anzahl_nachher}"
    )

    ergebnis = {}

    for spalte in messwerte:

        daten = df[spalte]

        ergebnis[spalte] = {
            "Mittelwert": daten.mean(),
            "Minimum": daten.min(),
            "Maximum": daten.max(),
            "Median": daten.median(),
            "95. Perzentil": daten.quantile(0.95)
        }

    return pd.DataFrame(ergebnis).T


def main():


    print("...Lese werte...")
    df_akt = lese_jetson_csv(CSV_akt)

    print()

    print(
        f"Messpunkte aktuell:  {len(df_akt)}"
    )

    print()


    # Statistiken berechnen
    stats_akt = berechne_statistik(
        df_akt
    )
    # Tabellen zusammenführen

    ergebnis = pd.DataFrame({

        "BF 16 – 07.10.2026": stats_akt[
            "Mittelwert"
        ]
    })

    # Komplette Tabelle ausgeben

    print("=" * 70)
    print("STATISTISCHE AUSWERTUNG")
    print("=" * 70)

    for messgroesse in [
        "CPU[%]",
        "RAM_MB",
        "GPU[%]",
        "GPU_TEMP_C"
    ]:

        print()
        print(
            f"--- {messgroesse} ---"
        )

        print(
            f"{'Kennzahl':<20}"
            f"{'BF 16 – 07.10.2026':>18}"
        )

        print("-" * 74)

        for kennzahl in [
            "Mittelwert",
            "Minimum",
            "Maximum",
            "Median",
            "95. Perzentil"
        ]:

            vorher = stats_akt.loc[
                messgroesse,
                kennzahl
            ]

            print(
                f"{kennzahl:<20}"
                f"{vorher:>17.2f}"
            )

    ergebnis_datei = "jetson_akt_statistik.csv"

    alle_stats = pd.concat(
        {
            "BF 16 – 07.10.2026": stats_akt
        },
        axis=1
    )

    alle_stats.to_csv(
        ergebnis_datei,
        sep=";",
        decimal=","
    )

    print()
    print(
        f"Ergebnis gespeichert als: "
        f"{ergebnis_datei}"
    )

    # Alle Messwerte plotten; nur die Achsenbeschriftung auf 5 Minuten setzen.
    df_plot = df_akt.copy()
    df_plot["Zeit"] = pd.to_timedelta(df_plot["Zeit"])
    startzeit = pd.to_timedelta(df_akt["Zeit"].iloc[0])
    df_plot["Messzeit_min"] = (
        df_plot["Zeit"] - startzeit
    ).dt.total_seconds() / 60

    #Subplotting: 1 Zeit-Achse, 4 X-Achsen für CPU, RAM, GPU und GPU-Temperatur 
    fig, axes = plt.subplots(
        4,
        1,
        sharex=True,
        figsize=(15, 9)
    )

    axes[0].plot(
        df_plot["Messzeit_min"],
        df_plot["CPU[%]"],
        color="tab:blue",
        linewidth=1.2
    )
    axes[0].set_ylabel("CPU [%]")
    axes[0].set_ylim(0, 100)
    axes[0].set_title("Systemauslastung")
    axes[0].grid(True, alpha=0.3)

    axes[1].plot(
        df_plot["Messzeit_min"],
        df_plot["GPU[%]"],
        color="tab:orange",
        linewidth=1.2
    )
    axes[1].set_ylabel("GPU [%]")
    axes[1].set_ylim(0, 100)
    axes[1].grid(True, alpha=0.3)

    axes[2].plot(
        df_plot["Messzeit_min"],
        df_plot["RAM_MB"],
        color="tab:green",
        linewidth=1.2
    )
    axes[2].set_ylabel("RAM_[MB]")
    #axes[2].set_xlabel("Uhrzeit")
    axes[2].grid(True, alpha=0.3)

    axes[3].plot(
            df_plot["Messzeit_min"],
            df_plot["GPU_TEMP_C"],
            color="tab:green",
            linewidth=1.2
        )
    axes[3].set_ylabel("GPU Temperatur [°C]")
    axes[3].set_xlabel("Uhrzeit")
    axes[3].grid(True, alpha=0.3)

    tick_minuten = range(
        0,
        int(df_plot["Messzeit_min"].max()) + 1,
        5
    )
    axes[3].set_xticks(
        list(tick_minuten)
    )
    axes[3].set_xticklabels(
        [
            (
                pd.Timestamp("2000-01-01")
                + startzeit
                + pd.to_timedelta(minute, unit="m")
            ).strftime("%H:%M")
            for minute in tick_minuten
        ],
        rotation=45,
        ha="right"
    )
    fig.tight_layout()

    #Aktuelle Zeit im Dateinamen inkrementieren
    datumsstempel = date.today().isoformat()
    ausgabe_datei = Path(
        f"jetson_allComponents_{datumsstempel}.png"
    )
    nummer = 2
    while ausgabe_datei.exists():
        ausgabe_datei = Path(
            f"jetson_allComponents_{datumsstempel}_{nummer}.png"
        )
        nummer += 1

    plt.savefig(
        ausgabe_datei,
        dpi=300
    )

    print(
        f"Graph gespeichert als: "
        f"{ausgabe_datei}"
    )

    plt.show()

if __name__ == "__main__":
    main()
