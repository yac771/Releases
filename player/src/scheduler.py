import logging, requests, sys

class Scheduler:
    def __init__(self, config_path):
        self.config_path = config_path
        self.playlist = []
        self.current_index = -1
        self.logger = logging.getLogger(__name__)
        
        # Le Player va chercher les parametres locaux pour interroger le CMS
        # Si le CMS est lance sur une autre machine du meme WiFi, le Player s'y connectera !
        try:
            # S'il y a un argument (ex: --player 192.168.1.50), on l'utilise
            if len(sys.argv) > 2:
                ip = sys.argv[2]
                self.api_url = f"http://{ip}:5000/api/playlist"
            else:
                self.api_url = "http://127.0.0.1:5000/api/playlist"
        except:
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
            return {"type": "web", "url": "data:text/html;charset=utf-8,<html><body style='background:%230f172a;color:white;display:flex;align-items:center;justify-content:center;height:100vh;font-family:sans-serif;margin:0;'><div style='text-align:center;'><h1 style='font-size:3rem;margin-bottom:10px;'>OmniScreen</h1><p style='color:%2364748b;font-size:1.5rem;'>En attente de contenu...</p><p style='font-size:1rem;margin-top:40px;opacity:0.5;'>Connectez-vous au CMS pour ajouter des medias a la boucle.</p></div></body></html>", "duration": 10}
        self.current_index = (self.current_index + 1) % len(self.playlist)
        return self.playlist[self.current_index]
