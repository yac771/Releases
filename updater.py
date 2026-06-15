import os, sys, requests, tempfile
import logging
import urllib3

urllib3.disable_warnings()

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

def parse_version(v_str):
    clean = v_str.lower().replace('v', '').split('-')[0]
    return [int(x) for x in clean.split('.') if x.isdigit()]

def check_for_updates():
    local_version = get_local_version()
    logging.info(f"Version locale : {local_version}")
    
    try:
        # TEST: On essaye aussi les "tags" si "latest" bloque à cause des "Pre-Releases" de GitHub
        resp = requests.get(GITHUB_REPO_API_URL, timeout=5, verify=False)
        
        # FIX DE L'ERREUR D'UPDATER : Parfois GitHub refuse le "/latest".
        # On va chercher TOUTE la liste des releases et on prend la premiere !
        if resp.status_code != 200:
            resp = requests.get("https://api.github.com/repos/yac771/Releases/releases", timeout=5, verify=False)
            if resp.status_code == 200 and len(resp.json()) > 0:
                data = resp.json()[0] # On prend la derniere release publiee meme si elle est en "Beta"
            else:
                return False
        else:
            data = resp.json()
            
        remote_version = data.get('tag_name', '').replace('v', '')
        
        assets = data.get('assets', [])
        download_url = None
        for asset in assets:
            if asset.get('name', '').lower().endswith('.exe'):
                download_url = asset.get('browser_download_url')
                break
        
        if download_url and remote_version:
            local_parsed = parse_version(local_version)
            remote_parsed = parse_version(remote_version)
            
            if remote_parsed > local_parsed:
                logging.info(f"Mise a jour GitHub trouvee ({remote_version}) !")
                return (download_url, remote_version)
            else:
                logging.info("Le logiciel est a jour.")
                return False
                
    except Exception as e:
        logging.warning(f"Echec verification: {e}")
        return f"ERR:{str(e)[:30]}"
        
    return False
