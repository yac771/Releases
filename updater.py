import os, sys, requests
import logging
import urllib3

# Desactivation des alertes de securite SSL qui bloquent l'exe
urllib3.disable_warnings()

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
    clean = v_str.split('-')[0]
    return [int(x) for x in clean.split('.') if x.isdigit()]

def check_for_updates():
    local_version = get_local_version()
    logging.info(f"Version locale : {local_version}")
    
    try:
        # TECHNIQUE ANTI-LIMITE : On passe par la redirection web plutot que l'API !
        url = "https://github.com/yac771/Releases/releases/latest"
        resp = requests.get(url, allow_redirects=False, timeout=10, verify=False)
        
        remote_version = None
        if resp.status_code in [301, 302]:
            location = resp.headers.get('Location', '')
            if 'tag/v' in location:
                remote_version = location.split('tag/v')[-1]
                
        if remote_version:
            local_parsed = parse_version(local_version)
            remote_parsed = parse_version(remote_version)
            
            if remote_parsed > local_parsed:
                logging.info(f"MAJ trouvee: {remote_version}")
                download_url = f"https://github.com/yac771/Releases/releases/download/v{remote_version}/OmniScreen_Setup_v{remote_version}.exe"
                return (download_url, remote_version)
                
    except Exception as e:
        logging.warning(f"Echec verification: {e}")
        return f"ERR:{str(e)}"
        
    return False
