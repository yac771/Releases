import sys, os, logging
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

def main():
    LOCAL_APPDATA = os.environ.get('LOCALAPPDATA', os.path.expanduser('~'))
    OMNI_DIR = os.path.join(LOCAL_APPDATA, 'OmniScreenData')
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
    
    config_path = os.path.join(OMNI_DIR, 'config', 'schedule.json')
    
    # Import retarde pour eviter les fuites de memoire entre Launcher et Player
    from player.src.player import SignagePlayer
    
    # Il FAUT forcer ces arguments sous Windows pour que le navigateur web du player marche en plein ecran
    sys.argv.extend(["--disable-gpu-compositing", "--disable-software-rasterizer"])
    
    app = QApplication(sys.argv)
    if hasattr(Qt, 'BlankCursor'):
        app.setOverrideCursor(Qt.BlankCursor)
        
    player = SignagePlayer(config_path)
    player.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
