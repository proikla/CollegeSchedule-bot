# stdlib
import asyncio
import os

# third-party
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from loguru import logger

# local
import app.config as config

from app.handlers.start import router as start_router

dp = Dispatcher()
TOKEN = config.token

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

# todo: see app/handlers/start.py:20.
# todo: users can upload the schedule.
# todo: maybe rework Schedule structure.
# todo: add a way of viewing the schedule using an inline keyboard.


async def main() -> None:
    # register routers
    dp.include_router(start_router)

    logger.info("Bot started!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    if os.name == "nt":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(main())
