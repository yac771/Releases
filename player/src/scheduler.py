import json
import logging
import os
import requests

class Scheduler:
    def __init__(self, config_path):
        self.config_path = config_path
        self.playlist = []
        self.current_index = -1
        self.logger = logging.getLogger(__name__)
        self.api_url = None
        self.load_schedule()

    def load_schedule(self):
        # On essaie d'abord de voir si on a configuré une URL API dans le fichier
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    self.api_url = data.get("api_url")
                    
                    if not self.api_url:
                        # Si pas d'API, on utilise la playlist locale
                        if data.get("campaigns") and len(data["campaigns"]) > 0:
                            self.playlist = data["campaigns"][0].get("items", [])
                            self.logger.info(f"Loaded {len(self.playlist)} items from local file.")
                        else:
                            self.logger.warning("No campaigns found in schedule.")
                except json.JSONDecodeError as e:
                    self.logger.error(f"Invalid JSON in schedule: {e}")
        else:
            self.logger.error(f"Config file not found: {self.config_path}")
            
        # Si une API est configurée, on télécharge la playlist
        self.fetch_from_api()

    def fetch_from_api(self):
        if not self.api_url:
            return
            
        self.logger.info(f"Fetching playlist from CMS API: {self.api_url}")
        try:
            response = requests.get(self.api_url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("campaigns") and len(data["campaigns"]) > 0:
                    self.playlist = data["campaigns"][0].get("items", [])
                    self.logger.info(f"Loaded {len(self.playlist)} items from CMS API.")
            else:
                self.logger.error(f"Failed to fetch from API. Status: {response.status_code}")
        except Exception as e:
            self.logger.error(f"Error connecting to CMS API: {e}")

    def get_next_item(self):
        # On met à jour depuis l'API à chaque boucle (ou on garde la dernière version si l'internet coupe)
        if self.current_index == len(self.playlist) - 1:
            self.fetch_from_api()
            
        if not self.playlist:
            return None
            
        self.current_index = (self.current_index + 1) % len(self.playlist)
        return self.playlist[self.current_index]
