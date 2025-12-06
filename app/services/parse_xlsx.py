from collections import defaultdict
from typing import Generator
import loguru
import pandas as pd
from datetime import datetime, timedelta
import os
import re

logger = loguru.logger
WEEKDAYS = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота"]


class Class:
    def __init__(self, subject, classroom):
        self.subject = subject
        self.classroom = classroom

    def __format__(self, format_spec):
        if not (self.subject and self.classroom):
            return ""
        return f"{self.classroom} - {self.subject}"


class Day:
    def __init__(self, date, classes, name):
        self.date = datetime(date.year, date.month, date.day)
        self.classes: list[Class] = classes
        self.name: str = name

    def __format__(self, format_spec):
        return f"*{self.name.capitalize()} {self.date.strftime('%d.%m.%y')}*\n{''.join([f"{idx+1}: {_class}\n" for idx, _class in enumerate(self.classes)])}"


def merge_days_by_slot(days):
    groups = defaultdict(list)
    for d in days:
        groups[d.date.date()].append(d)

    merged = []
    for date_key, group in groups.items():
        group.sort(key=lambda d: d.date)  # chronological
        max_len = max(len(d.classes) for d in group)  # longest slot count
        slots = [""] * max_len

        for d in group:
            for i, cls in enumerate(d.classes):
                s = format(cls, "")  # uses Class.__format__
                if not slots[i]:
                    slots[i] = s
                else:
                    slots[i] = f"{slots[i]} | {s}" if s else f"{slots[i]}"

        first = group[0]
        merged.append(Day(first.date, slots, first.name))

    return sorted(merged, key=lambda d: d.date)


def read_data() -> list[pd.DataFrame]:
    """
    Read all xlsx files in app/data/ and return dataframes

    :return: list of dataframes
    :rtype: list[DataFrame]
    """
    dataframes: list[pd.DataFrame] = []
    data_path = "app/data/"

    for filename in os.listdir(data_path):
        dataframes.append(pd.read_excel(os.path.join(data_path, filename), header=None))

    return dataframes


def is_weekday(s: str) -> str | bool:
    for weekday in WEEKDAYS:
        if weekday in s:
            return weekday

    return False


def calculate_classes_amount(df):
    """
    figure out how many classes each day has

    Returns:
        dict: `{<weekday>: <amount_of_classes>}`
    """
    rows = df[0]
    days_to_classes_amount = {}
    classes_count = 0
    current_day = ""

    for row in rows:
        if not pd.notna(row) and current_day:
            classes_count += 1

        if isinstance(row, str):
            row = row.strip().lower()

            if weekday := is_weekday(row):
                # * store info
                if classes_count:
                    days_to_classes_amount[current_day] = classes_count
                    classes_count = 0

                # * start counting on a new day
                current_day = weekday
                classes_count += 1

    days_to_classes_amount[current_day] = classes_count
    return days_to_classes_amount


def find_classes_columns(df: pd.DataFrame, starting_row) -> list:
    """find out what columns contain classes.

    Returns:
        list: Indecies of the columns that contain classes info.
    """
    columns = []
    row = starting_row - 1
    for i in range(len(df.columns)):
        value = df[i][row]
        if re.search(r"\d+\.\d+-\d+\.\d+", str(value)):
            columns.append(i)

    return columns


# find what row classes start on
def find_starting_row(df) -> int:
    """Find the row classes start on.

    Returns:
        int: Index of the row classes start on.
    """
    # usually starting row is on the same row 'понедельник' is on, which is also the first column
    count = 0
    for row in df[0]:
        if isinstance(row, str) and WEEKDAYS[0] in row.strip().lower():
            return count
        count += 1


def find_starting_date(df, cached_starting_row: int, cached_classes_columns: list):
    "Find the date of the first day in the schedule."
    date_row = cached_starting_row - 1
    return (
        df[cached_classes_columns[0]]
        .astype(str)
        .tolist()[date_row]
        .replace(" ", "")
        .split("-")[0]
    )


def compose_schedule():
    # start wit starting row
    # * for each file in data/
    schedule = []
    data = read_data()
    cache = calculate_cache(data)
    for idx, df in enumerate(data):

        cached_starting_row, cached_classes_amount, cached_classes_columns = cache[idx]

        start_date = find_starting_date(
            df=df,
            cached_classes_columns=cached_classes_columns,
            cached_starting_row=cached_starting_row,
        )

        start_date = datetime.strptime(
            f"{start_date}.{datetime.now().year}", "%d.%m.%Y"
        )
        days_processed = 0

        # iterate thru columns that contain classes. (weeks)
        for week_idx in cached_classes_columns:  # [3,5,...]
            i = cached_starting_row
            j = i + cached_classes_amount.get("понедельник")

            for day_name in WEEKDAYS:  # iterate thru days in that column
                j = i + cached_classes_amount.get(day_name, 0)

                subjects = df.iloc[i:j, week_idx].fillna("").astype(str).tolist()
                classrooms = df.iloc[i:j, week_idx + 1].fillna("").astype(str).tolist()

                classes = [
                    Class(subject.strip(), classroom.strip())
                    for subject, classroom in zip(subjects, classrooms)
                ]

                day = Day(
                    start_date + timedelta(days=days_processed),
                    classes,
                    day_name,
                )

                schedule.append(day)
                days_processed += 1
                i = j

            days_processed += 1  # one for Sunday

    return merge_days_by_slot(schedule)


def get_classes_for_today():
    schedule = compose_schedule()
    for day in schedule:
        if day.date == datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0
        ):
            return day


def calculate_cache(data: list[pd.DataFrame]) -> list[list]:
    """
    todo

    :param data: Description
    :type data: list[pd.DataFrame]
    :return: List of lists - [[cached_row, cached_amount, cached_columns], [...]]
    :rtype: list[list]
    """
    cache = []
    for df in data:
        cache.append([])

        starting_row = find_starting_row(df)
        classes_amount = calculate_classes_amount(df)
        classes_columns = find_classes_columns(df, starting_row)

        cache[-1].append(starting_row)
        cache[-1].append(classes_amount)
        cache[-1].append(classes_columns)

    return cache


# todo: you can merge cached_starting_row and cached_classes_amount into one thing
