import asyncio
import serial
import sys
from urllib.parse import parse_qs
from websockets import serve, connect

# Platform dependent disabling of terminal echo
import os
if os.name == 'nt':  # Windows
    import msvcrt
else:  # Unix-based (Linux, macOS)
    import tty
    import termios

# Websocket Configs
WEBSOCKET_HOST = '0.0.0.0' # Bind to all network interfaces for remote access
WEBSOCKET_PORT = 8765

async def startServer():
    """
    Start the WebSocket server on the host.
    """
    async with serve(handleWebsocketConnect, WEBSOCKET_HOST, WEBSOCKET_PORT) as server:
        print("Started websocket server")
        await server.serve_forever()

async def handleWebsocketConnect(websocket):
    """
    Handle the beginning of a websocket connection.
    """
    # Parse the path to extract the UART port and baudrate
    params = parse_qs(websocket.request.path.lstrip("/"))
    params = {key: value[0] for key, value in params.items()}
    uartPort = params['uartPort']
    baudRate = int(params['baudrate'])

    try:
        print("Updating UART port")
        ser = serial.Serial(uartPort, baudRate, timeout=0)
        print(f"[CLIENT] Opened UART port {uartPort} at {baudRate} baudrate")
    except Exception as e:
        print(f"[CLIENT] Failed to open UART port {uartPort}: {e}")
        await websocket.close()
        return

    # Read data from websocket into uart
    async def readFromUART():
        loop = asyncio.get_event_loop()
        while True:
            char = await loop.run_in_executor(None, ser.read, 1)
            try:
                if char:
                    char = char.decode()
                    await websocket.send(char)
            except:
                print("[CLIENT] Error reading from UART")
            # Below await slows down reading from UART
            await asyncio.sleep(0.0001)

    # Write data from websocket into UART
    async def writeToUART():
        async for char in websocket:
            ser.write(char.encode())

    # Start the read and write tasks
    readTask = asyncio.create_task(readFromUART())
    writeTask = asyncio.create_task(writeToUART())
    try:
        await asyncio.gather(readTask, writeTask)
    finally:
        ser.close()
        await websocket.close()

async def clientConnect(hostURI):
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

if __name__ == "__main__":
    print("Select mode:")
    print("1 - Start WebSocket server as host")
    print("2 - Connect as a client to a WebSocket server")
    choice = input("Enter your choice (1/2): ").strip()
    
    # Route clients and hosts to different entry points
    if choice == "1":
        asyncio.run(startServer())
    elif choice == "2":
        # Let users configure their connection
        remoteHost = input("Enter the server address (e.g., 192.168.1.100): ").strip()
        uartPort = input("Enter the path to serial port (e.g., /dev/ttyUSB0): ").strip()
        uartBaudrate = None
        while not uartBaudrate:
            try:
                uartBaudrate = int(input("Enter the baud rate (e.g., 115200): ").strip())
            except ValueError:
                print("Invalid baud rate. Please enter an integer")

        # Construct connection URI
        hostURI = f"ws://{remoteHost}:{WEBSOCKET_PORT}/uartPort={uartPort}&baudrate={uartBaudrate}"
        asyncio.run(clientConnect(hostURI))
    else:
        print("Invalid choice. Exiting.")