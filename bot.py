from telethon import TelegramClient, events
import configparser
import re


class SubscriberBot:

    def __init__(self, loop, api_id, api_hash, bot_token):
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        self.api_id = api_id
        self.api_hash = api_hash
        self.bot_token = bot_token
        self.bot: TelegramClient
        self.event_loop = loop

        self.subscriber = -1

        self.subscriptions = set()
        for sub in self.config.get('Subscriptions', 'usernames').split(','):
            self.subscriptions.add(sub)

    async def create_session(self):

        self.bot = TelegramClient('sessions/bot', self.api_id, self.api_hash)

        @self.bot.on(events.NewMessage(pattern='/start'))
        async def command_start(event):
            if self.subscriber != -1:
                reply_message = self.config.get('Messages', 'reject')
                await self.bot.send_message(event.sender_id, reply_message)
                return
            reply_message = self.config.get('Messages', 'start')
            sender_id = event.sender_id
            self.subscriber = sender_id
            await self.bot.send_message(sender_id, reply_message)

        @self.bot.on(events.NewMessage(pattern='/help'))
        async def command_help(event):
            reply_message = self.config.get('Messages', 'help')
            await self.bot.send_message(event.sender_id, reply_message)

        @self.bot.on(events.NewMessage(pattern='/subs'))
        async def command_subs(event):
            if self.subscriber != -1:
                reply_message = "Ваши текущие подписки:"
                for subb in self.subscriptions:
                    reply_message += "\n" + subb
                await self.bot.send_message(event.sender_id, reply_message)

        @self.bot.on(events.NewMessage(pattern='/addsub'))
        async def command_add_sub(event):
            if self.subscriber != -1:
                enter_message = self.config.get('Messages', 'enter_username_add')
                username = await request_username(event, enter_message)
                if username == '':
                    return
                self.subscriptions.add(username)
                save_subscriptions()

        @self.bot.on(events.NewMessage(pattern='/delsub'))
        async def command_del_sub(event):
            if self.subscriber != -1:
                enter_message = self.config.get('Messages', 'enter_username_del')
                username = await request_username(event, enter_message)
                if username == '':
                    return
                if username in self.subscriptions:
                    self.subscriptions.remove(username)
                    save_subscriptions()

        @self.bot.on(events.NewMessage(pattern='/cancel'))
        async def command_cancel(event):
            if self.subscriber != -1:
                self.subscriber = -1
                reply_message = self.config.get('Messages', 'cancel')
                await self.bot.send_message(event.sender_id, reply_message)

        def save_subscriptions():
            subs = ''
            for subb in self.subscriptions:
                subs += subb + ','
            self.config['Subscriptions']['usernames'] = subs[:-1]
            with open('config.ini', 'w') as f:
                self.config.write(f)

        async def request_username(event, enter_text: str):
            async with self.bot.conversation(await event.get_chat(), exclusive=True) as conv:
                flag = False
                while not flag:
                    await conv.send_message(enter_text)
                    answer = await conv.get_response()
                    if answer.text == 'отмена':
                        conv.cancel_all()
                        return ''
                    flag = re.fullmatch(r'@\w+', answer.text)
                await conv.send_message('Готово!')
                conv.cancel_all()
                return answer.text

    async def start_session(self):
        await self.bot.start(bot_token=self.bot_token)
        await self.bot.run_until_disconnected()
