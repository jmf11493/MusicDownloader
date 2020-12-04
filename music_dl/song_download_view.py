'''
Created on Aug 5, 2020

@author: Jeff
'''
import PyQt5
from PyQt5 import QtCore, QtGui, QtWidgets
import datetime
import pyperclip

#Fixes scaling issues on high res monitors
if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
    PyQt5.QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
    PyQt5.QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

class SongDownloadView(object):
    '''
    classdocs
    '''

    def __init__(self, model, controller, MainWindow):
        self._model = model
        self._controller = controller
        self.setupUi(MainWindow)
        
        self._log           = '-----Start of Log-----\n'
        self._song_fail_log = ''
        
        self._model.song_total_change.connect(self.on_song_total_change)
        self._model.skipped_total_change.connect(self.on_skipped_total_change)
        self._model.song_download_change.connect(self.on_song_download_change)
        self._model.song_failed_change.connect(self.on_song_failed_change)
        self._model.song_progress_change.connect(self.on_update_progress)
        self._model.estimate_change.connect(self.on_estimate_update_change)
        self._model.log_change.connect(self.on_log_update)
        self._model.song_failed_name.connect(self.on_song_failed_update)
        self.start_download_button.clicked.connect(self.start_download_listener)
        
        self.normalize_audio.stateChanged.connect(self._controller.normalize_change)
        self.convert_mp3.stateChanged.connect(self._controller.convert_change)
        self.browse_csv_button.clicked.connect(self.get_csv_path)
        self.browse_output_button.clicked.connect(self.get_output_path)
        self.csv_file_location.textChanged.connect(self._controller.csv_file_change)
        self.output_file_location.textChanged.connect(self._controller.output_dir_change)
        
        self.download_retry_spinbox.valueChanged.connect(self._controller.download_try_change)
        self.retry_wait_time_spinbox.valueChanged.connect(self._controller.time_sleep_change)
        
        self.stop_download_button.clicked.connect(self.stop_download_listener)
        
        self.copy_log_button.clicked.connect(self.copy_log_listener)
        
        
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(758, 500)
        MainWindow.setMinimumSize(QtCore.QSize(758, 500))
        MainWindow.setMaximumSize(QtCore.QSize(758, 500))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayoutWidget_4 = QtWidgets.QWidget(self.centralwidget)
        self.gridLayoutWidget_4.setGeometry(QtCore.QRect(10, 10, 735, 421))
        self.gridLayoutWidget_4.setObjectName("gridLayoutWidget_4")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.gridLayoutWidget_4)
        self.gridLayout_4.setContentsMargins(5, 0, 5, 0)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.start_download_button = QtWidgets.QPushButton(self.gridLayoutWidget_4)
        self.start_download_button.setMaximumSize(QtCore.QSize(100, 16777215))
        self.start_download_button.setObjectName("start_download_button")
        self.gridLayout_4.addWidget(self.start_download_button, 4, 0, 1, 1)
        self.log_output = QtWidgets.QPlainTextEdit(self.gridLayoutWidget_4)
        self.log_output.setEnabled(True)
        self.log_output.setReadOnly(True)
        self.log_output.setObjectName("log_output")
        self.gridLayout_4.addWidget(self.log_output, 12, 0, 1, 3)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setContentsMargins(5, -1, 5, -1)
        self.gridLayout.setObjectName("gridLayout")
        self.skipped_songs_count = QtWidgets.QLCDNumber(self.gridLayoutWidget_4)
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Light, brush)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Midlight, brush)
        self.skipped_songs_count.setPalette(palette)
        self.skipped_songs_count.setEnabled(True)
        self.skipped_songs_count.setObjectName("skipped_songs_count")
        self.gridLayout.addWidget(self.skipped_songs_count, 2, 1, 1, 1)
        self.total_songs_count = QtWidgets.QLCDNumber(self.gridLayoutWidget_4)
        self.total_songs_count.setPalette(palette)
        self.total_songs_count.setObjectName("total_songs_count")
        self.gridLayout.addWidget(self.total_songs_count, 5, 1, 1, 1)
        self.total_songs_label = QtWidgets.QLabel(self.gridLayoutWidget_4)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.total_songs_label.setFont(font)
        self.total_songs_label.setObjectName("total_songs_label")
        self.gridLayout.addWidget(self.total_songs_label, 5, 0, 1, 1)
        self.downloaded_songs_count = QtWidgets.QLCDNumber(self.gridLayoutWidget_4)
        self.downloaded_songs_count.setPalette(palette)
        self.downloaded_songs_count.setObjectName("downloaded_songs_count")
        self.gridLayout.addWidget(self.downloaded_songs_count, 1, 1, 1, 1)
        self.downloaded_songs_label = QtWidgets.QLabel(self.gridLayoutWidget_4)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.downloaded_songs_label.setFont(font)
        self.downloaded_songs_label.setObjectName("downloaded_songs_label")
        self.gridLayout.addWidget(self.downloaded_songs_label, 1, 0, 1, 1)
        self.song_progress_bar = QtWidgets.QProgressBar(self.gridLayoutWidget_4)
        self.song_progress_bar.setProperty("value", 0)
        self.song_progress_bar.setObjectName("song_progress_bar")
        self.gridLayout.addWidget(self.song_progress_bar, 6, 0, 1, 2)
        self.skipped_songs_label = QtWidgets.QLabel(self.gridLayoutWidget_4)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.skipped_songs_label.setFont(font)
        self.skipped_songs_label.setObjectName("skipped_songs_label")
        self.gridLayout.addWidget(self.skipped_songs_label, 2, 0, 1, 1)
        self.progress_label = QtWidgets.QLabel(self.gridLayoutWidget_4)
        font = QtGui.QFont()
        font.setPointSize(18)
        self.progress_label.setFont(font)
        self.progress_label.setAlignment(QtCore.Qt.AlignCenter)
        self.progress_label.setObjectName("progress_label")
        self.gridLayout.addWidget(self.progress_label, 0, 0, 1, 2)
        self.failed_songs_count_label = QtWidgets.QLabel(self.gridLayoutWidget_4)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.failed_songs_count_label.setFont(font)
        self.failed_songs_count_label.setObjectName("failed_songs_count_label")
        self.gridLayout.addWidget(self.failed_songs_count_label, 3, 0, 1, 1)
        self.failed_songs_count = QtWidgets.QLCDNumber(self.gridLayoutWidget_4)
        self.failed_songs_count.setPalette(palette)
        self.failed_songs_count.setEnabled(True)
        self.failed_songs_count.setObjectName("failed_songs_count")
        self.gridLayout.addWidget(self.failed_songs_count, 3, 1, 1, 1)
        self.gridLayout_4.addLayout(self.gridLayout, 0, 4, 4, 1)
        self.time_remaining_label = QtWidgets.QLabel(self.gridLayoutWidget_4)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.time_remaining_label.setFont(font)
        self.time_remaining_label.setObjectName("time_remaining_label")
        self.gridLayout_4.addWidget(self.time_remaining_label, 4, 4, 1, 1)
        self.failed_songs_label = QtWidgets.QLabel(self.gridLayoutWidget_4)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.failed_songs_label.setFont(font)
        self.failed_songs_label.setObjectName("failed_songs_label")
        self.gridLayout_4.addWidget(self.failed_songs_label, 11, 3, 1, 2)
        self.log_label = QtWidgets.QLabel(self.gridLayoutWidget_4)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.log_label.setFont(font)
        self.log_label.setObjectName("log_label")
        self.gridLayout_4.addWidget(self.log_label, 11, 0, 1, 2)
        self.stop_download_button = QtWidgets.QPushButton(self.gridLayoutWidget_4)
        self.stop_download_button.setEnabled(False)
        self.stop_download_button.setMaximumSize(QtCore.QSize(100, 16777215))
        self.stop_download_button.setAutoFillBackground(False)
        self.stop_download_button.setObjectName("stop_download_button")
        self.gridLayout_4.addWidget(self.stop_download_button, 4, 2, 1, 1)
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setContentsMargins(5, -1, -1, -1)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.browse_output_button = QtWidgets.QPushButton(self.gridLayoutWidget_4)
        self.browse_output_button.setMaximumSize(QtCore.QSize(150, 16777215))
        self.browse_output_button.setObjectName("browse_output_button")
        self.gridLayout_2.addWidget(self.browse_output_button, 1, 1, 1, 1)
        self.setup_label = QtWidgets.QLabel(self.gridLayoutWidget_4)
        font = QtGui.QFont()
        font.setPointSize(18)
        self.setup_label.setFont(font)
        self.setup_label.setAlignment(QtCore.Qt.AlignCenter)
        self.setup_label.setObjectName("setup_label")
        self.gridLayout_2.addWidget(self.setup_label, 0, 1, 1, 2)
        self.browse_csv_button = QtWidgets.QPushButton(self.gridLayoutWidget_4)
        self.browse_csv_button.setMaximumSize(QtCore.QSize(150, 16777215))
        self.browse_csv_button.setObjectName("browse_csv_button")
        self.gridLayout_2.addWidget(self.browse_csv_button, 2, 1, 1, 1)
        self.output_file_location = QtWidgets.QLineEdit(self.gridLayoutWidget_4)
        self.output_file_location.setReadOnly(True)
        self.output_file_location.setObjectName("output_file_location")
        self.gridLayout_2.addWidget(self.output_file_location, 1, 2, 1, 1)
        self.csv_file_location = QtWidgets.QLineEdit(self.gridLayoutWidget_4)
        self.csv_file_location.setReadOnly(True)
        self.csv_file_location.setObjectName("csv_file_location")
        self.gridLayout_2.addWidget(self.csv_file_location, 2, 2, 1, 1)
        self.gridLayout_3 = QtWidgets.QGridLayout()
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.download_retry_spinbox = QtWidgets.QSpinBox(self.gridLayoutWidget_4)
        self.download_retry_spinbox.setMinimum(1)
        self.download_retry_spinbox.setProperty("value", 5)
        self.download_retry_spinbox.setObjectName("download_retry_spinbox")
        self.gridLayout_3.addWidget(self.download_retry_spinbox, 2, 4, 1, 1)
        self.download_retry_label = QtWidgets.QLabel(self.gridLayoutWidget_4)
        self.download_retry_label.setToolTip("")
        self.download_retry_label.setObjectName("download_retry_label")
        self.gridLayout_3.addWidget(self.download_retry_label, 2, 3, 1, 1)
        self.configuration_label = QtWidgets.QLabel(self.gridLayoutWidget_4)
        font = QtGui.QFont()
        font.setPointSize(18)
        self.configuration_label.setFont(font)
        self.configuration_label.setAlignment(QtCore.Qt.AlignCenter)
        self.configuration_label.setObjectName("configuration_label")
        self.gridLayout_3.addWidget(self.configuration_label, 0, 1, 1, 4)
        self.retry_wait_time_spinbox = QtWidgets.QSpinBox(self.gridLayoutWidget_4)
        self.retry_wait_time_spinbox.setMinimum(2)
        self.retry_wait_time_spinbox.setObjectName("retry_wait_time_spinbox")
        self.gridLayout_3.addWidget(self.retry_wait_time_spinbox, 2, 2, 1, 1)
        self.retry_wait_time_label = QtWidgets.QLabel(self.gridLayoutWidget_4)
        self.retry_wait_time_label.setToolTip("")
        self.retry_wait_time_label.setObjectName("retry_wait_time_label")
        self.gridLayout_3.addWidget(self.retry_wait_time_label, 2, 1, 1, 1)
        self.normalize_audio = QtWidgets.QCheckBox(self.gridLayoutWidget_4)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.normalize_audio.setFont(font)
        self.normalize_audio.setChecked(True)
        self.normalize_audio.setObjectName("normalize_audio")
        self.gridLayout_3.addWidget(self.normalize_audio, 1, 1, 1, 1)
        self.convert_mp3 = QtWidgets.QCheckBox(self.gridLayoutWidget_4)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.convert_mp3.setFont(font)
        self.convert_mp3.setChecked(True)
        self.convert_mp3.setObjectName("convert_mp3")
        self.gridLayout_3.addWidget(self.convert_mp3, 1, 2, 1, 3)
        self.gridLayout_2.addLayout(self.gridLayout_3, 3, 1, 1, 2)
        self.gridLayout_4.addLayout(self.gridLayout_2, 0, 0, 1, 4)
        self.failed_songs_log = QtWidgets.QPlainTextEdit(self.gridLayoutWidget_4)
        self.failed_songs_log.setEnabled(True)
        self.failed_songs_log.setReadOnly(True)
        self.failed_songs_log.setObjectName("failed_songs_log")
        self.gridLayout_4.addWidget(self.failed_songs_log, 12, 3, 1, 2)
        self.copy_log_button = QtWidgets.QPushButton(self.gridLayoutWidget_4)
        self.copy_log_button.setObjectName("copy_log_button")
        self.gridLayout_4.addWidget(self.copy_log_button, 11, 2, 1, 1)
        self.version_label = QtWidgets.QLabel(self.centralwidget)
        self.version_label.setGeometry(QtCore.QRect(330, 460, 81, 16))
        self.version_label.setObjectName("version_label")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Music Downloader"))
        self.start_download_button.setText(_translate("MainWindow", "Start Download"))
        self.total_songs_label.setText(_translate("MainWindow", "Total Songs:"))
        self.downloaded_songs_label.setText(_translate("MainWindow", "Songs Downloaded:"))
        self.skipped_songs_label.setText(_translate("MainWindow", "Songs Skipped:"))
        self.progress_label.setText(_translate("MainWindow", "Progress"))
        self.failed_songs_count_label.setText(_translate("MainWindow", "Songs Failed:"))
        self.time_remaining_label.setText(_translate("MainWindow", "Estimated Time Remaining: "))
        self.failed_songs_label.setText(_translate("MainWindow", "Failed Songs:"))
        self.log_label.setText(_translate("MainWindow", "Log:"))
        self.stop_download_button.setText(_translate("MainWindow", "Stop Download"))
        self.browse_output_button.setText(_translate("MainWindow", "Select Output Directory"))
        self.setup_label.setText(_translate("MainWindow", "Setup"))
        self.browse_csv_button.setText(_translate("MainWindow", "Select CSV File"))
        self.download_retry_label.setText(_translate("MainWindow", "Download Attempts"))
        self.configuration_label.setText(_translate("MainWindow", "Configuration"))
        self.retry_wait_time_label.setText(_translate("MainWindow", "Time to Wait Between Tries"))
        self.normalize_audio.setText(_translate("MainWindow", "Normalize Audio"))
        self.convert_mp3.setText(_translate("MainWindow", "Convert To MP3 and Add Metadata"))
        self.copy_log_button.setText(_translate("MainWindow", "Copy Log to Clipboard"))
        self.version_label.setText(_translate("MainWindow", "Version 1.0.0"))
        
    def on_song_total_change(self, value):
        self.total_songs_count.display(value)
    
    def on_skipped_total_change(self, value):
        self.skipped_songs_count.display(value)
        
    def on_song_download_change(self, value):
        self.downloaded_songs_count.display(value)
        
    def on_song_failed_change(self, value):
        self.failed_songs_count.display(value)

    def on_update_progress(self, value):
        self.song_progress_bar.setValue(value)
        
    def on_estimate_update_change(self, value):
        self.time_remaining_label.setText('Estimated Time Remaining: ' + value)
    
    def on_log_update(self, value):
        now = datetime.datetime.now()
        date = str(now.year) + '-' + str(now.month) + '-' + str(now.day) + ' '+ str(now.hour) + ':' + str(now.minute) + ':' + str(now.second)
        self._log = self._log +'['+ date +']'+ value + '\n'
        self.log_output.setPlainText(self._log)
        self.log_output.verticalScrollBar().setValue(self.log_output.verticalScrollBar().maximum())
        
    def on_song_failed_update(self, value):
        self._song_fail_log = self._song_fail_log + value + '\n'
        self.failed_songs_log.setPlainText(self._song_fail_log)
        self.failed_songs_log.verticalScrollBar().setValue(self.failed_songs_log.verticalScrollBar().maximum())
        
    def get_csv_path(self):
        file = QtWidgets.QFileDialog().getOpenFileName(None, 'Select CSV', '', '*.csv')
        file_path = file[0]
        file_path = file_path.replace('/', '\\' )
        self.csv_file_location.setText(file_path)

    def get_output_path(self):
        file_path = QtWidgets.QFileDialog().getExistingDirectory()
        file_path = file_path.replace('/', '\\' )
        self.output_file_location.setText(file_path)
    
    def start_download_listener(self):
        self.start_download_button.setDisabled(True)
        self.stop_download_button.setDisabled(False)
        self._controller.start_download_click()
        
    def stop_download_listener(self):
        self.start_download_button.setDisabled(False)
        self.stop_download_button.setDisabled(True)
        self._controller.stop_download_click()
        
    def copy_log_listener(self):
        copy_value = self.log_output.toPlainText()
        pyperclip.copy(copy_value)