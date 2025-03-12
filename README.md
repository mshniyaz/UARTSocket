# WebSocket UART

This project provides a method to pipe UART data over the web using WebSockets. The host PC connects to a UART port, creates a WebSocket server to serve the UART data over the network, and allows a client PC to access and interact with it as if it is being viewed from serial communication programs like minicom.

`TODO: Connection is currently not secure, need to switch to wss protocol?`

## Requirements

- Python version `3.10.12` (Other python versions have not been tested) and `pip`
- Python libraries in requirements.txt
  - `asyncio`
  - `websockets`
  - `pyserial`

## Installation

1. Clone the repository and cd into it
2. Install the required dependencies
   ```sh
   pip install -r requirements.txt
   ```

## Usage

### Starting the WebSocket Server

1. Run the `main.py` script and select the option to start the WebSocket server:
    ```sh
    python src/main.py
    ```
2. Select option `1` to start the WebSocket server.
3. Note down the hostname of the current machine
   ```sh
   hostname -I # For UNIX based systems
   ipconfig # For Windows, check output for IPv4 address
   ```

### Connecting as a Client

1. Run the `main.py` script and select the option to connect as a client:
    ```sh
    python src/main.py
    ```
2. Select option `2` to connect as a client.
3. Enter the server address, UART port path, and baud rate when prompted.

## Configuration

The WebSocket server configuration is stored in `src/config.py`, port and host IP can be changed accordingly:
```python
WEBSOCKET_HOST = '0.0.0.0'  # Bind to all network interfaces for remote access
WEBSOCKET_PORT = 8765
```