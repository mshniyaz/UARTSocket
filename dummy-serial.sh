#!/bin/bash

# This script generates a virtual serial device which can be used to test UART
# communication over websockets when a physical serial device isn't available.
# One of the serial ports continuously transmits time passed since script start.
# A host can then serve UART data from this serial port to a web client, who can verify the output.

# Create pair of serial devices using socat
socat -d -d pty,raw,echo=0 pty,raw,echo=0 > /tmp/socat_output.txt 2>&1 &
sleep 1

# Grep to get 2 pseudo terminals (platform specific)
SOCAT_OUTPUT=$(cat /tmp/socat_output.txt)
OS_TYPE=$(uname)
if [ "$OS_TYPE" == "Linux" ]; then
    PTY1=$(echo "$SOCAT_OUTPUT" | grep -o '/dev/pts/[0-9]*' | sed -n '1p')
    PTY2=$(echo "$SOCAT_OUTPUT" | grep -o '/dev/pts/[0-9]*' | sed -n '2p')
else 
    # Assume macos
    PTY1=$(echo "$SOCAT_OUTPUT" | grep -o '/dev/tty[sf][0-9]*' | sed -n '1p')
    PTY2=$(echo "$SOCAT_OUTPUT" | grep -o '/dev/tty[sf][0-9]*' | sed -n '2p')
fi
printf "Created PTY devices: $PTY1 and $PTY2.\r\n"
printf "Listen on $PTY1 to see output.\r\n"

# Continuously write the current epoch time to the second PTY every 3 seconds
START_EPOCH=$(date +%s)
while true; do
    TIME_PASSED=$(($(date +%s)-START_EPOCH))
    echo -e "${TIME_PASSED}s passed\r" > $PTY2
    sleep 1
done &