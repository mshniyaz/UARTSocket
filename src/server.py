import asyncio
import serial
import websockets
from urllib.parse import parse_qs
import ssl
import pathlib
from configs import WEBSOCKET_HOST, WEBSOCKET_PORT, UART_READ_DELAY

# All communications should be encrypted via WSS (https://websockets.readthedocs.io/en/stable/howto/encryption.html)
# Note that the below is only for testing purposes, deployment should be behind a reverse proxy like nginx/ngrok
# sslContext = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
# localhostPem = pathlib.Path(__file__).resolve().parent / "localhost.pem"
# sslContext.load_cert_chain(localhostPem)

# Keep track of all connections
CLIENTS = set()


async def startServer():
    """
    Start the WebSocket server on the host.
    """
    async with websockets.serve(
        handleWebsocketConnect, WEBSOCKET_HOST, WEBSOCKET_PORT
    ) as server:
        print(f"Started websocket server on {WEBSOCKET_HOST}:{WEBSOCKET_PORT}")
        await server.serve_forever()


async def handleWebsocketConnect(websocket: websockets.ClientConnection):
    """
    Handle the beginning of a websocket connection.
    """

    # Parse the path to extract the UART port and baudrate
    def parsePath(socketPath):
        params = parse_qs(socketPath.lstrip("/").lstrip("?"))
        params = {key: value[0] for key, value in params.items()}
        return params

    params = parsePath(websocket.request.path)
    uartPort = params["uartPort"]
    baudRate = int(params["baudrate"])

    # Ensure no clients are connected to the given UART port
    for clientSocket in CLIENTS:
        if parsePath(clientSocket.request.path)["uartPort"] == uartPort:
            # Terminate the connection, issue a warning
            await websocket.send(
                f"[ERROR] Other client is already connected to {uartPort}\r\n".encode()
            )
            await websocket.close()
            return
    CLIENTS.add(websocket)
    # Note client ID for logging purposes
    clientID = websocket.id

    # Open up the given serial port
    try:
        ser = serial.Serial(uartPort, baudRate, timeout=0)
        print(f"[{clientID}] Opened UART port {uartPort} at {baudRate} baudrate")
    except Exception as e:
        print(f"[{clientID}] Failed to open UART port {uartPort}")
        await websocket.close()
        return

    # Read data from websocket into uart
    async def readFromUART():
        loop = asyncio.get_event_loop()
        while True:
            try:
                # Execute the blocking serial read in a different thread
                waitingBytes = await loop.run_in_executor(None, lambda: ser.in_waiting)
                if waitingBytes > 0:
                    # Read and transmit the raw bytes
                    data = await loop.run_in_executor(None, ser.read, waitingBytes)
                    await websocket.send(data)
            except Exception as e:
                print(f"[{clientID}] Error reading from UART: {e}")
                break
            # Length of await determines CPU usage and UART speed
            await asyncio.sleep(UART_READ_DELAY)

    # Write data from websocket into UART
    async def writeToUART():
        async for char in websocket:
            ser.write(char.encode())

    # Start the read and write tasks
    readTask = asyncio.create_task(readFromUART())
    writeTask = asyncio.create_task(writeToUART())
    try:
        await asyncio.gather(readTask, writeTask)
    except websockets.exceptions.ConnectionClosedError as e:
        print(f"[{clientID}] Connection closed")
        # Termianate tasks
        readTask.cancel()
        writeTask.cancel()
    except Exception as w:
        print(f"[{clientID}] Unexpected {type(e).__name__}: {e}\r")
    finally:
        # Cleanup
        ser.close()
        CLIENTS.remove(websocket)
        await websocket.close()


if __name__ == "__main__":
    print("----------------")
    print("Remote UART host")
    print("----------------")
    # Start the server
    asyncio.run(startServer())
