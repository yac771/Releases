import sys, os, logging
# CORRECTION IMPORTANTE: On n'importe PAS QApplication directement ici, car s'il y a un 
# double import avec launcher.py, ca fait crasher le systeme C++ sous-jacent.
from PyQt5 import QtWidgets, QtCore

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
    
    # Nettoyage absolu des arguments
    # Si Windows envoie des chemins bizarres a l'exe, on les nettoie.
    safe_argv = [sys.argv[0], "--no-sandbox", "--disable-gpu-compositing"]
    
    # On s'assure qu'une seule application existe
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication(safe_argv)
        
    if hasattr(QtCore.Qt, 'BlankCursor'):
        app.setOverrideCursor(QtCore.Qt.BlankCursor)
        
    # Import retarde de l'UI
    from player.src.player import SignagePlayer
    player = SignagePlayer(config_path)
    player.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
