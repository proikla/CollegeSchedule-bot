# third-party
from datetime import datetime
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from loguru import logger

from app.services.parse_xlsx import compose_schedule, get_classes_for_today

router = Router()


@router.message(CommandStart())
async def command_start_handler(message: Message, state) -> None:
    """
    This handler receives messages with `/start` command
    """
    classes = get_classes_for_today(
        "03.11"
    )  # todo user has to set the `start_date` thru the bot somehow

    await message.answer(text=f"{classes}", parse_mode="Markdown")
