import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from auth.auth import DiscordAuth
import logging
from time import sleep
from webhook.webhook import DiscordWebhook

class DiscordBot:
    BASE_URL = "https://discord.com/api/v9"

    def __init__(self, auth: DiscordAuth, webhook: DiscordWebhook):
        self.auth = auth
        self.webhook = webhook

    def _make_request(self, url):
        headers = self.auth.get_headers()
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            if http_err.response.status_code == 429:
                retry_after = int(http_err.response.headers.get('Retry-After', 1))
                logging.warning(f"Limite de taux atteinte, réessayer après {retry_after} secondes.")
                sleep(retry_after)
                return self._make_request(url)
            else:
                logging.error(f"HTTP error: {http_err}")
        except Exception as e:
            logging.error(f"Error making request: {e}")
        return None

    def get_guilds(self):
        url = f"{self.BASE_URL}/users/@me/guilds"
        return self._make_request(url)

    def process_guild(self, guild):
        logging.info(f"Processing guild: {guild['id']} - {guild['name']}")
        channels_url = f"{self.BASE_URL}/guilds/{guild['id']}/channels"
        channels = self._make_request(channels_url)
        if channels:
            for channel in channels:
                messages_url = f"{self.BASE_URL}/channels/{channel['id']}/messages"
                messages = self._make_request(messages_url)
                if messages:
                    for message in messages:
                        self.webhook.send_message(f"Message from {guild['name']}/{channel['name']}: {message['content']}")

    def run(self):
        guilds = self.get_guilds()
        if guilds:
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(self.process_guild, guild) for guild in guilds]

                for future in as_completed(futures):
                    try:
                        future.result()
                    except Exception as e:
                        logging.error(f"Error in processing guild: {e}")
