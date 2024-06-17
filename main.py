import logging
from config.config import get_env_variable
from auth.auth import DiscordAuth
from discord_api.discord_api import DiscordAPI
from webhook.webhook import DiscordWebhook
from DiscordBot.discord_bot import DiscordBot

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    try:
        auth_token = get_env_variable('AUTH_TOKEN')
        guild_id = get_env_variable('GUILD_ID')
        webhook_url = get_env_variable('WEBHOOK_URL')

        auth = DiscordAuth(auth_token)
        api = DiscordAPI(auth)
        webhook = DiscordWebhook(webhook_url)

        channels = api.retrieve_channels(guild_id)
        if channels:
            for channel in channels:
                api.retrieve_messages(channel.id, webhook)
        bot = DiscordBot(auth, webhook)
        bot.run()

    except ValueError as e:
        logging.error(str(e))
