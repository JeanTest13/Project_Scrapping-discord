class DiscordAuth:
    def __init__(self, auth_token: str):
        self.auth_token = auth_token

    def get_headers(self) -> dict:
        return {'Authorization': self.auth_token}
