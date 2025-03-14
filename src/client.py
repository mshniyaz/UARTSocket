import asyncio
import  sys, os, argparse
import websockets
import ssl, pathlib # Used to encrypt connections with TLS
from configs import WEBSOCKET_PORT

# Platform dependent disabling of terminal echo
import os
if os.name == 'nt':  # Windows
    import msvcrt
else:  # Unix-based (Linux, macOS)
    import tty
    import termios

# Encrypt all communications via WSS
sslContext = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
keysDir = pathlib.Path(__file__).resolve().parent / 'keys'
sslContext.load_verify_locations(cafile=keysDir / 'cert.pem')

async def clientConnect(ipAddress, serialPort, baudRate):
    """
    Entrypoint for clients, connect to the host to send/receive UART data.
    """
    # Connect to the WebSocket server given
    hostURI = f"wss://{ipAddress}:{WEBSOCKET_PORT}/uartPort={serialPort}&baudrate={baudRate}"
    try:
        websocket = await websockets.connect(hostURI, ssl=sslContext)
        print(f"Connected to {hostURI}. Type to send data, Ctrl+C to exit.")

        async def readFromServer():
            async for char in websocket:
                if char:
                    # Replace DEL character with a backspace string
                    if ord(char) == 127:
                        char = "\b \b"
                    # Print all characters received from the server
                    print(f"{char}", end="", flush=True)

        async def writeToServer():
            # Windows method to read single byte, no echo
            if os.name == 'nt':
                def readChar():
                    return msvcrt.getch().decode()
            # Equivalent method for UNIX based systems
            else:
                def readChar():
                    fd = sys.stdin.fileno() # File descriptor for stdin
                    oldSettings = termios.tcgetattr(fd) 
                    try:
                        tty.setraw(fd)  # Disable echo and buffering (temp)
                        return sys.stdin.read(1)
                    finally:
                        termios.tcsetattr(fd, termios.TCSADRAIN, oldSettings)  # Restore old settings

            # Await input character on different thread and send to server
            loop = asyncio.get_running_loop()
            while True:
                char = await loop.run_in_executor(None, readChar)
                if char:
                    await websocket.send(char)

        # Start read and write tasks
        readTask = asyncio.create_task(readFromServer())
        writeTask = asyncio.create_task(writeToServer())
        await asyncio.gather(readTask, writeTask)
    except (websockets.exceptions.InvalidURI, websockets.exceptions.InvalidHandshake) as e:
        print(f"Failed to connect to {hostURI}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        await websocket.close()
        sys.exit("Websocket connection closed")
        

if __name__ == "__main__":
    print("------------------")
    print("Remote UART client")
    print("------------------")
    
    # Parse CLI inputs
    parser = argparse.ArgumentParser(description="WebSocket client to access serial devices")
    # Required arguments
    parser.add_argument("ip_address", help="IP address of the host computer to connect to")
    parser.add_argument("serial_port", help="Path to the serial port on the host (e.g., /dev/ttyUSB0 or COM3)")
    # Optional baud rate argument with short and long options
    parser.add_argument("-b", "--baud", type=int, default=115200, help="Baud rate for the serial connection (default: 115200)")
    args = parser.parse_args()

    # Begin connecting the client
    asyncio.run(clientConnect(args.ip_address, args.serial_port, args.baud))