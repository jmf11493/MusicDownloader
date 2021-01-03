'''
Created on Aug 5, 2020

@author: Jeff
'''

from music_dl.song_download_model import SongDownloadModel 
import threading

class SongDownloadController(object):
    '''
    classdocs
    '''


    def __init__(self, model: SongDownloadModel):
        '''
        Constructor
        '''
        self._model          = model
        self._normalize      = True
        self._csv_file       = ''
        self._output_file    = ''
        self._sleep_time     = 2
        self._download_try   = 5
        
    def normalize_change(self, value):
        self._normalize = value
        
    def csv_change(self, value):
        self._csv_file = value
    
    def output_change(self, value):
        self._output_file = value
        
    def csv_file_change(self, value):
        self._csv_file = value

    def output_dir_change(self, value):
        self._output_file = value
    
    
    def time_sleep_change(self, value):
        self._sleep_time = value
        
    def download_try_change(self, value):
        self._download_try = value
    
    def stop_download_click(self):
        self._model.stop_download(True)
    
    def start_download_click(self):
        thread = threading.Thread(target=self.download_thread)
        thread.start()
        
    def download_thread(self):
        self._model.stop_download(False)
        self._model.start_download(
            self._csv_file, 
            self._output_file, 
            self._normalize,
            self._sleep_time,
            self._download_try
        )