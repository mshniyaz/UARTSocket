import asyncio, sys, os
from websockets import connect
from config import WEBSOCKET_PORT

# Platform dependent disabling of terminal echo
import os
if os.name == 'nt':  # Windows
    import msvcrt
else:  # Unix-based (Linux, macOS)
    import tty
    import termios

async def clientConnect():
    # Let users configure their connection
    remoteHost = input("Enter the server address (e.g., 192.168.1.100): ").strip()
    uartPort = input("Enter the path to serial port (e.g., /dev/ttyUSB0): ").strip()
    uartBaudrate = None
    while not uartBaudrate:
        try:
            uartBaudrate = int(input("Enter the baud rate (e.g., 115200): ").strip())
        except ValueError:
            print("Invalid baud rate. Please enter an integer")
    hostURI = f"ws://{remoteHost}:{WEBSOCKET_PORT}/uartPort={uartPort}&baudrate={uartBaudrate}"

    # Connect to the WebSocket server given
    async with connect(hostURI) as websocket:
        print(f"Connected to {hostURI}. Type to send data, Ctrl+C to exit.")

        async def readFromServer():
            async for char in websocket:
                if char:
                    # Replace DEL character with a backspace string
                    if ord(char) == 127:
                        char = "\b \b"
                    print(f"{char}", end="", flush=True)

        async def writeToServer():
            # Windows method to read single byte, no echo
            if os.name == 'nt':
                def readChar():
                    return msvcrt.getch().decode()
            # UNIX based systems
            else:
                def readChar():
                    fd = sys.stdin.fileno() # File descriptor for stdin
                    oldSettings = termios.tcgetattr(fd) 
                    try:
                        tty.setraw(fd)  # Disable echo and buffering (temp)
                        return sys.stdin.read(1)
                    finally:
                        termios.tcsetattr(fd, termios.TCSADRAIN, oldSettings)  # Restore old settings

            # Read input character asynchronously and send to server
            loop = asyncio.get_running_loop()
            while True:
                char = await loop.run_in_executor(None, readChar)
                if char:
                    await websocket.send(char)
                await asyncio.sleep(0.05)

        # Start read and write tasks
        readTask = asyncio.create_task(readFromServer())
        writeTask = asyncio.create_task(writeToServer())
        await asyncio.gather(readTask, writeTask)