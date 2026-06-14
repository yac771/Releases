import json, logging, os, requests

class Scheduler:
    def __init__(self, config_path):
        self.config_path = config_path
        self.playlist = []
        self.current_index = -1
        self.logger = logging.getLogger(__name__)
        # Desormais, le Player tape en direct sur l'API de ton CMS !
        self.api_url = "http://127.0.0.1:5000/api/playlist"
        self.fetch_from_api()

    def fetch_from_api(self):
        self.logger.info(f"Synchronisation Player <-> CMS via: {self.api_url}")
        try:
            response = requests.get(self.api_url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("campaigns") and len(data["campaigns"]) > 0:
                    self.playlist = data["campaigns"][0].get("items", [])
                    self.logger.info(f"Playlist recuperee : {len(self.playlist)} medias.")
            else:
                self.logger.error("Echec API.")
        except Exception as e:
            self.logger.error(f"Le CMS n'est pas joignable: {e}")

    def get_next_item(self):
        if self.current_index == len(self.playlist) - 1 or len(self.playlist) == 0:
            self.fetch_from_api()
        if not self.playlist:
            return None
        self.current_index = (self.current_index + 1) % len(self.playlist)
        return self.playlist[self.current_index]
