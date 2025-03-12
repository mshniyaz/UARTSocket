import asyncio
from server import startServer
from client import clientConnect

if __name__ == "__main__":
    print("--------------------------")
    print("Remote UART over websocket")
    print("--------------------------")
    print("Select mode:")
    print("1 - Start WebSocket server as host")
    print("2 - Connect as a client to a WebSocket server")
    choice = input("Enter your choice (1/2): ").strip()
    
    # Route clients and hosts to different entry points
    if choice == "1":
        asyncio.run(startServer())
    elif choice == "2":
        asyncio.run(clientConnect())
    else:
        print("Invalid choice. Exiting.")