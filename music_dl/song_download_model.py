'''
Created on Aug 5, 2020

@author: Jeff
'''
import csv
import os
import fnmatch
import time
import datetime
from music_dl.audio_formatter import AudioFormatter
from music_dl.logger import Logger
from music_dl.youtube_search import YoutubeSearch
from music_dl.youtube_download import YoutubeDownload
from music_dl.song import Song
from PyQt5.QtCore import QObject, pyqtSignal


class SongDownloadModel(QObject):
    '''
    classdocs
    '''
    skipped_total_change = pyqtSignal(int)
    song_total_change = pyqtSignal(int)
    song_download_change = pyqtSignal(int)
    song_progress_change = pyqtSignal(int)
    song_failed_change = pyqtSignal(int)
    
    estimate_change = pyqtSignal(str)
    song_failed_name = pyqtSignal(str)
    log_change = pyqtSignal(str)

    def __init__(self):
        '''
        Constructor
        '''
        super().__init__()
        self._stop_download = False
        self._song_total = 0
        self._skipped_total = 0
        self._song_failed = 0
        self._song_download_count = 0
        self._logger = Logger(self.log_change)
        self.audio_formatter = AudioFormatter(self._logger)
        
        self._average_download_time = 0
        self._download_time_array = []
        self._average_convert_time = 0
        self._convert_time_array = []
        self._average_normalize_time = 0
        self._normalize_time_array = []
    
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
    
    async def async_search(self, search):
        await search.next()
    
    def stop_download(self, did_stop):
        if did_stop:
            self._logger.log_info('Received Halt')
        self._stop_download = did_stop
    
    def get_number_of_songs(self, csv_file_path):
        # First read the csv and determine the song count for the progress bar
        csv_file = open(csv_file_path, newline='')
        # Subtract 1 for the header row
        song_total = len(list(csv.reader(csv_file))) - 1
        csv_file.close()
        self.song_total(song_total)

    def create_directory(self, directory):
        if not os.path.exists(directory):
            self._logger.log_debug("Creating new directory: " + directory)
            try:
                os.makedirs(directory)
                self._logger.log_debug("Directory created")
            except OSError as err:
                self._logger.log_error("Directory creation failure: " + err)
        else:
            self._logger.log_debug("Directory exists")

    def check_file_exists(self, song_name, directory):
        file_found = False
        for file_name in os.listdir(directory):
            # maybe add the file extension here...
            if fnmatch.fnmatch(file_name, song_name + ".*"):
                file_found = True
                break
        return file_found
        
    def calculate_average(self, timer_start, timer_end, array):
        array.append(timer_end - timer_start)
        total_time = 0

        for time_avg in array:
            total_time = total_time + time_avg
    
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
        
        time_estimate = int(time_estimate)
        remaining_songs = self._song_total - self._song_download_count - self._song_failed - self._skipped_total
        remaining_time = time_estimate * remaining_songs
        
        self.estimate_change.emit(str(datetime.timedelta(seconds=remaining_time)))

    def start_download(self, csv_file_path, output_directory, normalize_flag, sleep_time, download_retry):
        self._logger.log_debug("CSV File Path: " + csv_file_path)
        self._logger.log_debug("Output Directory: " + output_directory)
        self._logger.log_debug("Normalize Audio: " + str(normalize_flag))
        self._logger.log_debug("Retry delay: " + str(sleep_time) + " seconds")
        self._logger.log_debug("Download retry: " + str(download_retry))
        
        self._skipped_total = 0
        self._song_download_count = 0
        self._song_failed = 0
        self.get_number_of_songs(csv_file_path)

        root_dir = output_directory
        if not root_dir or not os.path.exists(root_dir):
            self._logger.log_error("output directory is empty")
            return
            
        csv_file = open(csv_file_path, newline='')
        csv_reader = csv.reader(csv_file, delimiter=',')
        song_yt_ids = []
        row_count = -1

        for row in csv_reader:
            # Check for kill signal
            if self._stop_download:
                csv_file.close()
                self._logger.log_debug("Stopped Execution")
                return

            row_count = row_count + 1
            if row_count == 0:
                continue
            self._logger.log_debug(str(row))
            song = Song(row)
                
            directory = root_dir + "\\" + song.band + "\\" + song.album
            self.create_directory(directory)
            download_file = directory + "\\" + song.name

            if self.check_file_exists(song.name, directory):
                self._logger.log_info("File exists, skipping: " + download_file)
                self.skipped_total()
                continue

            # SEARCH
            best_match = YoutubeSearch(self._logger).search(song)
            self._logger.log_info('Search results: ' + best_match['id'])

            youtube_id = best_match['id']
            youtube_url = best_match['link']
            youtube_title = best_match['title']
            search = best_match['search']

            if youtube_id in song_yt_ids:
                self._logger.log_error('GOT THE SAME YOUTUBE ID!!! id:' + youtube_id + ' search: ' + search)
                self.song_failed(song.band + '-' + song.name)
                continue
            else:
                song_yt_ids.append(youtube_id)
    
            if youtube_id == '':
                # TODO make the search a retry attempt
                self._logger.log_error('Youtube id was not found for ' + song.name + ', skipping')
                self.song_failed(song.band + '-' + song.name)
                continue
    
            self._logger.log_info(search + " :: youtube title: " + youtube_title + " :: youtube id: " + str(youtube_id) + " url:" + youtube_url)

            # DOWNLOAD
            retry = 0
            did_download = False
            while retry < download_retry and not did_download:
                retry = retry + 1
                self._logger.log_info("Attempting to download: " + song.name + " - Attempt #" + str(retry))
                
                download_timer_start = time.time()
                download_file_path = YoutubeDownload(self._logger).download(youtube_url, song, directory, download_retry)
                if download_file_path:
                    self._logger.log_info("Downloaded: " + song.name)
                    did_download = True
                    download_timer_end = time.time()
                    self.calculate_download_average(download_timer_start, download_timer_end)
             
            if not did_download:
                self._logger.log_error("Failed to download: " + song.name + " after " + str(download_retry) + " attempts")
                self.song_failed(song.band + '-' + song.name)
                continue

            self.song_downloaded()
            self.song_progress()
            self._logger.log_info("downloaded file: " + download_file_path)

            # NORMALIZE
            if normalize_flag:
                normalize_timer_start = time.time()
                self.audio_formatter.normalize_audio(download_file_path)
                normalize_timer_end = time.time()
                self.calculate_normalize_average(normalize_timer_start, normalize_timer_end)

            # CONVERT
            convert_timer_start = time.time()
            mp3_path = self.audio_formatter.convert_to_mp3(directory, song.name, download_file_path)
            self.audio_formatter.add_meta_data(mp3_path, song)
            convert_timer_end = time.time()
            self.calculate_convert_average(convert_timer_start, convert_timer_end)
            
            self._logger.log_info("Done")
            self.calc_estimated_time(normalize_flag, True)
        self._logger.log_info("Finished downloading all songs")
        self._logger.log_info("-----End of Log-----")
        csv_file.close()
        return
