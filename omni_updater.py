import sys, os, time, requests, subprocess, tempfile
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QProgressBar
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont

class DownloadThread(QThread):
    progress_signal = pyqtSignal(int)
    done_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)

    def __init__(self, url, version):
        super().__init__()
        self.url = url
        self.version = version

    def run(self):
        exe_path = os.path.join(tempfile.gettempdir(), f"OmniScreen_Update_{self.version}.exe")
        try:
            response = requests.get(self.url, stream=True, timeout=10)
            response.raise_for_status()
            total_length = int(response.headers.get('content-length', 0))
            
            with open(exe_path, 'wb') as f:
                if total_length == 0:
                    f.write(response.content)
                    self.progress_signal.emit(100)
                else:
                    downloaded = 0
                    for data in response.iter_content(chunk_size=4096):
                        downloaded += len(data)
                        f.write(data)
                        done = int(100 * downloaded / total_length)
                        self.progress_signal.emit(done)
            
            time.sleep(1)
            self.done_signal.emit(exe_path)
            
        except Exception as e:
            self.error_signal.emit(str(e))

class UpdaterWindow(QWidget):
    def __init__(self, download_url, version):
        super().__init__()
        self.download_url = download_url
        self.version = version
        
        self.setWindowTitle("OmniScreen - Mise à jour")
        self.setFixedSize(400, 150)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setStyleSheet("background-color: #0f172a; border: 2px solid #3b82f6; border-radius: 10px;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        self.title_label = QLabel(f"Installation de la mise à jour (v{self.version})...")
        self.title_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.title_label.setStyleSheet("color: white; border: none;")
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #1e293b;
                border-radius: 5px;
                text-align: center;
                color: white;
                background-color: #1e293b;
            }
            QProgressBar::chunk {
                background-color: #3b82f6;
                width: 20px;
            }
        """)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel("Téléchargement des fichiers...")
        self.status_label.setFont(QFont("Segoe UI", 9))
        self.status_label.setStyleSheet("color: #94a3b8; border: none;")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        self.start_download()

    def start_download(self):
        self.thread = DownloadThread(self.download_url, self.version)
        self.thread.progress_signal.connect(self.update_progress)
        self.thread.done_signal.connect(self.installation_phase)
        self.thread.error_signal.connect(self.show_error)
        self.thread.start()

    def update_progress(self, val):
        self.progress_bar.setValue(val)

    def installation_phase(self, exe_path):
        self.title_label.setText("Application de la mise à jour...")
        self.status_label.setText("Veuillez autoriser l'installation Windows.")
        self.status_label.setStyleSheet("color: #10b981; border: none;")
        
        # CORRECTION EXPERT: L'updater GUI se ferme AVANT de lancer l'installation Windows.
        # Si on lance l'installeur pendant que PyQt tourne, ca creait un conflit de DLL.
        DETACHED_PROCESS = 0x00000008
        subprocess.Popen([exe_path, '/SILENT', '/SUPPRESSMSGBOXES'], creationflags=DETACHED_PROCESS)
        
        # On quitte l'application actuelle proprement 
        QApplication.quit()
        sys.exit(0)

    def show_error(self, err):
        self.title_label.setText("Erreur de téléchargement")
        self.status_label.setText("Veuillez vérifier votre connexion internet.")
        self.status_label.setStyleSheet("color: #ef4444; border: none;")

if __name__ == '__main__':
    # Ceci est execute si on l'appelle depuis la ligne de commande (ce qui ne devrait plus arriver, mais c'est securise)
    pass
