import re
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

log_file = Path(r"C:\U_M\Studienarbeit\SA_auswertung_profiler_fp16\hw_fp16_logs.txt")
records = []

# Auszug aus Logfile:
# 10-08-2026 22:17:47 RAM 13185/62841MB (lfb 4x4MB) SWAP 0/31420MB (cached 0MB) 
# CPU [0%@729,0%@729,0%@729,1%@729,0%@729,0%@729,0%@729,0%@729,0%@729,0%@729,0%@729,4%@729] 
# GR3D_FREQ 0% cpu@40.468C soc2@37.531C soc0@37.875C gpu@36.562C tj@40.656C soc1@37.312C VDD_GPU_SOC 2390mW/2390mW VDD_CPU_CV 398mW/398mW VIN_SYS_5V0 2612mW/2612mW


time_pattern = re.compile(
    r"^(\d{2}-\d{2}-\d{4})\s+(\d{2}:\d{2}:\d{2})"
)

cpu_pattern = re.compile(r"CPU\s*\[([^\]]+)\]")
gpu_pattern = re.compile(r"GR3D_FREQ\s+(\d+)%")

with log_file.open("r", encoding="utf-8", errors="replace") as file:
    for line in file:

        time_match = time_pattern.search(line)
        cpu_match = cpu_pattern.search(line)
        gpu_match = gpu_pattern.search(line)

        # Zeilen ohne Zeitstempel oder CPU-Werte überspringen
        if not time_match or not cpu_match:
            continue

        date_string = time_match.group(1)
        time_string = time_match.group(2)

        # Datumsformat: MM-DD-YYYY
        timestamp = pd.to_datetime(
            f"{date_string} {time_string}",
            format="%m-%d-%Y %H:%M:%S",
            errors="coerce"
        )

        if pd.isna(timestamp):
            continue

        # Alle prozentualen CPU-Werte extrahieren.
        # Beispiel: 0%@729,0%@729,1%@729
        cpu_values = re.findall(
            r"(\d+(?:\.\d+)?)\s*%",
            cpu_match.group(1)
        )

        if not cpu_values:
            continue

        row = {"Zeit": timestamp}

        for i, value in enumerate(cpu_values, start=1):
            row[f"CPU Kern {i}"] = float(value)
        
        gpu_value = float(gpu_match.group(1)) if gpu_match else None
        row["GPU"] = gpu_value

        records.append(row)

df = pd.DataFrame(records)

if df.empty:
    raise ValueError(
        "Keine gültigen Zeitstempel oder CPU-Werte gefunden."
    )

df = (
    df.sort_values("Zeit")
      .drop_duplicates(subset="Zeit", keep="last")
      .reset_index(drop=True)
)

cpu_columns = [
    column for column in df.columns
    if column.startswith("CPU Kern ")
]

print(df.head())
print(f"\nAnzahl Messungen: {len(df)}")
print(f"Erkannte CPU-Kerne: {len(cpu_columns)}")


# 1. Plot: Zeit auf X-, CPU-Auslastung auf Y-Achse

fig, ax = plt.subplots(figsize=(10, 8))

for core in cpu_columns:
    ax.plot(
        df["Zeit"],
        df[core],
        label=core,
        linewidth=1.2
    )

ax.set_xlabel("Zeit")
ax.set_ylabel("CPU-Kern-Auslastung [%]")
ax.set_title("Auslastung CPU-Kerne")

# Prozentuale Auslastung von 0 bis 100 %
ax.set_ylim(0, 100)

# Lesbare Zeitbeschriftung
locator = mdates.AutoDateLocator()
ax.xaxis.set_major_locator(locator)
ax.xaxis.set_major_formatter(
    mdates.ConciseDateFormatter(locator)
)

ax.grid(True, alpha=0.3)
ax.legend(loc="best", ncol=2)
fig.tight_layout()

ausgabe_datei = Path(
        f"fp16_CPUcores.png"
    )
plt.savefig(
        ausgabe_datei,
        dpi=300
    )

# 2.Plot: Zeit auf X-, GPU-Auslastung auf Y-Achse
fig, ax = plt.subplots(figsize=(10, 8))

ax.plot(
    df["Zeit"],
    df["GPU"],
    label="GPU",
    linewidth=1.2
)

ax.set_xlabel("Zeit")
ax.set_ylabel("GPU-Auslastung [%]")
ax.set_title("Auslastung GPU")

# Prozentuale Auslastung von 0 bis 100 %
ax.set_ylim(0, 100)

# Lesbare Zeitbeschriftung
locator = mdates.AutoDateLocator()
ax.xaxis.set_major_locator(locator)
ax.xaxis.set_major_formatter(
    mdates.ConciseDateFormatter(locator)
)

ax.grid(True, alpha=0.3)
ax.legend(loc="best", ncol=2)
fig.tight_layout()

ausgabe_datei = Path(
        f"fp16_GPU.png"
    )
plt.savefig(
        ausgabe_datei,
        dpi=300
    )


plt.show()
