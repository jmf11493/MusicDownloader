'''
Created on Aug 5, 2020

@author: Jeff
'''
import asyncio
import json
from youtubesearchpython import SearchVideos
from youtubesearchpython.__future__ import VideosSearch
import csv
import os
import fnmatch
import pafy
import time
import datetime
import re
import audioread
from music_dl.audio_formatter import AudioFormatter 
from PyQt5.QtCore import QObject, pyqtSignal
from _overlapped import NULL

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
        self._debug_log           = False
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

    def log_debug(self, message):
        message = "DEBUG: " + message
        print(message)
        if self._debug_log:
            self.log(message)

    def log_warn(self, message):
        message = "WARN: " + message
        self.log(message)

    def log_error(self, message):
        message = "ERROR: " + message
        self.log(message)

    def log_info(self, message):
        message = "INFO: " + message
        self.log(message)

    def log(self, message):
        self.log_change.emit(message)
    
    async def async_search(self, search):
        await search.next()
    
    def string_clean(self, text):
        replacements = [ "\\", "/", "|", "*", ":", "?", ">", "<", "\"", "[", "]", ",", "{", "}" ]
    
        for remove_char in replacements:
            text = text.replace( remove_char, "" )
        text.replace( "&amp;", "&" )
        
        # Remove all non ascii characters
        return re.sub(r'[^\x00-\x7f]', '', text)
    
    def stop_download(self, did_stop):
        if did_stop:
            self.log_info('Received Halt')
        self._stop_download = did_stop
    
    def get_number_of_songs(self, csv_file_path):
        # First read the csv and determine the song count for the progress bar
        csv_file   = open(csv_file_path, newline = '')
        # Subtract 1 for the header row
        song_total = len(list(csv.reader(csv_file))) - 1
        self.song_total(song_total)

    def apply_scoring(self, result, band, name, song_length, search):
        score = 0
        title = result['title']
        channel = result['channel']
        duration = result['duration']
        duration_sec = 0
        if ":" in duration:
            if duration.count(":") == 2:
                time_split = duration.split(":")
                hours   = time_split[0]
                minutes = time_split[1]
                seconds = time_split[2]
                int_hours = int(hours) * 60 * 60
                int_sec = int(minutes) * 60
                duration_sec = int_sec + int(seconds) + int_hours
            elif duration.count(":") == 1:
                time_split = duration.split(":")
                minutes = time_split[0]
                seconds = time_split[1]
                int_sec = int(minutes) * 60
                duration_sec = int_sec + int(seconds)
            else:
                self.log_warn("duration is way too long")
        else:
            if duration == "LIVE":
                duration_sec = 0
            else:
                duration_sec = int(duration)

        result['duration'] = duration_sec

        # Band's channels aren't always a good indication of accuracy
        # if self.str_lower_replace(channel) == self.str_lower_replace(band):
        #     score = score + 10

        if "musicvideo" not in self.str_lower_replace(title):
            score = score + 15

        if name not in self.str_lower_replace(title):
            score = score - 30

        print(title)
        print(search)

        title_len = len(title)
        search_len = len(search)
        title_diff = abs(title_len - search_len)
        score = 30 - min(title_diff, 30)

        song_diff = abs(song_length - duration_sec)
        if song_diff <= 1:
            score = score + 20
        if song_diff >= 20:
            score = score - 15

        dict_map = {"score": score, "result": result}
        print(dict_map)

        return dict_map

    def str_lower_replace(self, string):
        string = string.lower()
        string = string.replace(' ', '')
        string = string.replace('_', '')

        return string

    def download_callback(self, total, received, ratio, rate, eta):
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

    def start_download(self, csv_file_path, output_directory, normalize_flag, sleep_time, download_retry):
        self.log_debug("CSV File Path: " + csv_file_path)
        self.log_debug("Output Directory: " + output_directory)
        self.log_debug("Normalize Audio: " + str(normalize_flag))
        self.log_debug("Retry delay: " + str(sleep_time) + " seconds")
        self.log_debug("Download retry: " + str(download_retry))
        
        self._skipped_total = 0
        self._song_download_count = 0
        self._song_failed = 0
        self.get_number_of_songs(csv_file_path)
        
        official_audio = "+official+audio"
        search = ""
        root_dir = output_directory
        if not root_dir:
            self.log_error("output directory is empty")
            return
        
        if not os.path.exists(root_dir):
            self.log_error("directory missing")
        else:
            self.log_debug("directory exists")
            
        # Check for kill signal
        if self._stop_download:
            self.log_debug("Stopped Execution")
            return
            
        csv_file = open(csv_file_path, newline = '')
        csv_reader = csv.reader(csv_file, delimiter = ',')
        row_count = -1
        song_yt_ids = []
        bad_yt_ids = ['JU1BlSgTXxw']
        for row in csv_reader:
            row_count = row_count + 1
            if row_count == 0:
                continue
            self.log_debug(str(row))
            name         = self.string_clean(row[2])
            band         = self.string_clean(row[4])
            album        = self.string_clean(row[3])
            track_number = '' #self.string_clean(row[5])
            genre        = self.string_clean(row[10].split(",")[0])
            duration_ms  = self.string_clean(row[6])
            year         = row[5]

            song_length_seconds = int(duration_ms)/1000

            if "/" in year:
                year = year.split("/")
                year = year[len(year)-1]
            year         = self.string_clean(year)
                
            directory = root_dir + "\\" + band + "\\" + album
        
            # Check for kill signal
            if self._stop_download:
                self.log_debug("Stopped Execution")
                return
        
            if not os.path.exists(directory):
                self.log_debug("Creating new directory: " + directory)
                try:
                    os.makedirs(directory)
                    self.log_debug("Directory created")
                except OSError as err:
                    self.log_error("Directory creation failure: " + err)
            else:
                self.log_debug("Directory exists")
            download_file = directory + "\\" + name
            
            file_found = False
            
            # Check for kill signal
            if self._stop_download:
                self.log_debug("Stopped Execution")
                return
            
            # Check if the file already exists
            for file_name in os.listdir(directory):
                # maybe add the file extension here...
                if fnmatch.fnmatch(file_name, name + ".*"):
                    # TODO could convert old files here...
                    file_found = True
                    break
                
            if file_found:
                self.log_info("File exists, skipping: " + download_file)
                self.skipped_total()
                continue
            
            suffix = ""
            
            # This could be a config option
            use_official_audio = True
            if use_official_audio:
                suffix = official_audio
            
            search = band + " " + name
