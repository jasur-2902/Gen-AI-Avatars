import sys
import os
from PyQt5 import QtWidgets
import vlc

class VideoPlayer(QtWidgets.QMainWindow):
    def __init__(self):
        super(VideoPlayer, self).__init__()
        self.setWindowTitle("Video Player")
        self.setGeometry(100, 100, 640, 480)  # Set the geometry of the main window

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
        media = self.vlc_instance.media_new(path)
        self.player.set_media(media)
        self.player.play()

    def closeEvent(self, event):
        self.player.stop()
        self.vlc_instance.release()
        super(VideoPlayer, self).closeEvent(event)

# Ensure the VLC library path is set
vlc_lib_path = "/Applications/VLC.app/Contents/MacOS/lib"
os.environ["DYLD_LIBRARY_PATH"] = vlc_lib_path + ":" + os.environ.get("DYLD_LIBRARY_PATH", "")

app = QtWidgets.QApplication(sys.argv)
player = VideoPlayer()
player.show()

player.play_video("video/downloaded.webm")


new_video_path = "video/3.mp4"
player.play_video(new_video_path)

sys.exit(app.exec_())
