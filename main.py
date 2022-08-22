import bot
import scrapper
import asyncio

if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    subscriber_bot = bot.SubscriberBot(loop)
    scrapper_bot = scrapper.Scrapper(loop, subscriber_bot)
    futures = [
        asyncio.ensure_future(subscriber_bot.create_session()),
        asyncio.ensure_future(subscriber_bot.start_session()),
        asyncio.ensure_future(scrapper_bot.create_session()),
        asyncio.ensure_future(scrapper_bot.start_session())
    ]

    loop.run_until_complete(asyncio.gather(*futures))
