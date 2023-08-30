import json

from youtubesearchpython import SearchVideos
from music_dl.logger import Logger
from music_dl.song import Song


class YoutubeSearch:
    _logger = None

    def __init__(self, logger: Logger):
        self._logger = logger

    def search(self, song: Song):
        search_str = song.band + " " + song.name
        self._logger.log_info("Searching for: " + search_str)
        try:
            # TODO don't use legacy search anymore?
            search_results = SearchVideos(search_str, offset=1, mode="json", max_results=20)
        except Exception as err:
            self._logger.log_error("Failed to execute search: " + err)

        json_results = json.loads(search_results.result())

        scored_results = []
        for result in json_results['search_result']:
            scored_results.append(self._apply_scoring(result, song, search_str))

        best_match = self._get_best_match(scored_results)
        best_match['search'] = search_str

        return best_match

    def _apply_scoring(self, result, song, search):
        score = 0
        title = result['title']
        channel = result['channel']
        duration = result['duration']
        song_length = song.duration_seconds
        duration_sec = 0

        if ":" in duration:
            if duration.count(":") == 2:
                # shouldn't be downloading songs over 1 hour long
                # this will cause memory errors
                score = score - 5000
            elif duration.count(":") == 1:
                time_split = duration.split(":")
                minutes = time_split[0]
                seconds = time_split[1]
                int_sec = int(minutes) * 60
                duration_sec = int_sec + int(seconds)
            else:
                score = score - 5000
                self._logger.log_warn("duration is way too long")
        else:
            if duration == "LIVE":
                duration_sec = 0
            else:
                duration_sec = int(duration)

        result['duration'] = duration_sec

        clean_title = self.str_lower_replace(title)

        if song_length + 10 > duration_sec > song_length - 10:
            score = score + 5
            if song_length + 5 > duration_sec > song_length - 5:
                score = score + 5
                if song_length + 2 > duration_sec > song_length - 2:
                    score = score + 10

        if "musicvideo" not in clean_title:
            score = score + 15

        if self.str_lower_replace(song.name) not in clean_title:
            score = score - 3000

        dict_map = {"score": score, "result": result}

        return dict_map

    def str_lower_replace(self, string):
        string = string.lower()
        string = string.replace(' ', '')
        string = string.replace('_', '')

        return string

    def _get_best_match(self, scored_results):
        best_match = None

        for scored_result in scored_results:
            if not best_match:
                best_match = scored_result
            elif best_match['score'] < scored_result['score']:
                best_match = scored_result
        self._logger.log_debug("Score: " + str(best_match['score']))
        self._logger.log_debug("Match: " + str(best_match))

        return best_match['result']
