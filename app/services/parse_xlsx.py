from typing import Generator
import pandas as pd

df = pd.read_excel("app/data/schedule.xlsx", header=None)
from datetime import datetime, timedelta


WEEKDAYS = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота"]


class Class:
    def __init__(self, subject, classroom):
        self.subject = subject
        self.classroom = classroom

    def __format__(self, format_spec):
        return f"{self.classroom} - {self.subject}"


class Day:
    def __init__(self, date, classes, name):
        self.date = datetime(date.year, date.month, date.day)
        self.classes: list[Class] = classes
        self.name: str = name

    def __format__(self, format_spec):
        return f"*{self.name.capitalize()}*\n{''.join([f"{idx+1}: {_class}\n" for idx, _class in enumerate(self.classes)])}"


def calculate_classes_amount(df=df):
    """
    figure out how many classes a day has

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

            if row in WEEKDAYS:
                # * store info
                if classes_count:
                    days_to_classes_amount[current_day] = classes_count
                    classes_count = 0

                # * start counting on a new day
                current_day = row
                classes_count += 1

    days_to_classes_amount[current_day] = classes_count
    return days_to_classes_amount


def find_classes_columns(df=df) -> list:
    """find out what columns contain classes.

    Returns:
        list: Indecies of the columns that contain classes info.
    """
    # just a pattern thing, usually classes are in the columns from the third one
    return list(range(2, len(df.columns), 2))


# * room info columns are ez to get by ++ classes columns


# find what row classes start on
def find_starting_row(df=df) -> int:
    """Find the row classes start on.

    Returns:
        int: Index of the row classes start on.
    """
    # usually starting row is on the same row 'понедельник' is on, which is also the first column
    count = 0
    for row in df[0]:
        if isinstance(row, str) and row.strip().lower() == WEEKDAYS[0]:
            return count
        count += 1


def compose_schedule(df=df, start_date="03.11"):
    # start wit starting row
    classes_amount = calculate_classes_amount()
    start_date = datetime.strptime(start_date, "%d.%m").replace(
        year=datetime.now().year
    )
    days_processed = 0

    week = []
    schedule = []
    # * FOR EACH WEEK
    for week_idx in find_classes_columns():  # [3,5,...]
        # * FOR EACH DAY
        i = find_starting_row()
        j = i + classes_amount.get("понедельник")
        for day_name in WEEKDAYS:
            j = i + classes_amount.get(day_name, 0)

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

            days_processed += 1
            week.append(day)
            i = j

        days_processed += 1  # one for the Sunday
        schedule.append(week)
        week = []
        day = []
    return schedule


def get_classes_for_today(start_date: str):
    schedule = compose_schedule(start_date=start_date)
    for week in schedule:
        for day in week:
            if day.date == datetime.now().replace(
                hour=0, minute=0, second=0, microsecond=0
            ):
                return day


if __name__ == "__main__":
    schedule = compose_schedule()
    for week in schedule:
        for day in week:
            print(f"{day.name} ({day.date}):\n{day}\n")
