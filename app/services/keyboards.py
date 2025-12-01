# stdlib
import logging
from datetime import UTC, datetime, timedelta
import calendar

# third-party
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.exceptions import TelegramBadRequest
import loguru
from app.services.parse_xlsx import Day, compose_schedule

logger = loguru.logger


router = Router()


async def get_inline_calendar_markup(month, year, schedule):

    flat: list[Day] = [x for sub in schedule for x in sub]
    length = len(flat)

    days_keyboard = [
        [
            InlineKeyboardButton(
                text=f"{flat[day_idx].date.day}",
                callback_data=f"{month}/{flat[day_idx].date.day}",
            )
            for day_idx in range(row, row + 8 if row + 8 < length else length)
            if flat[day_idx].date.month == month
        ]
        for row in range(0, length + 1, 8)
    ]

    builder = InlineKeyboardBuilder(days_keyboard).row(
        InlineKeyboardButton(text="<", callback_data=f"<"),
        InlineKeyboardButton(
            text=f"{month}/{year}",
            callback_data=f"todo",
        ),
        InlineKeyboardButton(text=">", callback_data=f">"),
    )
    return builder.as_markup()
