import time
from typing import List
from pathlib import Path
from datetime import datetime, timedelta
from collections import namedtuple

from django.core import management
from django.core.management.base import BaseCommand

from apscheduler.schedulers.background import BlockingScheduler

from dbbackup.storage import Storage
from dbbackup.management.commands import dbbackup


TIME_FORMAT = '%Y:%m:%d:%H:%M:%S'
Interval = namedtuple('Interval', ['name', 'max_backups'])
INTERVALS = [
    Interval('day', 7),
    Interval('week', 5),
    Interval('month', 12),
    Interval('year', 4),
]


class Command(BaseCommand):
    help = "Runs backup code"
    storage = Storage()

    @staticmethod
    def truncate_datetime(dt: datetime, interval_name: str) -> datetime:
        """
        Rounds datetime precision down to the nearest year, month, week, or day.
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
            raise Exception('Invalid Interval Name')

    def create_backup(self, file_path: str) -> bool:
        # returns True when backup was created and False otherwise
        try:
            management.call_command(dbbackup.Command(), verbosity=0, output_filename=file_path)
            return True
        except (Exception,):
            self.stdout.write(
                self.style.ERROR(f'Error Creating File {file_path}')
            )
            return False

    def should_save_new_file(self, interval: Interval, files: List[str]) -> bool:
        if len(files) == 0:
            return True

        most_recent_file_name = Path(files[-1]).stem
        most_recent_file_datetime = datetime.strptime(most_recent_file_name, TIME_FORMAT)

        truncated_recent_file_time = self.truncate_datetime(most_recent_file_datetime, interval.name)
        truncated_current_time = self.truncate_datetime(datetime.now(), interval.name)

        # compare the truncated times to see if they are the same
        return truncated_recent_file_time != truncated_current_time

    def remove_oldest_file(self, interval: Interval, files_in_folder):

        # when folder is empty, skip removing the oldest file
        if len(files_in_folder) == 0:
            return

        # when the file count hasn't reached the limit, skip removing the oldest file
        if len(files_in_folder) <= interval.max_backups:
            return

        oldest_file_name = files_in_folder[0]
        oldest_file_path = f'{interval.name}/{oldest_file_name}'
        try:
            self.storage.delete_file(oldest_file_path)
            self.stdout.write(
                self.style.SUCCESS(f'Deleted Old Backup For {interval.name} Named {oldest_file_name}')
            )
        except (Exception,):
            self.stdout.write(
                self.style.ERROR(f'Error Deleting File {oldest_file_name}')
            )

    def job(self):
        for interval in INTERVALS:
            try:
                files = self.storage.list_directory(path=interval.name)
                files.sort()
            except (Exception,):
                files = []

            if self.should_save_new_file(interval, files):
                file_name = f'{time.strftime(TIME_FORMAT)}.psql'
                file_path = f'{interval.name}/{file_name}'
                self.stdout.write(
                    self.style.SUCCESS(f'Creating Backup For {interval.name} Named {file_name}')
                )
                creation_successful = self.create_backup(file_path)

                if creation_successful:
                    files.append(file_name)
                    self.remove_oldest_file(interval, files)

        self.stdout.write(
            self.style.SUCCESS('Backup Script Complete')
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Running backup Script')
        )
        scheduler = BlockingScheduler()
        scheduler.add_job(self.job, 'cron', hour=23, minute=30)
        scheduler.start()
