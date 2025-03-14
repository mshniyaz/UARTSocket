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

### For hosts

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

5. Share the public key `cert.pem` with clients 

### For clients

Store the `cert.pem` file given by the host in src/keys/ (NOTE: This is inconvenient and there should be a method to fix it) 

## Usage

### Starting the WebSocket Server

Run the below command, follow the instructions to :
```sh
python src/server.py -h
```

### Connecting as a Client

1. Run the below command:
    ```sh
    python src/client.py -h
    ```

2. Read its output to connect to the correct device and serial port. For example:
    ```sh
    # Connect to IP 20.17.138.90, read serial device /tty/USB0 at baud of 2 Mb/s
    python src/client.py 20.17.138.90 /tty/USB0 -b 2000000 
    ```

**NOTE**: If serial communication programs like minicom are listening to the serial device on the host, clients will be unable to intercept the UART data. 

## Configuration

The WebSocket server configuration is stored in `src/config.py`, port and host IP can be changed accordingly.