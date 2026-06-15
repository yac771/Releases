import sys, os, subprocess, multiprocessing, threading
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel
from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtGui import QFont, QPixmap, QPainter, QColor

def launch_mode():
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        if mode == '--cms':
            from cms.cms_app import run_cms
            run_cms()
            sys.exit(0)
        elif mode == '--player':
            from player.src.main import main as run_player
            run_player()
            sys.exit(0)

class LauncherWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OmniScreen - Launcher")
        self.setFixedSize(500, 480)
        self.setStyleSheet("background-color: #f8fafc;")

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(40, 20, 40, 30)
        layout.setSpacing(15)

        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignCenter)
        
        pixmap = QPixmap(100, 100)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        painter.setBrush(QColor("#0f172a"))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(5, 5, 90, 90)
        
        painter.setBrush(QColor("#3b82f6"))
        painter.drawEllipse(20, 20, 60, 60)
        
        painter.setBrush(QColor("#ffffff"))
        painter.drawPolygon(QPoint(40, 35), QPoint(65, 50), QPoint(40, 65))
        painter.end()
        
        logo_label.setPixmap(pixmap)
        layout.addWidget(logo_label)

        title = QLabel("OmniScreen")
        title.setFont(QFont("Segoe UI", 26, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #0f172a; margin-top: -10px;")
        layout.addWidget(title)

        sub = QLabel("Que souhaitez-vous lancer sur cet ordinateur ?")
        sub.setFont(QFont("Segoe UI", 11))
        sub.setAlignment(Qt.AlignCenter)
        sub.setStyleSheet("color: #64748b; margin-bottom: 10px;")
        layout.addWidget(sub)

        self.btn_cms = QPushButton("Lancer le Serveur CMS (Tableau de bord)")
        self.btn_cms.setCursor(Qt.PointingHandCursor)
        self.btn_cms.setStyleSheet("QPushButton { background-color: #3b82f6; color: white; border-radius: 8px; padding: 15px; font-weight: bold; font-size:14px; } QPushButton:hover { background-color: #2563eb; }")
        self.btn_cms.clicked.connect(self.run_cms_process)
        layout.addWidget(self.btn_cms)

        self.btn_player = QPushButton("Lancer l'Écran d'Affichage (Player)")
        self.btn_player.setCursor(Qt.PointingHandCursor)
        self.btn_player.setStyleSheet("QPushButton { background-color: #10b981; color: white; border-radius: 8px; padding: 15px; font-weight: bold; font-size:14px; } QPushButton:hover { background-color: #059669; }")
        self.btn_player.clicked.connect(self.run_player_process)
        layout.addWidget(self.btn_player)

        self.btn_update = QPushButton("🔄 Rechercher des Mises à jour")
        self.btn_update.setCursor(Qt.PointingHandCursor)
        self.btn_update.setStyleSheet("QPushButton { background-color: transparent; color: #64748b; border: 1px solid #cbd5e1; border-radius: 8px; padding: 10px; font-weight: bold; font-size:12px; margin-top: 10px;} QPushButton:hover { background-color: #e2e8f0; color: #0f172a; }")
        self.btn_update.clicked.connect(self.manual_update_check)
        layout.addWidget(self.btn_update)
        
        self.lbl_update_status = QLabel("")
        self.lbl_update_status.setAlignment(Qt.AlignCenter)
        self.lbl_update_status.setStyleSheet("color: #3b82f6; font-size: 11px; font-weight: bold;")
        self.lbl_update_status.hide()
        layout.addWidget(self.lbl_update_status)

    def run_cms_process(self):
        # Ne cache plus la fenetre pour eviter la perte du thread pyqt
        subprocess.Popen([sys.executable, '--cms'])
        self.close()

    def run_player_process(self):
        # REPARATION: Le processus player etait bloque car Pyinstaller a du mal a lancer PyQtMultimedia depuis un subprocess
        # Solution: On execute le code directement ici plutot qu'en subprocess !
        self.hide()
        from player.src.main import main as run_player
        run_player()
        self.close()

    def manual_update_check(self):
        self.btn_update.setEnabled(False)
        self.btn_update.setText("⏳ Recherche en cours...")
        self.lbl_update_status.hide()
        
        def check():
            from updater import check_for_updates
            result = check_for_updates()
            QTimer.singleShot(0, lambda: self.update_check_finished(result))
            
        threading.Thread(target=check).start()
        
    def update_check_finished(self, result):
        if result:
            self.updater_window = result
            self.updater_window.show()
            self.hide()
        else:
            self.btn_update.setText("🔄 Rechercher des Mises à jour")
            self.btn_update.setEnabled(True)
            self.lbl_update_status.setText("Vous avez la dernière version.")
            self.lbl_update_status.setStyleSheet("color: #64748b; font-size: 11px; font-weight: bold;")
            self.lbl_update_status.show()

if __name__ == "__main__":
    multiprocessing.freeze_support()
    launch_mode()
    app = QApplication(sys.argv)
    win = LauncherWindow()
    win.show()
    sys.exit(app.exec_())
