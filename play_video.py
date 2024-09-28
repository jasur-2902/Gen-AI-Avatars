import sys
import os
from PyQt5 import QtWidgets
import vlc

class VideoPlayer(QtWidgets.QMainWindow):
    def __init__(self):
        super(VideoPlayer, self).__init__()
        print("Video Player Class")
        self.setWindowTitle("Video Player")
        self.setGeometry(100, 100, 200, 200)  # Set the geometry of the main window

        # Create a basic video player widget
        self.videoframe = QtWidgets.QFrame(self)
        self.setCentralWidget(self.videoframe)
        
        # VLC player
        self.vlc_instance = vlc.Instance()
        self.player = self.vlc_instance.media_player_new()

        # Set the player window
        self.player.set_nsobject(int(self.videoframe.winId()))

    def play_video(self, path):
        if self.player.is_playing():
            self.player.stop()  # Stop the current video if playing
            print("Stopping previous playyer")
        media = self.vlc_instance.media_new(path)
        self.player.set_media(media)
        self.player.play()
        print("Playing")

    def closeEvent(self, event):
        self.player.stop()
        self.vlc_instance.release()
        super(VideoPlayer, self).closeEvent(event)

# Ensure the VLC library path is set
vlc_lib_path = "/Applications/VLC.app/Contents/MacOS/lib"
os.environ["DYLD_LIBRARY_PATH"] = vlc_lib_path + ":" + os.environ.get("DYLD_LIBRARY_PATH", "")

# # app = QtWidgets.QApplication(sys.argv)


# # sys.exit(app.exec_())


# import os
# from PyQt5 import QtCore, QtWidgets, QtGui
# import vlc

# class VideoPlayer(QtWidgets.QMainWindow):
#     video_signal = QtCore.pyqtSignal(str)  # Define a signal that carries a string

#     def __init__(self):
#         super(VideoPlayer, self).__init__()
#         self.setWindowTitle("Video Player")
#         self.setGeometry(100, 100, 640, 480)

#         self.videoframe = QtWidgets.QFrame(self)
#         self.setCentralWidget(self.videoframe)
        
#         self.vlc_instance = vlc.Instance()
#         self.player = self.vlc_instance.media_player_new()
#         self.player.set_nsobject(int(self.videoframe.winId()))

#         self.video_signal.connect(self.play_video)  # Connect signal to slot

#     def play_video(self, path):
#         if self.player.is_playing():
#             self.player.stop()
#         media = self.vlc_instance.media_new(path)
#         self.player.set_media(media)
#         self.player.play()

#     def closeEvent(self, event):
#         self.player.stop()
#         self.vlc_instance.release()
#         super(VideoPlayer, self).closeEvent(event)
