from telethon import TelegramClient, events
import configparser
from bot import SubscriberBot


class Scrapper:

    def __init__(self, loop, bot: SubscriberBot):
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        self.api_id = int(self.config.get('API', 'api_id'))
        self.api_hash = self.config.get('API', 'api_hash')
        self.client: TelegramClient
        self.event_loop = loop
        self.subscriber_bot = bot

    async def create_session(self):
        self.client = TelegramClient('sessions/scrapper', self.api_id, self.api_hash)

        @self.client.on(events.NewMessage)
        async def forward_to_bot(event):
            sender = await event.get_sender()
            sender_username = sender.username
            if ('@' + sender_username) in self.subscriber_bot.subscriptions \
                    and self.subscriber_bot.subscriber != -1:
                await self.client.send_message(self.subscriber_bot.subscriber, event.message)

    async def start_session(self):
        await self.client.start()
