#!/bin/bash

# This script generates a virtual serial device which can be used to test UART
# communication over websockets when a physical serial device isn't available.
# One of the serial ports continuously transmits time passed since script start.
# A host can then serve UART data from this serial port to a web client, who can verify the output.

# Create pair of serial devices using socat
socat -d -d pty,raw,echo=0 pty,raw,echo=0 > /tmp/socat_output.txt 2>&1 &
sleep 1

# Grep to get 2 pseudo terminals
SOCAT_OUTPUT=$(cat /tmp/socat_output.txt)
PTY1=$(echo "$SOCAT_OUTPUT" | grep -o '/dev/pts/[0-9]*' | sed -n '1p')
PTY2=$(echo "$SOCAT_OUTPUT" | grep -o '/dev/pts/[0-9]*' | sed -n '2p')
printf "Created PTY devices: $PTY1 and $PTY2.\r\n"
printf "Listen on $PTY1 to see output.\r\n"

# Continuously write the current epoch time to the second PTY every 3 seconds
START_EPOCH=$(date +%s)
while true; do
    TIME_PASSED=$(($(date +%s)-START_EPOCH))
    echo -e "$TIME_PASSED seconds have passed\r" > $PTY2
    sleep 3
done &

# Cleanup and run the startup script
rm "/tmp/socat_output.txt"
DIR="$( cd "$( dirname "$0" )" && pwd )"
$DIR/startup.sh