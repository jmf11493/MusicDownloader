# Music Downloader
Downloads music from youtube based off an imported csv file. Creates a file directory structure Band > Album > Song based on the specified output directory.
Songs are then converted to MP3s to add meta-data and to normalize the audio. The normalization process forces all songs to play at the same level audio so that some songs aren't louder than others.

An acceptable csv file can be generated here: http://joellehman.com/playlist/index.html

## Download the installer to give it a try!
The exe can be found here: music_dl/installer/Output/music_downloader_setup.exe

![music downloader screenshot](https://github.com/jmf11493/MusicDownloader/blob/main/screenshots/Music%20Download%20Screenshot.JPG)

## Basic Useage
1. Select desired output directory
2. Select a valid input .csv file
3. Click start download

## Known issues:
Currently using Pafy to download from youtube. One of the issues is some videos won't fully complete the download and result in a corrupt audio file. The software accounts for this by throwing out unreasonably small file sizes and logs an error into the log which song failed to download. Opened and issue for it here: https://github.com/mps-youtube/pafy/issues/267

## To Generate a New .exe and Installer
1. pyinstaller command: pyinstaller main.py -n "Music Downloader" --noconsole -F
Note: Failed to execute script: Delete all build files and re-run the pyinstaller command
2. To create an installer run Inno Setup Script
 
GUI is created using PyQt
To convert the ui file to python use the following command: pyuic my_gui_file.ui -o gui_file.py
