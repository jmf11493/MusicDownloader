'''
Created on Aug 5, 2020

@author: Jeff
'''

import os
import eyed3
from pydub import AudioSegment

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
        # TODO make this a configuration
        audio_adjust = -20.0
        if(audio_file.endswith('.m4a')):
            model.log("Normalizing Audio")
            try:
                audio_segment = AudioSegment.from_file( audio_file, "m4a" )
                change_in_dBFS = audio_adjust - audio_segment.dBFS
                normalized = audio_segment.apply_gain( change_in_dBFS )
                normalized.export( audio_file, format="mp4" )
            except:
                model.log("Failed to normalize audio")
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

    def add_meta_data(self, file_name, name, band, album, year, track_number, model):
        if file_name.endswith('.mp3'):
            model.log("Adding metadata")
            music_file = eyed3.load( file_name )
            music_file.tag.artist = band
            music_file.tag.album = album
            music_file.tag.title = name
            music_file.tag.track_num = track_number
            music_file.tag.save()
        