import sys, os, logging
from PyQt5 import QtWidgets, QtCore

def main():
    PUBLIC_DOCS = os.environ.get('PUBLIC', 'C:\\Users\\Public')
    OMNI_DIR = os.path.join(PUBLIC_DOCS, 'OmniScreenData')
    
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
    
    safe_argv = [sys.argv[0], "--no-sandbox", "--disable-gpu-compositing"]
    
    app = QtWidgets.QApplication.instance()
    if not app:
        QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
        app = QtWidgets.QApplication(safe_argv)
        
    if hasattr(QtCore.Qt, 'BlankCursor'):
        app.setOverrideCursor(QtCore.Qt.BlankCursor)
        
    from player.src.player import SignagePlayer
    player = SignagePlayer(config_path)
    player.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
