import bot
import scrapper
import asyncio
import os

if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    api_id = os.environ['API_ID']
    api_hash = os.environ['API_HASH']
    bot_token = os.environ['BOT_TOKEN']
    subscriber_bot = bot.SubscriberBot(loop, api_id, api_hash, bot_token)
    scrapper_bot = scrapper.Scrapper(loop, subscriber_bot)
    futures = [
        asyncio.ensure_future(subscriber_bot.create_session()),
        asyncio.ensure_future(subscriber_bot.start_session()),
        asyncio.ensure_future(scrapper_bot.create_session()),
        asyncio.ensure_future(scrapper_bot.start_session())
    ]

    loop.run_until_complete(asyncio.gather(*futures))
