import sys, os, subprocess, multiprocessing, threading
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel, QMessageBox
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QIcon, QPixmap, QPainter, QColor

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
        self.setFixedSize(500, 480) # Agrandissement pour faire de la place au beau logo et au bouton de MAJ
        self.setStyleSheet("background-color: #f8fafc;")

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(40, 20, 40, 30)
        layout.setSpacing(15)

        # ====== LE NOUVEAU LOGO MAGNIFIQUE (Généré en Code pour ne pas dependre de fichiers externes) ======
        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignCenter)
        
        # On dessine un faux "Logo" tres moderne (Style Oeil / Lentille futuriste)
        pixmap = QPixmap(100, 100)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Cercle exterieur bleu fonce
        painter.setBrush(QColor("#0f172a"))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(5, 5, 90, 90)
        
        # Cercle interieur bleu electrique
        painter.setBrush(QColor("#3b82f6"))
        painter.drawEllipse(20, 20, 60, 60)
        
        # Centre ecran "Play" blanc
        painter.setBrush(QColor("#ffffff"))
        painter.drawPolygon(*[Qt.QPoint(40, 35), Qt.QPoint(65, 50), Qt.QPoint(40, 65)])
        painter.end()
        
        logo_label.setPixmap(pixmap)
        layout.addWidget(logo_label)
        # ===================================================================================================

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

        # ====== LE NOUVEAU BOUTON "RECHERCHER DES MISES A JOUR" ======
        self.btn_update = QPushButton("🔄 Rechercher des Mises à jour")
        self.btn_update.setCursor(Qt.PointingHandCursor)
        self.btn_update.setStyleSheet("QPushButton { background-color: transparent; color: #64748b; border: 1px solid #cbd5e1; border-radius: 8px; padding: 10px; font-weight: bold; font-size:12px; margin-top: 10px;} QPushButton:hover { background-color: #e2e8f0; color: #0f172a; }")
        self.btn_update.clicked.connect(self.manual_update_check)
        layout.addWidget(self.btn_update)
        
        # Texte informatif caché pour le resultat de la maj
        self.lbl_update_status = QLabel("")
        self.lbl_update_status.setAlignment(Qt.AlignCenter)
        self.lbl_update_status.setStyleSheet("color: #3b82f6; font-size: 11px; font-weight: bold;")
        self.lbl_update_status.hide()
        layout.addWidget(self.lbl_update_status)

    def run_cms_process(self):
        self.hide()
        subprocess.Popen([sys.executable, '--cms'])
        self.close()

    def run_player_process(self):
        self.hide()
        subprocess.Popen([sys.executable, '--player'])
        self.close()

    def manual_update_check(self):
        self.btn_update.setEnabled(False)
        self.btn_update.setText("⏳ Recherche en cours...")
        self.lbl_update_status.hide()
        
        # On lance la verification dans un thread separe pour ne pas figer l'interface
        def check():
            from updater import check_for_updates
            # check_for_updates renvoie desormais True si une maj est lancee, False sinon
            result = check_for_updates()
            
            # On demande au fil principal de remettre le bouton normal
            QTimer.singleShot(0, lambda: self.update_check_finished(result))
            
        threading.Thread(target=check).start()
        
    def update_check_finished(self, result):
        if result:
            self.lbl_update_status.setText("✅ Mise à jour trouvée ! Installation...")
            self.lbl_update_status.setStyleSheet("color: #10b981; font-size: 11px; font-weight: bold;")
        else:
            self.btn_update.setText("🔄 Rechercher des Mises à jour")
            self.btn_update.setEnabled(True)
            self.lbl_update_status.setText("Vous avez la dernière version.")
            self.lbl_update_status.setStyleSheet("color: #64748b; font-size: 11px; font-weight: bold;")
        self.lbl_update_status.show()

if __name__ == "__main__":
    multiprocessing.freeze_support()
    launch_mode()
    
    # On desactive le check silencieux automatique au demarrage 
    # car maintenant on a un bouton explicite pour le client !
    
    app = QApplication(sys.argv)
    win = LauncherWindow()
    win.show()
    sys.exit(app.exec_())
