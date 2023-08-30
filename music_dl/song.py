from typing import List
from music_dl.validator import Validator


class Song:
    '''
    classdocs
    '''
    name = ''
    band = ''
    album = ''
    genre = ''
    year = ''
    duration_seconds = 0

    def __init__(self, row: List[str]):
        '''
        Constructor
        '''
        super().__init__()
        self.name = Validator.string_clean(row[2])
        self.band = Validator.string_clean(row[4])
        self.album = Validator.string_clean(row[3])
        self.genre = Validator.string_clean(row[10].split(',')[0])
        year = row[5]
        if "/" in year:
            year = year.split("/")
            year = year[len(year) - 1]
        self.year = Validator.string_clean(year)
        duration_ms = row[6]
        self.duration_seconds = int(duration_ms)/1000
