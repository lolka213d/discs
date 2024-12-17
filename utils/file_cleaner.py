import os
import time
from datetime import datetime, timedelta

class FileCleaner:
    def __init__(self, directory: str, max_age_hours: int = 24):
        self.directory = directory
        self.max_age_hours = max_age_hours

    def clean_old_files(self):
        """Remove files older than max_age_hours"""
        now = datetime.now()
        for filename in os.listdir(self.directory):
            file_path = os.path.join(self.directory, filename)
            if os.path.isfile(file_path):
                file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                if now - file_time > timedelta(hours=self.max_age_hours):
                    try:
                        os.remove(file_path)
                        print(f"Removed old file: {filename}")
                    except Exception as e:
                        print(f"Error removing file {filename}: {e}")
