import socket
import threading
import re
from viseme_generator import GenerateVideoAndAudio
from PyQt5 import QtWidgets
import sys
from play_video import VideoPlayer

# Server setup
server_ip = ''  # Listen on all available interfaces
server_port = 12345 # Your port
buffer_size = 1024  # Adjust based on the size of data you expect

app = QtWidgets.QApplication(sys.argv)
player = VideoPlayer()
player.show()

def play_video_test(): 
    app.exec_()
    player.play_video("video/2.mp4")
    print("Callback in main thread: Process completed.")


def handle_client(client_socket, address):
    print(f"Connected to {address}")
    try:
        while True:
            # Receiving data from the client
            data = client_socket.recv(4096).decode('utf-8')
            if not data:
                break  # Break the loop if data is not received
            
            generateVideoAndAudio = GenerateVideoAndAudio(play_video_test)

            if "beff-mode" in data: 
                generateVideoAndAudio
                return

            if "ssml" in data:
                print(f"Raw data {address}: {data}")
                extracted_strings = re.findall(r"<speak>(.*)</speak>", data)
                print(f"Received from {address}: {extracted_strings}")
                if(isinstance(extracted_strings, (list))):
                    extracted_strings = extracted_strings[0].replace("\\n","")
                else:
                    extracted_strings = extracted_strings.replace("\\n","")
                print(f"Cleaned up: {address}: {extracted_strings}")
                extracted_strings = extracted_strings.replace("\\", "")
                print(f"Cleaned up 2: {address}: {extracted_strings}")
                generateVideoAndAudio.generateViseme(extracted_strings)
                # print(f"Raw Data: {data}")

            # Send acknowledgement back to the client
            client_socket.send("Data received".encode('utf-8'))

            # Optional: Break if a specific termination message is received
            if data == 'close':
                print(f"Closing connection with {address} as requested.")
                break

    finally:
        # Close the client socket
        client_socket.close()
        print(f"Connection with {address} closed.")

def start_server():
    host = server_ip  # Listen on all network interfaces
    port = 12345      # Port to listen on (non-privileged ports are > 1023)

    # Create socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Bind the socket to the address and port
    server_socket.bind((host, port))
    
    # Listen for incoming connections
    server_socket.listen(5)
    print(f"Listening on {host}:{port}...")

    try:
        while True:
            # Accept an incoming connection
            client_socket, address = server_socket.accept()
            
            # Start a new thread to handle this client
            client_thread = threading.Thread(target=handle_client, args=(client_socket, address))
            client_thread.start()

    except KeyboardInterrupt:
        print("Server is shutting down.")
    finally:
        server_socket.close()
        print("Server shut down completely.")


if __name__ == '__main__':
    start_server()
    # while True:
    #     print("While loop")
    #     play_video_test()
    #     strq = input()

# sys.exit(app.exec_())
