import sys, logging, feedparser
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QStackedWidget, QGraphicsOpacityEffect
from PyQt5.QtCore import QTimer, Qt, QUrl, QPropertyAnimation
from PyQt5.QtGui import QPixmap, QFont
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
        self.setStyleSheet("background-color: black;")
        
        self.scheduler = Scheduler(config_path)
        self.downloader = Downloader()
        
        self.central_widget = QStackedWidget(self)
        self.setCentralWidget(self.central_widget)
        
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.central_widget.addWidget(self.image_label)
        
        self.web_view = QWebEngineView()
        self.central_widget.addWidget(self.web_view)
        
        self.video_widget = QVideoWidget()
        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.media_player.setVideoOutput(self.video_widget)
        self.central_widget.addWidget(self.video_widget)
        
        # BAndeau RSS
        self.rss_text = "OmniScreen News - En attente d'actualites..."
        try:
            d = feedparser.parse('https://www.france24.com/fr/rss')
            self.rss_text = " *** ".join([entry.title for entry in d.entries[:10]])
        except Exception as e:
            logging.error(f"RSS error: {e}")
            
        self.ticker_label = QLabel(self.rss_text, self)
        self.ticker_label.setStyleSheet("background-color: rgba(15, 23, 42, 0.85); color: white; padding: 10px; border-top: 2px solid #3b82f6;")
        self.ticker_label.setFont(QFont("Arial", 20, QFont.Bold))
        self.ticker_label.setFixedHeight(60)
        self.ticker_label.adjustSize()
        
        self.ticker_x = self.width()
        self.ticker_timer = QTimer(self)
        self.ticker_timer.timeout.connect(self.scroll_ticker)
        self.ticker_timer.start(20)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.play_next)
        self.play_next()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.ticker_label.move(self.ticker_x, self.height() - 60)

    def scroll_ticker(self):
        self.ticker_x -= 3
        if self.ticker_x < -self.ticker_label.width():
            self.ticker_x = self.width()
        self.ticker_label.move(self.ticker_x, self.height() - 60)

    def play_next(self):
        item = self.scheduler.get_next_item()
        if not item:
            self.timer.start(5000)
            return
            
        media_type = item.get("type")
        url = item.get("url")
        duration = item.get("duration", 10) * 1000
        
        # Animation Transition Fade
        self.effect = QGraphicsOpacityEffect()
        self.central_widget.setGraphicsEffect(self.effect)
        self.anim = QPropertyAnimation(self.effect, b"opacity")
        self.anim.setDuration(800)
        self.anim.setStartValue(0)
        self.anim.setEndValue(1)
        self.anim.start()

        if media_type == "image":
            self.media_player.stop()
            local_path = self.downloader.download(url)
            if local_path:
                pixmap = QPixmap(local_path)
                self.image_label.setPixmap(pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
                self.central_widget.setCurrentWidget(self.image_label)
                
        elif media_type in ["web", "widget_html", "widget_clock"]:
            self.media_player.stop()
            self.web_view.setUrl(QUrl(url))
            self.central_widget.setCurrentWidget(self.web_view)

        elif media_type == "video":
            local_path = self.downloader.download(url)
            if local_path:
                self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(local_path)))
                self.central_widget.setCurrentWidget(self.video_widget)
                self.media_player.play()
                
        self.timer.start(duration)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
