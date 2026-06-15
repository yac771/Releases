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
                # CORRECTION : S'assurer de bien telecharger le bon exe, pas un code source
                if asset.get('name', '').lower().endswith('.exe'):
                    download_url = asset.get('browser_download_url')
                    break
            
            # On parse proprement les versions pour eviter les bugs de type "1.10.0" > "1.9.0" 
            # (que la fonction float() simple ne comprend pas bien).
            def parse_version(v_str):
                # "1.4.0-beta" -> [1, 4, 0]
                clean = v_str.split('-')[0]
                return [int(x) for x in clean.split('.') if x.isdigit()]
                
            local_parsed = parse_version(local_version)
            remote_parsed = parse_version(remote_version)

            if download_url and remote_parsed > local_parsed:
                logging.info(f"Mise a jour GitHub trouvee ({remote_version}) ! On previent l'UI...")
                return (download_url, remote_version)
                
    except Exception as e:
        logging.warning(f"La verification des mises a jour a echoue : {e}")
        
    return False
