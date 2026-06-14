import sys, os, subprocess, multiprocessing
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

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
        self.setWindowTitle("OmniScreen - Launcher (BETA)")
        self.setFixedSize(500, 370)
        self.setStyleSheet("background-color: #f8fafc;")

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(40, 30, 40, 40)
        layout.setSpacing(15)

        # Ajout du badge Beta
        beta_badge = QLabel("VERSION BETA")
        beta_badge.setFont(QFont("Segoe UI", 9, QFont.Bold))
        beta_badge.setAlignment(Qt.AlignCenter)
        beta_badge.setStyleSheet("color: white; background-color: #ef4444; border-radius: 10px; padding: 4px; margin-left: 150px; margin-right: 150px;")
        layout.addWidget(beta_badge)

        title = QLabel("OmniScreen")
        title.setFont(QFont("Segoe UI", 28, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #0f172a;")
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

    def run_cms_process(self):
        self.hide()
        subprocess.Popen([sys.executable, '--cms'])
        self.close()

    def run_player_process(self):
        self.hide()
        subprocess.Popen([sys.executable, '--player'])
        self.close()

if __name__ == "__main__":
    multiprocessing.freeze_support()
    launch_mode()
    try:
        from updater import check_for_updates
        check_for_updates()
    except:
        pass
    app = QApplication(sys.argv)
    win = LauncherWindow()
    win.show()
    sys.exit(app.exec_())