#             search = band.replace(" ", "+") + "+" + name.replace(" ", "+") + suffix
            self.log_info("Searching for: " + search)
        
            # Check for kill signal
            if self._stop_download:
                self.log_debug("Stopped Execution")
                return

            try:
                search_results = SearchVideos(search, offset=1, mode="json", max_results=20)
            except Exception as err:
                self.log_error("Failed to execute search: " + err)

            # TODO do better search?
#             better_search = VideosSearch(search, limit = 3)
#             
#             loop = asyncio.new_event_loop()
#             asyncio.set_event_loop(loop)
#             better_results = self.async_search(better_search)
#             test = loop.run_until_complete(better_results)
            
#             print(search_results.result())
            
            # get best match
            best_match = None
            print(search_results.result())
            json_results = json.loads(search_results.result())

            scored_results = []
            for result in json_results['search_result']:
                scored_results.append(self.apply_scoring(result, band, name, song_length_seconds, search))
            for scored_result in scored_results:
                if not best_match:
                    best_match = scored_result
                elif best_match['score'] < scored_result['score'] and scored_result['result']['id'] not in bad_yt_ids:
                    best_match = scored_result
            self.log_debug("Score: " + str(best_match['score']))
            best_match = best_match['result']
            expected_duration = best_match['duration']


            self.log_info('Search results: ' + best_match['id'])
