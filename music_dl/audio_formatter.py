'''
Created on Aug 5, 2020

@author: Jeff
'''

from pydub import AudioSegment
from mutagen.mp4 import MP4

class AudioFormatter(object):
    '''
    classdocs
    '''
    
    def normalize_audio(self, audio_file, model):
        # TODO is there a way to normalize audio without using ffmpeg or libav???
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

    def add_meta_data(self, file_name, name, band, album, year, track_number, model):
        # Use mutagen to add metadata
        # https://mutagen.readthedocs.io/en/latest/
        # https://stackoverflow.com/questions/44895095/is-it-possible-to-add-id3-tags-to-m4a-files-using-mutagen
        if file_name.endswith('.m4a'):
            try:
                model.log("Adding metadata")
                tags = MP4(file_name).tags
                tags["\xa9nam"] = name
                tags["\xa9ART"] = band
                tags["\xa9alb"] = album
                tags["\xa9day"] = year
                tags.save(file_name)
            except:
                model.log("Failed to add meta data, " + file_name + " may be corrupt")
        