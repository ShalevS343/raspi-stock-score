#!/usr/bin/env python3
"""rfcomm-server.py

Simple server application that uses RFCOMM sockets.

"""

# Import necessary modules
from lcd_model import process_message, scroll_stocks  # Custom functions for processing and displaying messages on the LCD
import bluetooth  # PyBluez library for Bluetooth communication

# Create a Bluetooth socket using RFCOMM protocol
server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)

# Bind the socket to any available port
server_sock.bind(("", bluetooth.PORT_ANY))

# Listen for incoming connections with a backlog of 1
server_sock.listen(1)

# Get the port number assigned to the socket
port = server_sock.getsockname()[1]

# Define a UUID for the Bluetooth service
uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"

# Advertise the Bluetooth service with the given UUID and Serial Port Profile
bluetooth.advertise_service(server_sock, "SampleServer", service_id=uuid,
                            service_classes=[uuid, bluetooth.SERIAL_PORT_CLASS],
                            profiles=[bluetooth.SERIAL_PORT_PROFILE],
                            )

# Print message to indicate the server is waiting for a connection
print("Waiting for connection on RFCOMM channel", port)

# Initialize the LCD display with a start message
scroll_stocks('init_start')

try:
    # Main loop to handle incoming connections
    while True:
        # Accept an incoming connection
        client_sock, client_info = server_sock.accept()
        print("Accepted connection from", client_info)

        try:
            # Loop to receive data from the connected client
            while True:
                data = client_sock.recv(1024)  # Receive data (up to 1024 bytes) from the client
                if not data:
                    break  # If no data is received, break out of the loop
                message = data.decode('utf-8')  # Decode the received data to a string
                message = message.strip('\n')  # Remove any trailing newline characters
                message = message[:-1]  # Remove the last character (assuming it's a delimiter)
                process_message(message)  # Process the received message using a custom function
        except OSError:
            pass  # Ignore socket errors and continue

        print("Disconnected from", client_info)
        client_sock.close()  # Close the client socket

except KeyboardInterrupt:
    pass  # Handle keyboard interrupt (Ctrl+C) gracefully

finally:
    server_sock.close()  # Ensure the server socket is closed on exit
    print("All done.")
