#!/bin/bash

OUTPUT_DIR="$HOME/Systemmonitor"
mkdir -p "$OUTPUT_DIR"
DATE=$(date +"%Y-%m-%d")
OUTPUT_FILE="$OUTPUT_DIR/Systemmonitor_Jetson_$DATE.csv"
START_MIN=$((8*60))
END_MIN=$((20*60))

if [ ! -f "$OUTPUT_FILE" ]; then
    echo "Zeit;CPU[%];RAM_MB;GPU[%];GPU_FREQ_MHz" > "$OUTPUT_FILE"
fi

current_minutes() {
    H=$(date +"%H")
    M=$(date +"%M")
    echo $((10#$H * 60 + 10#$M))
}

collect_metrics() {
    # Abfrage-Intervall für tegrastats: 200ms (5 Hz) für präzise Peaks
    tegrastats --interval 200 | while read -r line; do
        NOW_MIN=$(current_minutes)
        if [ "$NOW_MIN" -lt "$START_MIN" ] || [ "$NOW_MIN" -ge "$END_MIN" ]; then
            break
        fi

        TIME=$(date +"%H:%M:%S.%3N")

        # 1. CPU-Auslastung aus tegrastats aggregieren (Format z.B.: RAM 2000/7800MB ... CPU [10%     	@1400,20%@1400,...])
        # Durschnitt aller CPU-Cores berechnen:
        CPU=$(echo "$line" | grep -o 'CPU \[[^]]*\]' | grep -o '[0-9]\+%' | tr -d '%' | awk '{sum+=$1; count++} END {if (count>0) print sum/count; else print 0}')

        # 2. Echten RAM-Verbrauch in MB aus tegrastats extrahieren (Format: RAM 3500/7764MB)
        RAM_MB=$(echo "$line" | grep -o 'RAM [0-9]\+/[0-9]\+MB' | grep -o '[0-9]\+' | head -n1)

        # 3. GPU-Auslastung (%) sauber isolieren (Format: GR3D_FREQ 45%@...)
        GPU_UTIL=$(echo "$line" | grep -o 'GR3D_FREQ [0-9]\+%' | grep -o '[0-9]\+' | head -n1)
        [ -z "$GPU_UTIL" ] && GPU_UTIL=0

        # 4. Aktueller GPU-Takt (MHz)
        GPU_FREQ=$(echo "$line" | grep -o 'GR3D_FREQ [0-9]\+%@[0-9]\+' | cut -d'@' -f2)
        [ -z "$GPU_FREQ" ] && GPU_FREQ=0

        echo "$TIME;$CPU;$RAM_MB;$GPU_UTIL;$GPU_FREQ" >> "$OUTPUT_FILE"
    done
}

while true; do
    NOW_MIN=$(current_minutes)

    if [ "$NOW_MIN" -ge "$START_MIN" ] && [ "$NOW_MIN" -lt "$END_MIN" ]; then
        collect_metrics
    else
        sleep 60
    fi
done