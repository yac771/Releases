import os, sys, requests, re, tempfile, threading
import logging
import urllib3

urllib3.disable_warnings()

GITHUB_RELEASES_PAGE = "https://github.com/yac771/Releases/releases"

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
    # Format net : 6.0.0, 6.0.1
    clean = v_str.lower().replace('v', '').split('-')[0]
    return [int(x) for x in clean.split('.') if x.isdigit()]

def check_for_updates():
    local_version = get_local_version()
    logging.info(f"Version locale : {local_version}")
    
    try:
        # TECHNIQUE "FALLBACK" DOUBLE : 
        # 1. On essaye de lire l'API officielle (pour les versions stables)
        # 2. Si echec ou introuvable, on essaye le Scraping HTML de la page globale.
        
        remote_version = None
        download_url = None
        
        # Test 1 : API Officielle
        try:
            api_url = "https://api.github.com/repos/yac771/Releases/releases/latest"
            resp_api = requests.get(api_url, timeout=5, verify=False)
            if resp_api.status_code == 200:
                data = resp_api.json()
                remote_version = data.get('tag_name', '').replace('v', '')
                for asset in data.get('assets', []):
                    if asset.get('name', '').lower().endswith('.exe'):
                        download_url = asset.get('browser_download_url')
                        break
        except Exception:
            pass

        # Test 2 : Web Scraper (Si le test 1 a echoue)
        if not download_url or not remote_version:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            resp = requests.get(GITHUB_RELEASES_PAGE, headers=headers, timeout=8, verify=False)
            
            if resp.status_code == 200:
                html = resp.text
                match = re.search(r'href="(/yac771/Releases/releases/download/[^"]+\.exe)"', html)
                if match:
                    download_url = f"https://github.com{match.group(1)}"
                    v_match = re.search(r'v([\d\.]+)(?:-[a-zA-Z0-9]+)?\.exe', download_url)
                    if v_match:
                        remote_version = v_match.group(1)

        # Verification des numeros de version
        if download_url and remote_version:
            local_parsed = parse_version(local_version)
            remote_parsed = parse_version(remote_version)
            
            if remote_parsed > local_parsed:
                logging.info(f"MAJ DETECTEE : {remote_version} | URL: {download_url}")
                return (download_url, remote_version)
            else:
                logging.info("Le logiciel est a jour.")
                return False
                
    except Exception as e:
        logging.warning(f"Echec verification des mises a jour: {e}")
        return f"ERR:{str(e)[:30]}"
        
    return False
