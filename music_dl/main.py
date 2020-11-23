'''
Created on Aug 5, 2020

@author: Jeff
'''

from PyQt5 import QtWidgets
import sys
from music_dl.audio_formatter import AudioFormatter
from music_dl.song_download_controller import  SongDownloadController
from music_dl.song_download_model import SongDownloadModel
from music_dl.song_download_view import SongDownloadView 

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    audio_formatter = AudioFormatter()
    model = SongDownloadModel(audio_formatter)
    controller = SongDownloadController(model)
    
    ui = SongDownloadView(model, controller, MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())