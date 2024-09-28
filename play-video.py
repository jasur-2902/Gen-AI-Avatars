import sys
import cv2
from PyQt5 import QtWidgets, QtCore, QtGui

class VideoPlayer(QtWidgets.QWidget):
    def __init__(self, video_path):
        super().__init__()
        self.video_path = video_path
        self.init_ui()

        # Load the video
        self.cap = cv2.VideoCapture(video_path)
        if not self.cap.isOpened():
            raise ValueError(f"Unable to open video file: {video_path}")

        # Set up a timer to update the video frame
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.next_frame)
        self.timer.start(int(1000 / self.cap.get(cv2.CAP_PROP_FPS)))

    def init_ui(self):
        self.setWindowTitle('Video Player')
        self.setGeometry(0, 0, 208, 160)
        self.video_label = QtWidgets.QLabel(self)
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.video_label)
        self.setLayout(self.layout)

    def next_frame(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (208, 170))  # Resize the frame to fit the window
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            qt_image = QtGui.QImage(frame.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
            self.video_label.setPixmap(QtGui.QPixmap.fromImage(qt_image))
        else:
            # If the video ended, loop it
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    def closeEvent(self, event):
        self.cap.release()
        event.accept()

class VideoApplication(QtWidgets.QApplication):
    def __init__(self, argv, video_path):
        super().__init__(argv)
        self.player = VideoPlayer(video_path)
        self.player.show()

if __name__ == "__main__":
    video_path = "video/beff.mp4"  # Replace with your video file path
    app = VideoApplication(sys.argv, video_path)
    sys.exit(app.exec_())
