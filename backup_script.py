import os
import time
from typing import List
from pathlib import Path
from datetime import datetime, timedelta
from collections import namedtuple

import django
from django.core import management

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'localcontexts.settings')
from dbbackup.storage import Storage
from dbbackup.management.commands import dbbackup


django.setup()


TIME_FORMAT = '%Y:%m:%d:%H:%M:%S'
IGNORED_FILES = ['gitkeep']
Interval = namedtuple('Interval', ['name', 'max_backups'])
INTERVALS = [
    Interval('day', 7),
    Interval('week', 5),
    Interval('month', 12),
    Interval('year', 4),
]


def truncate_datetime(dt: datetime, interval_name: str):
    """
    Rounds precision down to the nearest year, month, week, or day.
    """

    if interval_name == 'year':
        return datetime(year=dt.year, month=1, day=1)

    elif interval_name == 'month':
        return datetime(year=dt.year, month=dt.month, day=1)

    elif interval_name == 'week':
        # note start of week may be in previous month
        days_after_start_of_week = dt.weekday()
        return datetime(year=dt.year, month=dt.month, day=dt.day) - timedelta(days_after_start_of_week)

    elif interval_name == 'day':
        return datetime(year=dt.year, month=dt.month, day=dt.day)

    else:
        raise Exception('Invalid  Interval Name')


def should_save_new_file(interval: Interval, files: List[str]):
    if len(files) == 0:
        return True

    most_recent_file_name = Path(files[-1]).stem
    most_recent_file_datetime = datetime.strptime(most_recent_file_name, TIME_FORMAT)

    truncated_recent_file_time = truncate_datetime(most_recent_file_datetime, interval.name)
    truncated_current_time = truncate_datetime(datetime.now(), interval.name)

    # compare the truncated times to see if they are the same
    return truncated_recent_file_time != truncated_current_time


def run():
    storage = Storage()
    for interval in INTERVALS:
        try:
            files = storage.list_directory(path=interval.name)
        except:
            files = []

        if should_save_new_file(interval, files):
            file_path = f'{interval.name}/{time.strftime(TIME_FORMAT)}.psql'
            management.call_command(dbbackup.Command(), verbosity=0, output_filename=file_path)


        # prune, by removing the oldest x files in folder


if __name__ == '__main__':
    run()
