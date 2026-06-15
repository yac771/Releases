import os, sys, requests, tempfile
import logging

GITHUB_REPO_API_URL = "https://api.github.com/repos/yac771/Releases/releases/latest"

def get_local_version():
    if getattr(sys, 'frozen', False):
        base_dir = sys._MEIPASS
    else:
        base_dir = os.path.abspath(os.path.dirname(__file__))
        
    v_file = os.path.join(base_dir, 'version.txt')
    if os.path.exists(v_file):
        with open(v_file, 'r') as f:
            return f.read().strip()
    return '1.0.0'

def check_for_updates():
    local_version = get_local_version()
    logging.info(f"Version locale : {local_version}")
    
    try:
        resp = requests.get(GITHUB_REPO_API_URL, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            remote_version = data.get('tag_name', '').replace('v', '')
            
            assets = data.get('assets', [])
            download_url = None
            for asset in assets:
                if asset.get('name', '').endswith('.exe'):
                    download_url = asset.get('browser_download_url')
                    break
            
            if download_url and remote_version and float(remote_version.replace('.','')) > float(local_version.replace('.','')):
                # CORRECTION: On retourne DIRECTEMENT l'instance de la fenetre Updater
                # au lieu d'essayer de lancer un subprocess qui cassait tout.
                from omni_updater import UpdaterWindow
                return UpdaterWindow(download_url, remote_version)
                
    except Exception as e:
        logging.warning(f"La verification des mises a jour a echoue : {e}")
        
    return False
