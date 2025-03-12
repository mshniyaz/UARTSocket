import asyncio
import serial
from websockets import serve
from urllib.parse import parse_qs
from config import WEBSOCKET_HOST, WEBSOCKET_PORT

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
            # Below await seriously slows down reading from UART
            # await asyncio.sleep(0.001)

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