import requests
from requests.exceptions import HTTPError, ConnectionError, Timeout, RequestException
import logging
from models.models import Channel, Message
from auth.auth import DiscordAuth
from file_manager.file_manager import FileManager
from webhook.webhook import DiscordWebhook
from typing import Optional, List
from time import sleep


logger = logging.getLogger(__name__)

class DiscordAPI:
    BASE_URL = "https://discord.com/api/v9"

    def __init__(self, auth: DiscordAuth):
        self.auth = auth

    def _make_request(self, url, headers):
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response
        except HTTPError as http_err:
            status_code = http_err.response.status_code
            if status_code == 429:
                retry_after = int(http_err.response.headers.get('Retry-After', 1))
                logging.warning(f"Limite de taux atteinte, réessayer après {retry_after} secondes.")
                return self._make_request(url)
            elif status_code == 401:
                logger.error("Erreur 401: Non autorisé - Vérifiez votre token d'authentification.")
            elif status_code == 403:
                logger.error("Erreur 403: Interdit - Permissions insuffisantes.")
            elif status_code == 404:
                logger.error("Erreur 404: Non trouvé - L'URL ou la ressource est introuvable.")
            elif status_code == 429:
                logger.error("Erreur 429: Trop de requêtes - Limite de taux atteinte.")
            else:
                logger.error(f"Erreur HTTP : {http_err}")
        except ConnectionError:
            logger.error("Erreur de connexion - Impossible de se connecter à l'API Discord.")
        except Timeout:
            logger.error("Erreur de timeout - La requête a pris trop de temps pour répondre.")
        except RequestException as req_err:
            logger.error(f"Erreur de requête : {req_err}")
        return None

    def is_discord_up(self):
        try:
            response = requests.get(f"{self.BASE_URL}/gateway")
            return response.status_code == 200
        except (ConnectionError, Timeout):
            return False

    def retrieve_channels(self, guild_id: str) -> Optional[List[Channel]]:
        url = f"{self.BASE_URL}/guilds/{guild_id}/channels"
        headers = self.auth.get_headers()
        response = self._make_request(url, headers)
        if response and response.status_code == 200:
            return [Channel(**channel) for channel in response.json()]
        return None

    def retrieve_messages(self, channel_id: str, webhook: DiscordWebhook) -> None:
        url = f"{self.BASE_URL}/channels/{channel_id}/messages"
        headers = self.auth.get_headers()
        response = self._make_request(url, headers)
        if response and response.status_code == 200:
            for message_data in response.json():
                message = Message(**message_data)
                if message.content:
                    author_name = message.author.username if message.author else "Inconnu"
                    webhook.send_message(f"{author_name}: {message.content}")
                for attachment in message.attachments:
                    FileManager.download_file(attachment.url, attachment.filename)
