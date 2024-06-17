import os
from dotenv import load_dotenv

load_dotenv()

def get_env_variable(key: str) -> str:
    value = os.getenv(key)
    if not value:
        raise ValueError(f"La variable d'environnement {key} n'est pas définie.")
    return value