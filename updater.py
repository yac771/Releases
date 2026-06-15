import os, sys, requests, subprocess, tempfile
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
                logging.info(f"Mise a jour GitHub trouvee ({remote_version}) ! Demarrage Updater Graphique...")
                
                # ==== LE VRAI SYSTEME PROFESSIONNEL ====
                # On ne telecharge PAS le fichier de 60Mo ici en figeant le logiciel.
                # On lance un deuxieme programme cache appele "omni_updater.py" qui va
                # afficher une belle fenetre PyQt5 avec une vraie barre de pourcentage
                # puis fermer le logiciel principal, puis lancer le Setup.
                
                if getattr(sys, 'frozen', False):
                    base_dir = sys._MEIPASS
                else:
                    base_dir = os.path.abspath(os.path.dirname(__file__))
                    
                updater_script = os.path.join(base_dir, 'omni_updater.py')
                
                # On lance le script de maj dans un processus totallement detache
                DETACHED_PROCESS = 0x00000008
                
                # On lui passe l'URL et la version en argument
                subprocess.Popen([sys.executable, updater_script, download_url, remote_version], creationflags=DETACHED_PROCESS)
                
                # On ferme immediatement le Lanceur pour eviter de bloquer l'installation
                sys.exit(0)
                return True
    except Exception as e:
        logging.warning(f"La verification des mises a jour a echoue : {e}")
        
    return False
