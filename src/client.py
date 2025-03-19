import asyncio
import sys
import os
import argparse
import websockets

# Platform dependent disabling of terminal echo
if os.name == "nt":  # Windows
    import msvcrt
else:  # Unix-based (Linux, macOS)
    import tty
    import termios

# Encrypt all communications via WSS (only on localhost)
# Note that the below is only for testing purposes, deployment should be behind a reverse proxy like nginx/ngrok
# import ssl
# import pathlib
# sslContext = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
# localhostPem = pathlib.Path(__file__).resolve().parent / "localhost.pem"
# sslContext.load_verify_locations(localhostPem)


async def clientConnect(ipAddressPort: str, serialPort: str, baudRate: int, sslDisable:bool):
    """
    Entrypoint for clients, connect to the host to send/receive UART data.
    """
    # Connect to the WebSocket server given
    protocol = "ws" if sslDisable else "wss" 
    hostURI = f"{protocol}://{ipAddressPort}?uartPort={serialPort}&baudrate={baudRate}"
    try:
        print(f"Attempting to connect to {hostURI}")
        websocket = await websockets.connect(hostURI)
        print(f"Connection success. Type to send data, Ctrl+C to exit.")

        async def readFromServer():
            async for data in websocket:
                print(f"{data.decode()}", end="", flush=True)

        async def writeToServer():
            # Windows method to read single byte, no echo
            if os.name == "nt":

                def readChar():
                    return msvcrt.getch().decode()

            # Equivalent method for UNIX based systems
            else:
                def readChar():
                    fd = sys.stdin.fileno()  # File descriptor for stdin
                    oldSettings = termios.tcgetattr(fd)
                    try:
                        tty.setraw(fd)  # Disable echo and buffering (temp)
                        return sys.stdin.read(1)
                    finally:
                        # Restore old settings
                        termios.tcsetattr(fd, termios.TCSADRAIN, oldSettings)

            # Await input character on different thread and send to server
            loop = asyncio.get_running_loop()
            while True:
                char = await loop.run_in_executor(None, readChar)
                if char:
                    # Map ASCII DEL (0x7F) to Backspace (0x08)
                    if char == '\x7f':
                        char = '\x08'
                    await websocket.send(char)

        # Start read and write tasks
        readTask = asyncio.create_task(readFromServer())
        writeTask = asyncio.create_task(writeToServer())
        await asyncio.gather(readTask, writeTask)

    # Connection errors
    except (
        websockets.exceptions.InvalidURI,
        websockets.exceptions.InvalidHandshake,
    ) as e:
        print(f"Failed to connect to {hostURI}")
        print(f"Unexpected {type(e).__name__}: {e}\r")
    except ConnectionResetError:
        print("Server closed connection, possible SSL issues")
    # Closing the websocket normally
    except websockets.exceptions.ConnectionClosedOK:
        await websocket.close()
        sys.exit("Websocket connection closed")
    # Other errors
    except Exception as e:
        print(f"Unexpected {type(e).__name__}: {e}\r")
    # Cleanup
    finally:
        sys.exit("Websocket connection closed")


if __name__ == "__main__":
    print("------------------")
    print("Remote UART client")
    print("------------------")

    # Parse CLI inputs
    parser = argparse.ArgumentParser(
        description="WebSocket client to access serial devices"
    )
    # Required arguments
    parser.add_argument(
        "ip_address_port",
        help="IP address and port of the host computer to connect to (e.g. localhost:8765)",
    )
    parser.add_argument(
        "serial_port",
        help="Path to the serial port on the host (e.g., /dev/ttyUSB0 or COM3)",
    )
    # Optional arguments
    parser.add_argument(
        "-b",
        "--baud",
        type=int,
        default=115200,
        help="Baud rate for the serial connection (default: 115200)",
    )
    parser.add_argument(
        "-d",
        "--disable_ssl",
        action='store_true',
        help="Flag specifying if SSL encryption should be disabled. Should only be used for testing on localhost"
    )
    args = parser.parse_args()

    # Begin connecting the client
    asyncio.run(clientConnect(args.ip_address_port, args.serial_port, args.baud, args.disable_ssl))
