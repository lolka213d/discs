from .music_downloader import MusicDownloader
from .shazam_api import ShazamAPI
from .file_cleaner import FileCleaner

def clean_old_files(directory, hours=24):
    cleaner = FileCleaner(directory, hours)
    cleaner.clean_old_files()

__all__ = ['MusicDownloader', 'ShazamAPI', 'FileCleaner', 'clean_old_files']
