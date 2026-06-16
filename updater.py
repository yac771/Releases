import os, sys, requests, tempfile
import urllib3

urllib3.disable_warnings()

# L'API LISTE TOUTES LES RELEASES (Fiabilite a 100%)
GITHUB_API_URL = "https://api.github.com/repos/yac771/Releases/releases"

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

def parse_v(v_str):
    clean = v_str.lower().replace('v', '').split('-')[0]
    return [int(x) for x in clean.split('.') if x.isdigit()]

def check_for_updates():
    local_version = get_local_version()
    
    try:
        # On lit la liste des releases sur ton Github
        resp = requests.get(GITHUB_API_URL, timeout=8, verify=False)
        if resp.status_code == 200:
            releases = resp.json()
            if not releases:
                return False
                
            # On prend la toute derniere release publiee (la premiere de la liste)
            latest = releases[0]
            remote_version = latest.get('tag_name', '').replace('v', '')
            
            # On cherche le fichier EXE
            download_url = None
            for asset in latest.get('assets', []):
                if asset.get('name', '').lower().endswith('.exe'):
                    download_url = asset.get('browser_download_url')
                    break
            
            if download_url and remote_version:
                if parse_v(remote_version) > parse_v(local_version):
                    # MISE A JOUR TROUVEE ! On previent le launcher
                    return (download_url, remote_version)
    except Exception as e:
        return f"ERR:{str(e)[:30]}"
        
    return False
