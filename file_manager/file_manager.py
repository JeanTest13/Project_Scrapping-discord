import os
import requests
import logging


logger = logging.getLogger(__name__)


class FileManager:
    RED = '\033[91m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'


    @staticmethod
    def download_file(url: str, filename: str) -> None:
        download_path = ''
        color = ''

        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            download_path = os.path.join('Images', filename)
            color = FileManager.RED
        else:
            download_path = os.path.join('Fichiers', filename)
            color = FileManager.BLUE

        response = requests.get(url)
        if response.status_code == 200:
            os.makedirs(os.path.dirname(download_path), exist_ok=True)
            with open(download_path, 'wb') as f:
                f.write(response.content)
            logger.info(f"Fichier téléchargé: {color}{filename}{FileManager.ENDC}")
        else:
            logger.error(f"Erreur lors du téléchargement du fichier: {filename}")
