import asyncio
import serial
import websockets
from urllib.parse import parse_qs # Used to parse data passed from client to server
import ssl, pathlib # Used to encrypt connections with T
from configs import WEBSOCKET_HOST, WEBSOCKET_PORT, UART_READ_DELAY

# All communications should be encrypted via WSS (https://websockets.readthedocs.io/en/stable/howto/encryption.html)
sslContext = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
keysDir = pathlib.Path(__file__).resolve().parent / 'keys'
sslContext.load_cert_chain(certfile=keysDir / 'cert.pem', keyfile=keysDir / 'key.pem')

async def startServer():
    """
    Start the WebSocket server on the host.
    """
    async with websockets.serve(handleWebsocketConnect, WEBSOCKET_HOST, WEBSOCKET_PORT, ssl=sslContext) as server:
        print("Started websocket server.")
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
        ser = serial.Serial(uartPort, baudRate, timeout=0)
        print(f"[CLIENT] Opened UART port {uartPort} at {baudRate} baudrate")
    except Exception as e:
        print(f"[CLIENT] Failed to open UART port {uartPort}")
        await websocket.close()
        return # sys.exit here?

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
        print(f"[CLIENT] Connection closed")
    except Exception as w:
        print(f"Unexpected error: {e}")
    finally:
        # Cleanup
        ser.close()
        await websocket.close()

if __name__ == "__main__":
    print("----------------")
    print("Remote UART host")
    print("----------------")
    # Start the server
    asyncio.run(startServer())