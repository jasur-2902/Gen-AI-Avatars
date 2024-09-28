import sys
import socket
import threading
from PyQt5 import QtWidgets, QtCore
from play_video import VideoPlayer
import re
from viseme_generator import GenerateVideoAndAudio

class VideoApplication(QtWidgets.QApplication):
    play_video_signal = QtCore.pyqtSignal(str)  # Signal to play video

    def __init__(self, argv):
        print("Initing VideoPlayer")
        super().__init__(argv)
        self.player = VideoPlayer()
        self.player.show()
        # self.play_video_signal.connect(self.player.play_video)

    def play_video(self, path):
        self.play_video_signal.emit(path)  # Emit signal from any thread


def play_video_test():
    print("Do nothing")


def handle_client(client_socket, address, app):
    print(f"Connected to {address}")

    try:
        while True:
            data = client_socket.recv(8192).decode('utf-8')
            if not data:
                break

            if "beff-mode" in data: 
                generateVideoAndAudio.set_mode("beff-mode")
                # app.play_video("video/beff.mp4")
                print("\n El Jeffe Mode \n")

            if "jigar-mode" in data: 
                generateVideoAndAudio.set_mode("jigar-mode")
                # app.play_video("video/jigar.mp4")
                print("\n Jigario Mode \n")
                

            if "regular-mode" in data:
                generateVideoAndAudio.set_mode("regular-mode")
                # app.play_video("video/default.mp4")
                print("\n Regular Mode \n")

            if "sarayu-mode" in data:
                generateVideoAndAudio.set_mode("sarayu-mode")
                app.play_video("video/sarayu.mp4")
                print("\n Sarayu Mode \n")

            if "mickey-mode" in data:
                generateVideoAndAudio.set_mode("mickey-mode")
                # app.play_video("video/hulk.mp4")
                print("\n Mickey Mode \n")

            if "ssml" in data:
                print(f"Raw data {address}: {data}")
                extracted_strings = re.findall(r"<speak>(.*)</speak>", data)
                print(f"Received from {address}: {extracted_strings}")
                if(isinstance(extracted_strings, (list))):
                    extracted_strings = extracted_strings[0].replace("\\n","")
                else:
                    extracted_strings = extracted_strings.replace("\\n","")
                # print(f"Cleaned up: {address}: {extracted_strings}")
                extracted_strings = extracted_strings.replace("\\", "")
                # print(f"Cleaned up 2: {address}: {extracted_strings}")
                # generateVideoAndAudio = GenerateVideoAndAudio(play_video_test, "beff-mode")
                generateVideoAndAudio.generateViseme(extracted_strings)
                # app.play_video("video/2.mp4")
                # print(f"Raw Data: {data}")

            # Example of triggering video playback from the worker thread
            

            client_socket.send("Data received".encode('utf-8'))
            if data == 'close':
                print(f"Closing connection with {address} as requested.")
                break
    finally:
        client_socket.close()

def start_server(app):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # server_socket.bind(('192.168.0.229', 12345))
    server_socket.bind(('192.168.0.229', 12345))
    server_socket.listen(5)

    print("Starting Server")

    try:
        while True:
            client_socket, address = server_socket.accept()
            threading.Thread(target=handle_client, args=(client_socket, address, app)).start()
    except KeyboardInterrupt:
        pass
    finally:
        server_socket.close()

if __name__ == '__main__':
    app = VideoApplication(sys.argv)
    print("VideoApplication init")
    generateVideoAndAudio = GenerateVideoAndAudio(play_video_test, "beff-mode")
    server_thread = threading.Thread(target=start_server, args=(app,))
    server_thread.start()
    sys.exit(app.exec_())
