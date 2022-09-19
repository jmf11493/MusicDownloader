'''
Created on Aug 5, 2020

@author: Jeff
'''
import subprocess
import os
import sys
import eyed3
from pydub import AudioSegment
from mutagen.mp4 import MP4
MP4._padding = 0

class AudioFormatter(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        AudioSegment.converter = "ffmpeg\\bin\\ffmpeg.exe"
        AudioSegment.ffmpeg    = "ffmpeg\\bin\\ffmpeg.exe"
        AudioSegment.ffprobe   = "ffmpeg\\bin\\ffprobe.exe"


    def set_path(self, model):
        # https://stackoverflow.com/questions/30006722/os-environ-not-setting-environment-variables
        if os.path.exists('ffmpeg') and os.path.exists('ffmpeg\\bin'):
            path = os.environ['PATH']
            abs_path = '"' + os.path.abspath('ffmpeg\\bin') + '";'
            if abs_path not in path.split(';'):
                os.environ['PATH'] += ';' + abs_path

    def normalize_audio(self, audio_file, model):
#         relative_ffmpeg_path = 'ffmpeg'
#         ffmpeg_path = ''
#         path = os.environ['PATH']
#         if hasattr(sys, '_MEIPASS'):
#             ffmpeg_path = os.path.join(sys._MEIPASS, relative_ffmpeg_path)
#             model.log("ffmpeg path1: " + str(ffmpeg_path))
#         else:
#             ffmpeg_path = os.path.join(os.path.abspath("."), relative_ffmpeg_path)
#             model.log("ffmpeg path2: " + str(ffmpeg_path))
#         if ffmpeg_path not in path.split(';'):
#             os.environ['PATH'] += ';' + ffmpeg_path + '\\'
#             model.log("os path: " + str(os.environ['PATH']))
#         AudioSegment.converter = os.path.join(ffmpeg_path, "ffmpeg.exe")
#         AudioSegment.ffmpeg    = os.path.join(ffmpeg_path, "ffmpeg.exe")
#         AudioSegment.ffprobe   = os.path.join(ffmpeg_path, "ffprobe.exe")
        # TODO make this a configuration
        audio_adjust = -20.0
        if(audio_file.endswith('.m4a')):
            model.log("Normalizing Audio")
            try:
#                 audio_segment = subprocess.Popen(AudioSegment.from_file( audio_file, "m4a" ),shell=True)
                audio_segment = AudioSegment.from_file(audio_file, "m4a")
                change_in_dBFS = audio_adjust - audio_segment.dBFS
                normalized = audio_segment.apply_gain(change_in_dBFS)
                normalized.export(audio_file, format="mp4")
            except Exception as exc:
                model.log("Failed to normalize audio")
                model.log("Error: " + str(exc))
        else:
            model.log("Audio file not m4a, skipping normalization: " + audio_file)

    def convert_to_mp3(self, directory, file_name, file_path, model):
        path_to_mp3 = file_path
        self.set_path(model)
        if(file_path.endswith('.m4a')):
            model.log( "Converting file: " + file_path )
            try:
                mp4_file_audio = AudioSegment.from_file( file_path, "m4a" )
                mp3_file = directory + "\\" + file_name + ".mp3"
                mp4_file_audio.export( mp3_file )
                path_to_mp3 = mp3_file
                if(os.path.isfile(mp3_file)):
                    model.log("Removing mp4 file: " + file_path)
                    os.remove(file_path)
            except:
                model.log( "Error converting file to mp3: " + file_name )

        return path_to_mp3

    def add_meta_data(self, file_name, name, band, album, year, track_number, genre, model):
        if file_name.endswith('.mp3'):
            model.log("Adding metadata")
            music_file = eyed3.load( file_name )
            music_file.tag.genre  = genre
            music_file.tag.artist = band
            music_file.tag.album = album
            music_file.tag.title = name
            music_file.tag.release_date = year
#             music_file.tag.track_num = track_number
            music_file.tag.save()
        # Use mutagen to add metadata
        # https://mutagen.readthedocs.io/en/latest/
        # https://stackoverflow.com/questions/44895095/is-it-possible-to-add-id3-tags-to-m4a-files-using-mutagen
        MP4._padding = 0
        if file_name.endswith('.m4a'):
            try:
                model.log("Adding metadata")
                tags = MP4(file_name).tags
                tags["\xa9nam"] = name
                tags["\xa9ART"] = band
                tags["\xa9alb"] = album
                tags["\xa9day"] = year
                tags["\xa9gen"] = genre
                tags.save(file_name)
            except Exception as exc:
                model.log("Failed to add meta data, " + file_name + " may be corrupt")
                model.log("Error: " + str(exc))