#!/bin/bash

OUTPUT_DIR="$HOME/Systemmonitor"
mkdir -p "$OUTPUT_DIR"
DATE=$(date +"%Y-%m-%d")
OUTPUT_FILE="$OUTPUT_DIR/Systemmonitor_Jetson_$DATE.csv"

START_MIN=$((8*60))
END_MIN=$((20*60))    

if [ ! -f "$OUTPUT_FILE" ]; then
    echo "Zeit;CPU[%];RAM_MB;GPU[%];GPU_TEMP_C" > "$OUTPUT_FILE"
fi

get_current_min() {
    echo $(( 10#$(date +%H) * 60 + 10#$(date +%M) ))
}

tegrastats --interval 200 | while read -r line; do
    NOW_MIN=$(get_current_min)

    if [ "$NOW_MIN" -ge "$END_MIN" ] || [ "$NOW_MIN" -lt "$START_MIN" ]; then
        break
    fi

    TIME=$(date +"%H:%M:%S.%3N")

    CPU=$(echo "$line" | grep -o 'CPU \[[^]]*\]' | grep -o '[0-9]\+%' | tr -d '%' | awk '{sum+=$1; count++} END {if (count>0) print sum/count; else print 0}')
    RAM_MB=$(echo "$line" | grep -o 'RAM [0-9]\+/[0-9]\+MB' | grep -o '[0-9]\+' | head -n1)
    GPU_UTIL=$(echo "$line" | grep -o 'GR3D_FREQ [0-9]\+%' | grep -o '[0-9]\+' | head -n1)
    [ -z "$GPU_UTIL" ] && GPU_UTIL=0
    GPU_TEMP=$(echo "$line" | grep -o 'gpu@[0-9.]\+C' | grep -o '[0-9.]\+')
    [ -z "$GPU_TEMP" ] && GPU_TEMP=0

    echo "$TIME;$CPU;$RAM_MB;$GPU_UTIL;$GPU_TEMP" >> "$OUTPUT_FILE"
done