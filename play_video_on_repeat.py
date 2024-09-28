import sys
from PyQt5 import QtWidgets, QtCore, QtMultimedia, QtMultimediaWidgets

class VideoPlayer(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle('Video Player')
        self.setGeometry(100, 100, 800, 600)
        
        self.video_widget = QtMultimediaWidgets.QVideoWidget()
        self.media_player = QtMultimedia.QMediaPlayer(None, QtMultimedia.QMediaPlayer.VideoSurface)
        self.media_player.setVideoOutput(self.video_widget)
        
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.video_widget)
        self.setLayout(self.layout)
        
        # Connect the media status changed signal to the loop video slot
        self.media_player.mediaStatusChanged.connect(self.loop_video)
        
    def play_video(self, path):
        self.media_player.setMedia(QtMultimedia.QMediaContent(QtCore.QUrl.fromLocalFile(path)))
        self.media_player.play()
        
    def loop_video(self, status):
        if status == QtMultimedia.QMediaPlayer.EndOfMedia:
            self.media_player.setPosition(0)
            self.media_player.play()

class VideoApplication(QtWidgets.QApplication):
    play_video_signal = QtCore.pyqtSignal(str)  # Signal to play video

    def __init__(self, argv):
        print("Initing VideoPlayer")
        super().__init__(argv)
        self.player = VideoPlayer()
        self.player.show()
        self.play_video_signal.connect(self.player.play_video)

    def play_video(self, path):
        self.play_video_signal.emit(path)  # Emit signal from any thread

if __name__ == "__main__":
    app = VideoApplication(sys.argv)
    app.play_video("video/2.mp4")  # Replace with your video file path
    sys.exit(app.exec_())