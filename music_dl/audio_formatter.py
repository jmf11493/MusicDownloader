'''
Created on Aug 5, 2020

@author: Jeff
'''
import os
import sys
import eyed3
from pydub import AudioSegment
from mutagen.mp4 import MP4
from music_dl.song import Song
from music_dl.logger import Logger


class AudioFormatter(object):
    '''
    classdocs
    '''

    _logger = None

    def __init__(self, logger: Logger):
        '''
        Constructor
        '''
        self._logger = logger
        dir = os.getcwd()
        logger.log_info("MEIPASS: " + sys._MEIPASS)
        logger.log_info("Current dir: " + dir)

        ffmpeg = dir + "/ffmpeg/ffmpeg.exe"
        ffprobe = dir + "/ffmpeg/ffprobe.exe"

        logger.log_info("ffmpeg dir: " + ffmpeg)
        AudioSegment.converter = ffmpeg
        AudioSegment.ffmpeg = ffmpeg
        AudioSegment.ffprobe = ffprobe
        logger.log_info("audio segment dir: " + AudioSegment.converter)

    def normalize_audio(self, audio_file):
        # TODO make this a configuration?
        # https://stackoverflow.com/questions/42492246/how-to-normalize-the-volume-of-an-audio-file-in-python
        audio_adjust = -20.0
        self._logger.log_info("Normalizing Audio")
        # TODO open in a sub process?
        # https://stackoverflow.com/questions/43000394/python-windowserror-error-6-the-handle-is-invalid/43004804#43004804
        # proc = subprocess.Popen(args, shell=True, stdout=open(outimploc, 'w'), stderr=open(outimplocerr, 'w'),
        #                         stdin=subprocess.PIPE, cwd=self.tranusConf.workingDirectory).communicate()
        # https://stackoverflow.com/questions/22284461/pydub-windowserror-error-2-the-system-can-not-find-the-file-specified
        try:
            self._logger.log_info("audio segment dir, in normalize: " + AudioSegment.converter)
            audio_segment = AudioSegment.from_file(audio_file)
            change_in_dBFS = audio_adjust - audio_segment.dBFS
            normalized = audio_segment.apply_gain(change_in_dBFS)
            normalized.export(audio_file, format="mp4")
        except Exception as exc:
            self._logger.log_error("Failed to normalize audio")
            self._logger.log_error(str(exc))

    def convert_to_mp3(self, directory, file_name, file_path):
        path_to_mp3 = file_path
        self._logger.log_info("Converting file: " + file_path)
        try:
            # If audio is too long we can get a memory error
            mp4_file_audio = AudioSegment.from_file(file_path)
            mp3_file = directory + "\\" + file_name + ".mp3"
            mp4_file_audio.export(mp3_file)
            path_to_mp3 = mp3_file
            if os.path.isfile(mp3_file):
                self._logger.log_info("Removing mp4 file: " + file_path)
                os.remove(file_path)
        except:
            self._logger.log_error("Error converting file to mp3: " + file_name)

        return path_to_mp3

    def add_meta_data(self, file_name, song: Song):
        if file_name.endswith('.mp3'):
            self._logger.log_info("Adding metadata")
            music_file = eyed3.load(file_name)
            music_file.tag.genre = song.genre
            music_file.tag.artist = song.band
            music_file.tag.album = song.album
            music_file.tag.title = song.name
            music_file.tag.release_date = song.year
            music_file.tag.save()
        # Use mutagen to add metadata
        # https://mutagen.readthedocs.io/en/latest/
        # https://stackoverflow.com/questions/44895095/is-it-possible-to-add-id3-tags-to-m4a-files-using-mutagen
        MP4._padding = 0
        if file_name.endswith('.m4a'):
            try:
                self._logger.log_info("Adding metadata")
                tags = MP4(file_name).tags
                tags["\xa9nam"] = song.name
                tags["\xa9ART"] = song.band
                tags["\xa9alb"] = song.album
                tags["\xa9day"] = song.year
                tags["\xa9gen"] = song.genre
                tags.save(file_name)
            except Exception as exc:
                self._logger.log_error("Failed to add meta data, " + file_name + " may be corrupt")
                self._logger.log_error(str(exc))
