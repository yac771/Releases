import os, hashlib, requests, logging

class Downloader:
    def __init__(self):
        APPDATA = os.environ.get('APPDATA', os.path.expanduser('~'))
        self.cache_dir = os.path.join(APPDATA, 'OmniScreenData', 'assets')
        os.makedirs(self.cache_dir, exist_ok=True)
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def get_local_path(self, url):
        url_hash = hashlib.md5(url.encode('utf-8')).hexdigest()
        ext = url.split('.')[-1]
        if len(ext) > 4 or '?' in ext:
            ext = 'jpg'
        return os.path.join(self.cache_dir, f"{url_hash}.{ext}")

    def download(self, url):
        local_path = self.get_local_path(url)
        if os.path.exists(local_path):
            self.logger.info(f"Asset already cached: {local_path}")
            return local_path
        
        self.logger.info(f"Downloading {url} to {local_path}")
        try:
            response = requests.get(url, stream=True, timeout=10)
            response.raise_for_status()
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return local_path
        except Exception as e:
            self.logger.error(f"Failed to download {url}: {e}")
            return None
