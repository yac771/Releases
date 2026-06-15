import sys, logging
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QStackedWidget, QGraphicsOpacityEffect
from PyQt5.QtCore import QTimer, Qt, QUrl, QPropertyAnimation, QCoreApplication
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
        
        # Mode plein ecran total sans bordures
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.showFullScreen()
        self.setStyleSheet("background-color: black;")
        
        self.scheduler = Scheduler(config_path)
        self.downloader = Downloader()
        
        self.central_widget = QStackedWidget(self)
        self.setCentralWidget(self.central_widget)
        
        # Widget IMAGE
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("background-color: black;")
        self.central_widget.addWidget(self.image_label)
        
        # Widget WEB
        self.web_view = QWebEngineView()
        self.central_widget.addWidget(self.web_view)
        
        # Widget VIDEO
        self.video_widget = QVideoWidget()
        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.media_player.setVideoOutput(self.video_widget)
        self.central_widget.addWidget(self.video_widget)
        
        # Widget MESSAGE D'ATTENTE (Quand le CMS est vide)
        self.waiting_label = QLabel()
        self.waiting_label.setAlignment(Qt.AlignCenter)
        self.waiting_label.setStyleSheet("background-color: #0f172a; color: white;")
        self.waiting_label.setText("<div style='text-align:center;'><h1 style='font-size:4rem;margin-bottom:10px;'>OmniScreen</h1><p style='color:#64748b;font-size:2rem;'>En attente de contenu...</p><p style='font-size:1.5rem;margin-top:40px;opacity:0.5;'>Connectez-vous au CMS pour ajouter des medias a la boucle.</p></div>")
        self.central_widget.addWidget(self.waiting_label)
        
        # Bandeau d'actualites (Desactive temporairement si crash RSS)
        self.ticker_label = QLabel("", self)
        self.ticker_label.hide()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.play_next)
        self.play_next()

    def play_next(self):
        item = self.scheduler.get_next_item()
        
        # Si aucun element, ou si le CMS renvoie l'element vide par defaut
        if not item or item.get("type") == "web" and "data:text/html" in item.get("url", ""):
            self.media_player.stop()
            self.central_widget.setCurrentWidget(self.waiting_label)
            self.timer.start(5000) # On re-verifie dans 5 secondes
            return
            
        media_type = item.get("type")
        url = item.get("url")
        duration = item.get("duration", 10) * 1000
        
        # Petite animation de Transition (Fondu)
        self.effect = QGraphicsOpacityEffect()
        self.central_widget.setGraphicsEffect(self.effect)
        self.anim = QPropertyAnimation(self.effect, b"opacity")
        self.anim.setDuration(500)
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
            else:
                self.central_widget.setCurrentWidget(self.waiting_label)
                
        elif media_type in ["web", "widget_html", "widget_clock"]:
            self.media_player.stop()
            
            # Si c'est du code HTML brut envoye par le CMS, on l'affiche directement !
            if media_type != "web" and not url.startswith("http"):
                self.web_view.setHtml(url)
            else:
                self.web_view.setUrl(QUrl(url))
                
            self.central_widget.setCurrentWidget(self.web_view)

        elif media_type == "video":
            local_path = self.downloader.download(url)
            if local_path:
                # IMPORTANT: QUrl.fromLocalFile() gere les chemins Windows correctement
                self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(local_path)))
                self.central_widget.setCurrentWidget(self.video_widget)
                self.media_player.play()
            else:
                self.central_widget.setCurrentWidget(self.waiting_label)
                
        self.timer.start(duration)

    def keyPressEvent(self, event):
        # Touche ESC pour quitter le plein ecran
        if event.key() == Qt.Key_Escape:
            self.close()
            QCoreApplication.quit()
