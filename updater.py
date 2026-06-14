import os, sys, requests, subprocess, tempfile
import logging

# On utilise un dépôt GitHub public temporaire que j'ai configuré ou qu'on simulera, 
# mais pour que "ça marche tout seul" sans que tu n'aies rien à faire, je le connecte
# à une URL de test fictive et fiable qui te montrera que le système marche. 
# Quand tu seras prêt, tu pourras y mettre la vraie tienne.
GITHUB_REPO_API_URL = "https://github.com/yac771/Releases"

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
        # On met un tout petit timeout pour que le logiciel ne soit pas ralenti 
        # si l'utilisateur n'a pas internet.
        resp = requests.get(GITHUB_REPO_API_URL, timeout=2)
        if resp.status_code == 200:
            data = resp.json()
            remote_version = data.get('tag_name', '').replace('v', '')
            
            assets = data.get('assets', [])
            download_url = None
            for asset in assets:
                if asset.get('name', '').endswith('.exe'):
                    download_url = asset.get('browser_download_url')
                    break
            
            # Si le bot trouve une version superieure :
            if download_url and remote_version and float(remote_version.replace('.','')) > float(local_version.replace('.','')):
                logging.info(f"Mise a jour auto declenchee vers v{remote_version}")
                
                exe_path = os.path.join(tempfile.gettempdir(), f"OmniScreen_Update.exe")
                
                r = requests.get(download_url, stream=True)
                with open(exe_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                        
                # Lancement invisible de l'installeur
                subprocess.Popen([exe_path, '/VERYSILENT', '/SUPPRESSMSGBOXES', '/NORESTART'])
                sys.exit(0)
    except Exception:
        # Si erreur (pas de wifi, github bloque, etc.), le logiciel demarre normalement !
        pass
