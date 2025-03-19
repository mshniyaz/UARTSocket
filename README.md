# WebSocket UART

This project provides a method to transmit UART data over the web using WebSockets. The host PC connects to a UART port, creates a WebSocket server to serve the UART data over the network, and allows a client PC to access and interact with it as if using serial communication programs like minicom.

## Requirements

- Python version `3.10.12` (Other Python versions have not been tested) and `pip`
- Python libraries listed in `requirements.txt`:
  - `asyncio`
  - `websockets`
  - `pyserial`
  - All other dependencies are part of python's stdlib

## Usage

### For hosts

1.  Navigate to the project directory:

    ```sh
    cd /home/niyaz/Desktop/UARTSocket
    ```

2.  Install the required Python libraries:

    ```sh
    pip install -r requirements.txt
    ```

3.  Run the server locally. This binds the server to `0.0.0.0`, so the host will listen for all incoming connections on port `8765`. The IP address and port can be configured in `src/configs.py`.

    ```sh
    python ./src/server.py
    ```

4.  To enable encrypted communication via SSL/TLS, a certificate from a trusted third party is required, which typically involves owning a domain and using a reverse proxy such as Nginx or HAProxy. Alternatively, you can use ngrok to obtain a temporary domain (with a valid certificate) that accesses the host via an SSH tunnel. [Install ngrok](https://ngrok.com/docs/getting-started/) and then run the following:

    ```sh
    ngrok http <server_port> # Server port is specified in /src/config.py, 8765 by default

    # Example output
    # Forwarding https://1256-202-51-247-22.ngrok-free.app -> https://localhost:8765
    ```

### For clients

1. Install the required libraries:

   ```sh
   pip install -r requirements.txt
   ```

2. To connect from any machine to a serial port on the host, note the ngrok public domain (e.g., 1256-202-51-247-22.ngrok-free.app, without the https:// URI scheme) and run the following command:

   ```sh
   python src/client.py -h # Displays help for using the client

   # Connect to the host's /dev/ttyUSB serial port via the ngrok proxy, with a baud rate of 4800
   python src/client.py 1256-202-51-247-22.ngrok-free.app /dev/ttyUSB0 -b 4800
   ```

3. When connecting to localhost (for testing purposes), note that there is no self-signed SSL certificate available, so SSL must be disabled.
   ```sh
    # -d flag disables SSL, ensure port is specified
    python src/client.py localhost:8765 /dev/ttyUSB0 -d
   ```

4. Note that SSL must be disabled 

**NOTE**: If serial communication programs like minicom are listening to the serial device on the host, clients will be unable to intercept the UART data.

### Configuration

The WebSocket server configuration is stored in `src/config.py`. The port and host IP can be modified as needed.

## Testing

If you want to test this program but do not have access to a physical serial device, you can use the `dummy-serial.sh` script to create a dummy serial port. This script generates UART data by transmitting the elapsed time since the program started, every second. Note that `socat` is required to run the script.

The script has been tested on macOS and Linux.

```sh
# Run the dummy serial script to create a pseudo-terminal (e.g., /dev/pty/2)
./dummy-serial.sh

# Start the WebSocket server
python src/server.py

# In another terminal, connect the client to the dummy serial port
python src/client.py localhost:<server-port> <serial-port> -b <baud-rate> -d
```
Replace `<server-port>` with the WebSocket server port (default is 8765), `<serial-port>` with the path to the dummy serial port (e.g., `/dev/pty/2`), and `<baud-rate>` with the desired baud rate.