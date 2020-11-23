# MusicDownloader
Downloads music from youtube based off an imported csv file. Creates a file directory structure Band > Album > Song based on the specified output directory.
Songs are then converted to MP3s to add meta-data and to normalize the audio. The normalization process forces all songs to play at the same level audio so that some songs aren't louder than others.

An acceptable csv file can be generated here: http://joellehman.com/playlist/index.html

Known issues:
Currently using Pafy to download from youtube. One of the issues is some videos won't fully complete the download and result in a corrupt audio file. The software accounts for this by throwing out unreasonably small file sizes and logs an error into the log which song failed to download. Opened and issue for it here: https://github.com/mps-youtube/pafy/issues/267
