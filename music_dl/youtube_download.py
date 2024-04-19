
from pytube import YouTube

from music_dl.logger import Logger
from music_dl.song import Song


class YoutubeDownload:
    _logger = None

    def __init__(self, logger: Logger):
        self._logger = logger

    def download(self, youtube_url: str, song: Song, directory: str, retries: int):
        audio_to_download = None
        try:
            yt = YouTube(youtube_url)
            audio_streams = yt.streams.filter(only_audio=True, subtype='mp4')
            if not audio_streams:
                self._logger.log_warn("couldn't find mp4 audio")
                return False
            audio_to_download = audio_streams[0]
            for audio in audio_streams:
                if audio.filesize_mb > audio_to_download.filesize_mb:
                    audio_to_download = audio
            audio_title = audio_to_download.title
        except Exception as err:
            self._logger.log_error("failed: " + str(err))
        # encoding may fail sometimes with the video title
        if not audio_to_download:
            self._logger.log_error("couldn't find audio")
            return False
        if audio_title:
            self._logger.log_info("youtube title: " + audio_title)
        else:
            self._logger.log_warn("youtube title: Warning - There was a problem retrieving the video title")

        try:
            download_file_path = audio_to_download.download(directory, song.name, max_retries=retries)
        except Exception as err:
            self._logger.log_error("Download failed: " + str(err))
            return False
        return download_file_path
        self._logger.log_info("Downloaded: " + song.name)
