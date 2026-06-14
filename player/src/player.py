import sys
import logging
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QStackedWidget
from PyQt5.QtCore import QTimer, Qt, QUrl
from PyQt5.QtGui import QPixmap
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget

from player.src.scheduler import Scheduler
from player.src.downloader import Downloader

class SignagePlayer(QMainWindow):
    def __init__(self, config_path):
        super().__init__()
        self.setWindowTitle("OmniScreen Player")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.showFullScreen()
        
        # Core components
        self.scheduler = Scheduler(config_path)
        self.downloader = Downloader()
        
        # UI Setup
        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)
        
        # Image viewer
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("background-color: black;")
        self.central_widget.addWidget(self.image_label)
        
        # Web viewer
        self.web_view = QWebEngineView()
        self.central_widget.addWidget(self.web_view)
        
        # Video viewer
        self.video_widget = QVideoWidget()
        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.media_player.setVideoOutput(self.video_widget)
        self.central_widget.addWidget(self.video_widget)
        
        # Timer for transitioning
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.play_next)
        
        # Start playback
        self.play_next()

    def play_next(self):
        item = self.scheduler.get_next_item()
        if not item:
            logging.error("No items to play.")
            return
            
        media_type = item.get("type")
        url = item.get("url")
        duration = item.get("duration", 10) * 1000 # Convert to ms
        
        logging.info(f"Playing {media_type}: {url} for {duration}ms")
        
        if media_type == "image":
            self.media_player.stop()
            local_path = self.downloader.download(url)
            if local_path:
                pixmap = QPixmap(local_path)
                # Scale pixmap to fit screen while keeping aspect ratio
                scaled_pixmap = pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.image_label.setPixmap(scaled_pixmap)
                self.central_widget.setCurrentWidget(self.image_label)
            else:
                logging.error("Could not load image.")
                
        elif media_type == "web":
            self.media_player.stop()
            self.web_view.setUrl(QUrl(url))
            self.central_widget.setCurrentWidget(self.web_view)

        elif media_type == "video":
            local_path = self.downloader.download(url)
            if local_path:
                self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(local_path)))
                self.central_widget.setCurrentWidget(self.video_widget)
                self.media_player.play()
            else:
                logging.error("Could not load video.")
            
        else:
            logging.warning(f"Unsupported media type: {media_type}")
            
        # Schedule next item
        self.timer.start(duration)

    def keyPressEvent(self, event):
        # Allow exiting with ESC key
        if event.key() == Qt.Key_Escape:
            self.close()
