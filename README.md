# WebSocket UART

This project provides a method to pipe UART data over the web using WebSockets. The host PC connects to a UART port, creates a WebSocket server to serve the UART data over the network, and allows a client PC to access and interact with it as if it is being viewed from serial communication programs like minicom.

`TODO: Connection is currently not secure, need to switch to wss protocol?`

## Requirements

- Python version `3.10.12` (Other python versions have not been tested) and `pip`
- Python libraries in requirements.txt
  - `asyncio`
  - `websockets`
  - `pyserial`

## Setup

## Setup

1. Navigate to the project directory:
    ```sh
    cd /home/niyaz/Desktop/UARTSocket
    ```

2. Install the required Python libraries:
    ```sh
    pip install -r requirements.txt
    ```

3. Find the current IP address:
    ```sh
    hostname -I # UNIX based systems
    ipconfig # For Windows, check output for IPv4 address
    ```

4. Generate keys for use in WSS protocol with the below command, which stores the keys in `./src/keys`. Replace `<your-ip>` with your IP address:
    ```sh
    mkdir -p ./src/keys
    openssl req -newkey rsa:2048 -new -nodes -x509 -days 3650 -keyout ./src/keys/key.pem -out ./src/keys/cert.pem -subj "/CN=localhost" -addext "subjectAltName=IP:127.0.0.1, IP:<your-ip>"
    ```

## Usage

### Starting the WebSocket Server

1. Run the `main.py` script and select the option to start the WebSocket server:
    ```sh
    python src/main.py
    ```
2. Select option `1` to start the WebSocket server.
3. Note down the IP address of the host machine (instructions in setup)

### Connecting as a Client

1. Run the `main.py` script and select the option to connect as a client:
    ```sh
    python src/main.py
    ```
2. Select option `2` to connect as a client.
3. Enter the server address, UART port path, and baud rate when prompted.

**NOTE**: If serial communication programs like minicom are listening to the serial device on the host, clients will be unable to intercept the UART data. 

## Configuration

The WebSocket server configuration is stored in `src/config.py`, port and host IP can be changed accordingly:
```python
WEBSOCKET_HOST = '0.0.0.0'  # Bind to all network interfaces for remote access
WEBSOCKET_PORT = 8765
```