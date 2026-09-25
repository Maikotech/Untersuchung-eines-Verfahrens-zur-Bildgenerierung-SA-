#!/bin/bash

##############################################
# Systemmonitor:
# CPU, RAM, GPU und Netzwerk
##############################################

# Speicherort
OUTPUT_DIR="$HOME/Systemmonitor"
mkdir -p "$OUTPUT_DIR"

DATE=$(date +"%Y-%m-%d")
OUTPUT_FILE="$OUTPUT_DIR/Systemmonitor_$DATE.csv"

# CSV-Kopf erzeugen #
if [ ! -f "$OUTPUT_FILE" ]; then
    echo "Zeit;CPU[%];RAM[%];GPU[%];RX_Bytes;TX_Bytes" > "$OUTPUT_FILE"
fi

while [ "$(date +%H%M)" -lt 2000 ]
do

    HOUR=$(date +%H)

        # Zeit
        TIME=$(date +"%H:%M:%S")

        # CPU-Auslastung
        CPU=$(top -bn1 | grep "Cpu(s)" | awk '{print 100-$8}' | cut -d'.' -f1)

        # RAM-Auslastung aus /proc/meminfo
        RAM=$(awk '/MemTotal/ {total=$2} /MemAvailable/ {avail=$2} END {if(total>0) printf("%.0f", (total-avail)/total*100); else print "0"}' /proc/meminfo)

        # GPU-Auslastung (NVIDIA)
        if command -v tegrastats &> /dev/null
        then
            GPU=$(timeout 2 tegrastats --interval 1000 \
            | grep -o 'GR3D_FREQ [0-9]\+%' \
            | grep -o '[0-9]\+')
        else
            GPU="NA"
        fi

        # Netzwerkinterface auslesen
        INTERFACE=$(ip route | awk '/default/ {print $5}' | head -n1)

        RX=$(cat /sys/class/net/$INTERFACE/statistics/rx_bytes) #Empfangen
        TX=$(cat /sys/class/net/$INTERFACE/statistics/tx_bytes) #Gesendet

        echo "$TIME;$CPU;$RAM;$GPU;$RX;$TX" >> "$OUTPUT_FILE"

    # Messintervall alle 10 sekunden
    sleep 10

done