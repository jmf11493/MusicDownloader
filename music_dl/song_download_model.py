'''
Created on Aug 5, 2020

@author: Jeff
'''

from youtubesearchpython import SearchVideos
import csv
import os
import fnmatch
from bs4 import BeautifulSoup
import requests
import pafy
import time
import datetime
import re
from music_dl.audio_formatter import AudioFormatter 
from PyQt5.QtCore import QObject, pyqtSignal

class SongDownloadModel(QObject):
    '''
    classdocs
    '''
    skipped_total_change = pyqtSignal(int)
    song_total_change    = pyqtSignal(int)
    song_download_change = pyqtSignal(int)
    song_progress_change = pyqtSignal(int)
    song_failed_change   = pyqtSignal(int)
    
    estimate_change      = pyqtSignal(str)
    song_failed_name     = pyqtSignal(str)
    log_change           = pyqtSignal(str)

    def __init__(self, audio_formatter: AudioFormatter):
        '''
        Constructor
        '''
        super().__init__()
        self._stop_download       = False
        self._song_total          = 0
        self._skipped_total       = 0
        self._song_failed         = 0
        self._song_download_count = 0
        self.audio_formatter      = audio_formatter
        
        self._average_download_time  = 0
        self._download_time_array    = []
        self._average_convert_time   = 0
        self._convert_time_array     = []
        self._average_normalize_time = 0
        self._normalize_time_array   = []
    
    def skipped_total(self):
        self._skipped_total = self._skipped_total + 1
        self.skipped_total_change.emit(self._skipped_total)
    
    def song_total(self, num_songs):
        self._song_total = num_songs
        self.song_total_change.emit(self._song_total)
        self.song_progress()
    
    def song_downloaded(self):
        self._song_download_count = self._song_download_count + 1
        self.song_download_change.emit(self._song_download_count)
        
    def song_failed(self, song_name):
        self._song_failed = self._song_failed + 1
        self.song_failed_name.emit(song_name)
        self.song_failed_change.emit(self._song_failed)
        
    def song_progress(self):
        progress = ((self._song_download_count + self._skipped_total + self._song_failed)/self._song_total) * 100
        self.song_progress_change.emit(progress)
    
    def log(self, message):
        self.log_change.emit(message)
    
    def string_clean(self, text):
        replacements = [ "\\", "/", "|", "*", ":", "?", ">", "<", "\"", "[", "]", ",", "{", "}" ]
    
        for remove_char in replacements:
            text = text.replace( remove_char, "" )
        text.replace( "&amp;", "&" )
        
        # Remove all non ascii characters
        return re.sub(r'[^\x00-\x7f]', '', text)
    
    def stop_download(self, did_stop):
        if did_stop:
            self.log('Received Halt')
        self._stop_download = did_stop
    
    def get_number_of_songs(self, csv_file_path):
        # First read the csv and determine the song count for the progress bar
        csv_file   = open(csv_file_path, newline = '')
        # Subtract 1 for the header row
        song_total = len(list(csv.reader(csv_file))) - 1
        self.song_total(song_total)
    
    def download_callback(self, total, received, ratio, rate, eta ):
        global total_file_size
        total_file_size = total
        global file_received
        file_received = received
        
    def calculate_average(self, timer_start, timer_end, array):
        array.append(timer_end - timer_start)
        total_time = 0
        for time in array:
            total_time = total_time + time
    
        return total_time / len(array)
        
    def calculate_download_average(self, timer_start, timer_end):
        self._average_download_time = self.calculate_average(timer_start, timer_end, self._download_time_array)
    
    def calculate_normalize_average(self, timer_start, timer_end):
        self._average_normalize_time = self.calculate_average(timer_start, timer_end, self._normalize_time_array)
    
    def calculate_convert_average(self, timer_start, timer_end):
        self._average_convert_time = self.calculate_average(timer_start, timer_end, self._convert_time_array)
    
    def calc_estimated_time(self, normalize_flag, convert_flag):
        time_estimate = self._average_download_time
        
        if convert_flag:
            time_estimate = time_estimate + self._average_convert_time
            
        if normalize_flag:
            time_estimate = time_estimate + self._average_normalize_time
        
        time_estimate   = int(time_estimate)
        remaining_songs = self._song_total - self._song_download_count - self._song_failed - self._skipped_total
        remaining_time  = time_estimate * remaining_songs
        
        self.estimate_change.emit(str(datetime.timedelta(seconds=remaining_time)))
        
    
    def start_download(self, csv_file_path, output_directory, normalize_flag, convert_flag, sleep_time, download_retry, retry_scrape_max):
        self.log("CSV File Path: " + csv_file_path)
        self.log("Output Directory: " + output_directory)
        self.log("Normalize Audio: " + str(normalize_flag))
        self.log("Convert: " + str(convert_flag))
        self.log("Retry delay: " + str(sleep_time) + " seconds")
        self.log("Download retry: " + str(download_retry))
        self.log("Web scrape retry: " + str(retry_scrape_max))
        
        self._skipped_total = 0
        self._song_download_count = 0
        self._song_failed = 0
        self.get_number_of_songs(csv_file_path)
        
        official_audio = "+official+audio"
        search = ""
        root_dir = output_directory
        if not root_dir:
            self.log("output directory is empty")
            return
        
        if not os.path.exists(root_dir):
            self.log("directory missing")
        else:
            self.log("directory exists")
            
        # Check for kill signal
        if self._stop_download:
            self.log('Stopped Execution')
            return
            
        csv_file = open(csv_file_path, newline = '')
        csv_reader = csv.reader(csv_file, delimiter = ',')
        row_count = -1
        for row in csv_reader:
            row_count = row_count + 1
            if row_count == 0:
                continue
            self.log(str(row))
            name         = self.string_clean(row[1])
            band         = self.string_clean(row[2])
            album        = self.string_clean(row[3])
            track_number = self.string_clean(row[5])
            duration_ms  = self.string_clean(row[6])
            year         = ''
                
            # todo escape html characters before sending to query
            directory = root_dir + "\\" + band + "\\" + album
        
            # Check for kill signal
            if self._stop_download:
                self.log('Stopped Execution')
                return
        
            if not os.path.exists(directory):
                self.log( "Creating new directory: " + directory )
                try:
                    os.makedirs(directory)
                    self.log("Directory created")
                except OSError as err:
                    self.log("Directory creation failure: " + err)
            else:
                self.log("Directory exists")
            download_file = directory + "\\" + name
            
            file_found = False
            
            # Check for kill signal
            if self._stop_download:
                self.log('Stopped Execution')
                return
            
            # Check if the file already exists
            for file_name in os.listdir(directory):
                # maybe add the file extension here...
                if fnmatch.fnmatch(file_name, name + ".*"):
                    # could convert old files here...
                    file_found = True
                    break
                
            if file_found:
                self.log("File exists, skipping: " + download_file )
                self.skipped_total()
                continue
            
            suffix = ""
            
            # This could be a config option
            use_official_audio = True
            if use_official_audio:
                suffix = official_audio
            
            search = band + " " + name
