# third-party
from calendar import Day
from datetime import datetime
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CallbackQuery,
)
from aiogram.fsm.context import FSMContext
from loguru import logger

from app.services.keyboards import get_inline_calendar_markup
from app.services.parse_xlsx import compose_schedule, get_classes_for_today

router = Router()

schedule = compose_schedule(start_date="03.11")
flat: list[Day] = [x for sub in schedule for x in sub]


# todo: add comments.


def find_day(schedule, day_to_find: int):
    logger.debug("Find day triggered")
    for day in flat:
        if f"{day.date.month}/{day.date.day}" == day_to_find:
            return day


@router.callback_query(F.data.regexp(r"[><]"))
async def handle_callback(callback: CallbackQuery, state: FSMContext):
    logger.debug(
        f"Callback handled from {callback.from_user.username}-{callback.from_user.id}"
    )
    bot = callback.bot

    msg_id = await state.get_value("schedule_msg_id")
    month = await state.get_value("month")

    if callback.data == "<":
        month -= 1
        await bot.edit_message_reply_markup(
            chat_id=callback.from_user.id,
            message_id=msg_id,
            reply_markup=await get_inline_calendar_markup(
                month=month, year=2025, schedule=schedule
            ),
        )
    if callback.data == ">":
        month += 1
        await bot.edit_message_reply_markup(
            chat_id=callback.from_user.id,
            message_id=msg_id,
            reply_markup=await get_inline_calendar_markup(
                month=month, year=2025, schedule=schedule
            ),
        )
    await state.update_data({"month": month})
    await callback.answer()


@router.callback_query(F.data.regexp(r"\d+"))
async def handle_callback(callback: CallbackQuery, state: FSMContext):
    bot = callback.bot
    msg_id = await state.get_value("schedule_msg_id")

    for day in flat:
        logger.debug(day.date.day)
        if f"{day.date.month}/{day.date.day}" == callback.data:
            try:
                await bot.edit_message_text(
                    text=f"{day}",
                    chat_id=callback.from_user.id,
                    message_id=msg_id,
                    reply_markup=await get_inline_calendar_markup(
                        day.date.month, day.date.year, schedule=schedule
                    ),
                )
            except (
                Exception
            ) as e:  # probs Telegram Bad Request error - tried to edit to the same text.
                pass

    await callback.answer()


@router.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    """
    This handler receives messages with `/start` command
    """
    logger.debug(
        f"/start message from {message.from_user.username}-{message.from_user.id}"
    )
    classes = get_classes_for_today(
        "03.11"
    )  # todo user has to set the `start_date` thru the bot somehow

    msg: Message = await message.answer(
        text=f"{classes}",
        reply_markup=await get_inline_calendar_markup(
            12, 2025, compose_schedule(start_date="03.11")
        ),
    )
    await state.set_data({"schedule_msg_id": msg.message_id, "month": 12})
