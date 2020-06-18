"""
log recorder made by Hyungsuk Choi (choihyungsuk@gmail.com)
디버그를 위해 로그를 기록하는
범용 로그파일입니다.
"""

import logging
from logging.handlers import RotatingFileHandler


class ChoiLogger:
    def __init__(self, log_level):
        self.mylogger = logging.getLogger(__name__)
        self.log_level = log_level
        if len(self.mylogger.handlers) > 0:
            pass

        else:
            self.mylogger.setLevel(log_level)
            self.myformatter = logging.Formatter("%(asctime)s (%(module)s) [%(levelname)s] %(message)s")
            self.file_handler = RotatingFileHandler('tmp.log', maxBytes=4096, backupCount=1)
            self.file_handler.setFormatter(self.myformatter)

            self.stream_handler = logging.StreamHandler()
            self.stream_handler.setFormatter(self.myformatter)

            self.mylogger.addHandler(self.file_handler)
            self.mylogger.addHandler(self.stream_handler)

    def log(self):
        return self.mylogger