#             search = band.replace(" ", "+") + "+" + name.replace(" ", "+") + suffix
            self.log("Searching for: " + search)
        
            # Check for kill signal
            if self._stop_download:
                self.log('Stopped Execution')
                return
        
            search_results = SearchVideos( search, offset = 1, mode = "json", max_results = 3 )
            self.log( 'Search results: ' + search_results.links[0] )
            youtube_id = search_results.links[0]
            # Check for kill signal
            if self._stop_download:
                self.log('Stopped Execution')
                return
    
            if youtube_id == '':
                self.log('Youtube id was not found for ' + name + ', skipping')
                self.song_failed(band + '-' + name)
                continue
    
            self.log("youtube id: " + str(youtube_id))
            try:
                video = pafy.new(youtube_id)
            except Exception as err:
                self.log("pafy failed: " + str(err))
            # encoding may fail sometimes with the video title
            if video.title:
                self.log("youtube title: " + video.title)
            else:
                self.log("youtube title: Warning - There was a problem retrieving the video title")
        
            audio_stream = video.getbestaudio("m4a")
            download_file_path = download_file + "." + audio_stream.extension
            retry = 0
            did_download = False
            while ( retry < download_retry and not did_download ):
                retry = retry + 1
                global total_file_size
                global file_received
                self.log("Attempting to download: " + name + " - Attempt #" + str(retry))
                
                download_timer_start = time.time()
                
                audio_stream.download(download_file_path, quiet=True, callback=self.download_callback )
                self.log("Downloaded: " + name)
                if total_file_size < 50000:
                    self.log(name + " did not finish downloading or file size is too small to be a valid download")
                    self.log("file size: " + str(total_file_size))
                    self.log("file received: " + str(file_received))
                    self.log("Removing file: " + download_file_path )
                    os.remove(download_file_path)
                    self.log('Waiting ' + str(sleep_time) + ' seconds before retrying')
                    time.sleep(sleep_time)
                else:
                    download_timer_end = time.time()
                    self.log(name + " downloaded successfully")
                    self.calculate_download_average(download_timer_start, download_timer_end)
                    did_download = True
                    total_file_size = 0
                    file_received = 0
                    
            # Check for kill signal
            if self._stop_download:
                self.log('Stopped Execution')
                return
             
            if not did_download:
                #reset the count
                total_file_size = 0
                file_received = 0
                self.log("Failed to download: " + name + " after " + str(download_retry) + " attempts")
                self.song_failed(band + '-' + name)
                continue
            self.song_downloaded()
            self.song_progress()
            self.log("downloaded file: " + download_file_path)
            
            # Check for kill signal
            if self._stop_download:
                self.log('Stopped Execution')
                return
            # audio adjust m4a file
            if normalize_flag:
                normalize_timer_start = time.time()
                self.audio_formatter.normalize_audio( download_file_path, self )
                normalize_timer_end = time.time()
                self.calculate_normalize_average(normalize_timer_start, normalize_timer_end)
            
            # Check for kill signal
            if self._stop_download:
                self.log('Stopped Execution')
                return            
                
            if convert_flag:
                # convert file
                convert_timer_start = time.time()
                mp3_path = self.audio_formatter.convert_to_mp3( directory, name, download_file_path, self )
                # Check for kill signal
                if self._stop_download:
                    self.log('Stopped Execution')
                    return
                
                # add meta data
                self.audio_formatter.add_meta_data(mp3_path, name, band, album, year, track_number, self)
                convert_timer_end = time.time()
                self.calculate_convert_average(convert_timer_start, convert_timer_end)
            self.log("Done")
            self.calc_estimated_time(normalize_flag, convert_flag)
        self.log("Finished downloading all songs")
        self.log("-----End of Log-----")
        return