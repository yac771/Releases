import os, sys, requests, re, tempfile
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
    clean = v_str.lower().replace('v', '').split('-')[0]
    return [int(x) for x in clean.split('.') if x.isdigit()]

def check_for_updates():
    local_version = get_local_version()
    logging.info(f"Version locale : {local_version}")
    
    try:
        # RETOUR AU WEB SCRAPER (METHODE ULTIME ET INVINCIBLE)
        # Puisque l'API GitHub est capricieuse avec les droits et les redirections,
        # on lit directement le code HTML de TA page publique.
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        resp = requests.get(GITHUB_RELEASES_PAGE, headers=headers, timeout=8, verify=False)
        
        if resp.status_code == 200:
            html = resp.text
            
            # On cherche litteralement le texte bleu .exe sur la page web !
            match = re.search(r'href="(/yac771/Releases/releases/download/[^"]+\.exe)"', html)
            
            if match:
                partial_url = match.group(1)
                download_url = f"https://github.com{partial_url}"
                
                v_match = re.search(r'v([\d\.]+)(?:-[a-zA-Z0-9]+)?\.exe', download_url)
                if v_match:
                    remote_version = v_match.group(1)
                    
                    local_parsed = parse_version(local_version)
                    remote_parsed = parse_version(remote_version)
                    
                    if remote_parsed > local_parsed:
                        logging.info(f"MAJ SCRAPEE: {remote_version} | URL: {download_url}")
                        # On appelle omni_updater.py
                        return (download_url, remote_version)
                    else:
                        logging.info("Le logiciel est a jour.")
                        return False
            else:
                logging.info("Aucun .exe trouve sur la page GitHub.")
                return False
                
    except Exception as e:
        logging.warning(f"Echec verification Web Scraping: {e}")
        return f"ERR:{str(e)[:30]}"
        
    return False
