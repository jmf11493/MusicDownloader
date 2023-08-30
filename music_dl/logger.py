from PyQt5.QtCore import pyqtSignal


class Logger:

    _log_field = None

    def __init__(self, log_field: pyqtSignal):
        self._log_field = log_field
        self._debug_log = False

    def log_debug(self, message):
        message = "DEBUG: " + message
        print(message)
        if self._debug_log:
            self.log(message)

    def log_warn(self, message):
        message = "WARN: " + message
        print(message)
        self.log(message)

    def log_error(self, message):
        message = "ERROR: " + message
        print(message)
        self.log(message)

    def log_info(self, message):
        message = "INFO: " + message
        print(message)
        self.log(message)

    def log(self, message):
        self._log_field.emit(message)
