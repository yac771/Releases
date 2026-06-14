import sys, os, logging
from PyQt5.QtWidgets import QApplication
from player.src.player import SignagePlayer
from PyQt5.QtCore import Qt

def main():
    APPDATA = os.environ.get('APPDATA', os.path.expanduser('~'))
    OMNI_DIR = os.path.join(APPDATA, 'OmniScreenData')
    os.makedirs(OMNI_DIR, exist_ok=True)
    os.makedirs(os.path.join(OMNI_DIR, 'logs'), exist_ok=True)
    os.makedirs(os.path.join(OMNI_DIR, 'config'), exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(OMNI_DIR, 'logs', "player.log")),
            logging.StreamHandler()
        ]
    )
    
    # La config est désormais gérée dans APPDATA (modifiable en lecture/ecriture)
    config_path = os.path.join(OMNI_DIR, 'config', 'schedule.json')
    
    app = QApplication(sys.argv)
    if hasattr(Qt, 'BlankCursor'):
        app.setOverrideCursor(Qt.BlankCursor)
        
    player = SignagePlayer(config_path)
    player.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
