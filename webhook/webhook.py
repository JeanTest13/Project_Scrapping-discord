import requests
import logging
from time import sleep

class DiscordWebhook:
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    def send_message(self, message: str):
        data = {"content": message}
        response = requests.post(self.webhook_url, json=data)

        if response.status_code == 204:
            logging.info("Message envoyé avec succès.")
        elif response.status_code == 429:
            retry_after = int(response.headers.get('Retry-After', 1))
            logging.warning(f"Limite de taux atteinte, réessayer après {retry_after} secondes.")
            sleep(retry_after)
            self.send_message(message)
        elif response.status_code != 200:
            logging.error(f"Erreur lors de l'envoi du message: {response.status_code}")