#             self.log( 'Search results: ' + better_results['result'] )
            youtube_id = best_match['id']
            youtube_url = best_match['link']
            youtube_title = best_match['title']
            
            if youtube_id in song_yt_ids:
                self.log_error('GOT THE SAME YOUTUBE ID!!! id:' + youtube_id + ' search: ' + search)
                self.song_failed(band + '-' + name)
                continue
            else:
                song_yt_ids.append(youtube_id)

            # Check for kill signal
            if self._stop_download:
                self.log_debug("Stopped Execution")
                return
    
            if youtube_id == '':
                # TODO make the search a retry attempt
                self.log_error('Youtube id was not found for ' + name + ', skipping')
                self.song_failed(band + '-' + name)
                continue
    
            self.log_info(search + " :: youtube title: " + youtube_title + " :: youtube id: " + str(youtube_id) + " url:" + youtube_url)
            retry = 0
            did_download = False
            
            # Sometimes the youtube id might be the same or something goes
            # wrong with the youtube downloader and it sticks with possibly the last
            # song it tried to download, because the metadata would be correct but the
            # actual audio is a completely different song
            
            while (retry < download_retry and not did_download):
                retry = retry + 1
                global total_file_size
                global file_received
                self.log_info("Attempting to download: " + name + " - Attempt #" + str(retry))
                
                download_timer_start = time.time()
                
                video = NULL
                try:
                    video = pafy.new(youtube_url)
                except Exception as err:
                    self.log_error("pafy failed: " + str(err))
                # encoding may fail sometimes with the video title
                if not video:
                    did_download = False
                    self.log_error("pafy encountered unrecoverable error")
                    continue
                if video.title:
                    self.log_info("youtube title: " + video.title)
                else:
                    self.log_warn("youtube title: Warning - There was a problem retrieving the video title")
            
                try:
                    audio_stream = video.getbestaudio("m4a")
                except Exception as err:
                    did_download = False
                    self.log_error("Failed to get audio stream: " + str(err))
                    continue
                download_file_path = download_file + "." + audio_stream.extension

                try:
                    audio_stream.download(download_file_path, quiet=True, callback=self.download_callback )
                except Exception as err:
                    did_download = False
                    self.log_error("Download failed: " + str(err))
                    continue
                self.log_info("Downloaded: " + name)
                # Average file size 1 MB per minute which is 16 KB per second
                kb_per_second = 16
                # file size in bytes multiply by 1000, for a buffer we will divide it by 3
                expected_file_size = (song_length_seconds * kb_per_second * 1000)/3

                if download_file_path.endswith('.m4a'):
                    remove_file = False
                    with audioread.audio_open(download_file_path) as audio_file:
                        downloaded_length = audio_file.duration
                        self.log_debug("Downloaded file length: " + str(downloaded_length))
                        if not (expected_duration + 5 >= downloaded_length >= expected_duration - 5):
                            self.log_error("Downloaded file length is outside expected window. Actual: " + str(downloaded_length) + " Expected: " + str(expected_duration))
                            did_download = False
                            remove_file = True
                    if remove_file:
                        os.remove(download_file_path)
                        continue

                # Throw out files that are less than 1/3 of their expected file size
                if total_file_size < expected_file_size:
                    did_download = False
                    self.log_error(name + " did not finish downloading or file size is too small to be a valid download")
                    self.log_info("file size: " + str(total_file_size))
                    self.log_info("file received: " + str(file_received))
                    self.log_info("Removing file: " + download_file_path)
                    os.remove(download_file_path)
                    self.log_info('Waiting ' + str(sleep_time) + ' seconds before retrying')
                    time.sleep(sleep_time)
                else:
                    download_timer_end = time.time()
                    self.log_info(name + " downloaded successfully")
                    self.calculate_download_average(download_timer_start, download_timer_end)
                    did_download = True
                    total_file_size = 0
                    file_received = 0
                    
            # Check for kill signal
            if self._stop_download:
                self.log_debug("Stopped Execution")
                return
             
            if not did_download:
                # reset the count
                total_file_size = 0
                file_received = 0
                self.log_error("Failed to download: " + name + " after " + str(download_retry) + " attempts")
                self.song_failed(band + '-' + name)
                continue

            self.song_downloaded()
            self.song_progress()
            self.log_info("downloaded file: " + download_file_path)
            
            # Check for kill signal
            if self._stop_download:
                self.log_debug("Stopped Execution")
                return
            
            # audio adjust m4a file
            if normalize_flag:
                normalize_timer_start = time.time()
                self.audio_formatter.normalize_audio(download_file_path, self)
                normalize_timer_end = time.time()
                self.calculate_normalize_average(normalize_timer_start, normalize_timer_end)
            
            # Check for kill signal
            if self._stop_download:
                self.log_debug("Stopped Execution")
                return            
                
            convert_timer_start = time.time()
            mp3_path = self.audio_formatter.convert_to_mp3( directory, name, download_file_path, self)
            # Check for kill signal
            if self._stop_download:
                self.log_debug("Stopped Execution")
                return

            # add meta data
            self.audio_formatter.add_meta_data(mp3_path, name, band, album, year, track_number, genre, self)
            convert_timer_end = time.time()
            self.calculate_convert_average(convert_timer_start, convert_timer_end)
                
            # add meta data
            #self.audio_formatter.add_meta_data(download_file_path, name, band, album, year, track_number, genre, self)
            
            self.log_info("Done")
            self.calc_estimated_time(normalize_flag, True)
        self.log_info("Finished downloading all songs")
        self.log_info("-----End of Log-----")
        return
