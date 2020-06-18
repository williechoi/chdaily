import os, errno
import sys
import queue
import threading
import tkinter as tk
import timetable as tt
import choi_confighandler as ccfg
from datetime import datetime, timedelta
from tkinter import filedialog

date_default_val = "YYYY-MM-DD 형식"


def _validate_date_format(date_string):
    try:
        if not isinstance(date_string, str) or not date_string:
            return False
        datetime.strptime(date_string, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def _validate_path_format(path_string):
    try:
        if not isinstance(path_string, str) or not path_string:
            return False

        _, pathname = os.path.splitdrive(path_string)

        root_dirname = os.environ.get('HOMEDRIVE', 'C:') if sys.platform == 'win32' else os.path.sep
        assert os.path.isdir(root_dirname)

        root_dirname = root_dirname.rstrip(os.path.sep) + os.path.sep
        for pathname_part in pathname.split(os.path.sep):
            try:
                os.lstat(root_dirname + pathname_part)

            except OSError as exc:
                if hasattr(exc, 'winerror'):
                    if exc.winerror == 123:
                        return False
                elif exc.errno in {errno.ENAMETOOLONG, errno.ERANGE}:
                    return False

    except TypeError as exc:
        return False

    else:
        return True


class BusinessLogic:
    def __init__(self, master):
        self.master = master
        self.msg_queue = master.msg_queue
        self.logger = master.logger

        self.get_tv_schedule_queue = queue.Queue()
        self.get_tv_schedule_thread = None
        self.export_to_csv_thread = None
        self.record_log_thread = None

    def start_tv_schedule_thread(self):
        date_str = self.master.date_value.get()
        path_str = self.master.output_directory.get()
        if not _validate_date_format(date_str):
            self.msg_queue.put(("날짜를 올바른 형태(YYYY-mm-dd)로 입력하세요 (예: 2020-01-01)", "error"))
            return False

        if not _validate_path_format(path_str):
            self.msg_queue.put(("올바른 경로를 입력하세요", "error"))
            return False

        self.logger.debug("start fetching tv schedule from five Christian TV broadcastors")
        self.msg_queue.put("다섯 개의 기독교 방송국에서 TV스케줄을 가져옵니다")
        self.get_tv_schedule_thread = threading.Thread(target=tt.main, args=(self.master.date_value.get(),
                                                                             self.get_tv_schedule_queue))
        self.get_tv_schedule_thread.start()
        self.master.progress_bar.start()
        self.master.after(100, self.check_tv_schedule_thread)

    def check_tv_schedule_thread(self):
        if self.get_tv_schedule_thread.is_alive():
            self.master.after(100, self.check_tv_schedule_thread)
        else:
            self.exporting_to_csv(self.get_tv_schedule_queue.get())

    def exporting_to_csv(self, data):
        if data is None:
            self.logger.debug("no data to be uploaded")
            self.msg_queue.put(("업로드할 데이터가 없습니다", "error"))

        else:
            self.logger.debug("start exporting data to csv file")
            self.msg_queue.put("수집한 정보를 csv파일로 export합니다")
            self.export_to_csv_thread = threading.Thread(target=tt.export_tvtable,
                                                         args=(data[0], data[1], self.master.date_value.get(),
                                                               self.master.output_directory.get()))
            self.export_to_csv_thread.start()
            self.master.after(100, self.check_export_to_csv_thread)

    def check_export_to_csv_thread(self):
        if self.export_to_csv_thread.is_alive():
            self.master.after(100, self.check_export_to_csv_thread)
        else:
            self.master.progress_bar.stop()
            self.msg_queue.put((f"결과파일을 {self.master.output_directory.get()}로 내보냈습니다", "ok"))
            self.logger.debug(f"output file has been exported to {self.master.output_directory.get()}")

    # 로그처리 스레드 수행
    def start_record_log(self):
        self.logger.debug("start checking log")
        self.record_log_thread = threading.Thread(target=self.check_msg_queue)
        self.record_log_thread.daemon = True
        self.record_log_thread.start()

    # 로그메시지 0.1초에 한번씩 확인하여 로그메시지 있을 경우 처리하는 메서드 수행
    def check_msg_queue(self):
        while True:
            try:
                log_msg = self.msg_queue.get()
            except queue.Empty:
                break
            else:
                self.process_log(log_msg)

        self.master.after(100, self.check_msg_queue)

    # 로그메시지 처리하여 로그창에 보여줌
    def process_log(self, log_msg):
        if isinstance(log_msg, tuple) or isinstance(log_msg, list):
            txt, flag = log_msg[0], log_msg[1]
        else:
            txt, flag = str(log_msg), "info"

        self.master.log_scrt.insert(tk.INSERT, txt + '\n', flag)
        self.master.log_scrt.see(tk.END)

    def set_next_day(self):
        self.msg_queue.put("내일날짜로 설정합니다")
        self.logger.debug("set the date variable to tomorrow")
        self.master.date_value.set(datetime.strftime(datetime.today() + timedelta(days=1), "%Y-%m-%d"))
        self.master.date_entry.configure(fg='black')

    def on_closing(self):
        self.save_config(self.master.conf)
        self.master.quit()
        exit(0)

    def date_callback(self, event):
        event.widget.configure(fg='black')
        # self.master.date_entry.configure(fg='black')
        if self.master.date_value.get() == date_default_val:
            self.master.date_value.set("")
        else:
            event.widget.select_range(0, 'end')
            event.widget.icursor('end')
            # self.master.date_entry.select_range(0, 'end')
            # self.master.date_entry.icursor('end')

    def set_output_dir(self):
        old_output_dir = self.master.output_directory.get()
        self.msg_queue.put(f"현재 저장경로 설정: {old_output_dir}")
        self.logger.debug(f"current output path is set to {old_output_dir}")

        desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
        new_shortcut_dir = filedialog.askdirectory(initialdir=desktop)
        if new_shortcut_dir != '':
            self.master.output_directory.set(new_shortcut_dir)
            self.msg_queue.put(f"저장경로가 {new_shortcut_dir}로 설정되었습니다")
            self.logger.debug(f"output path has been changed to {new_shortcut_dir}")

    def f2_callback(self):
        self.start_tv_schedule_thread()

    def f4_callback(self):
        self.on_closing()

    def enter_callback(self):
        self.start_tv_schedule_thread()

    def init_config(self, cfg_obj):
        config_dict = cfg_obj.load_conf()

        try:
            self.logger.debug(f"output directory var: {config_dict['output_dir']}")
            self.master.output_directory.set(config_dict['output_dir'])
        except KeyError as e:
            self.logger.debug(f"error occurred while initializing the output var: {e}")
            self.master.output_directory.set("")

    def save_config(self, cfg_obj):
        config_dict = dict()
        config_dict["output_dir"] = self.master.output_directory.get()

        if cfg_obj.update_conf(config_dict):
            self.logger.debug("configuration file saved.")
        else:
            self.logger.debug("failed to save configuration file.")

