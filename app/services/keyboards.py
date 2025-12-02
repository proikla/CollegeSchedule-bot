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


async def get_inline_calendar_markup(month, year, schedule, step=6):

    length = len(schedule)

    days_keyboard = [
        [
            InlineKeyboardButton(
                text=f"{schedule[day_idx].date.day}",
                callback_data=f"{month}/{schedule[day_idx].date.day}",
            )
            for day_idx in range(row, row + step if row + step < length else length)
            if schedule[day_idx].date.month == month
        ]
        for row in range(0, length + 1, step)
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
