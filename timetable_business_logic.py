import queue
import threading
import tkinter as tk
import timetable as tt
import choi_confighandler as ccfg


class BusinessLogic:
    def __init__(self, master):
        self.master = master
        self.msg_queue = master.msg_queue
        self.logger = master.logger

        self.get_tv_schedule_queue = queue.Queue()
        self.get_tv_schedule_thread = None
        self.record_log_thread = None

    def start_tv_schedule_thread(self):
        self.logger.debug("start fetching tv schedule from five Christian TV broadcastors")
        self.msg_queue.put("다섯 개의 기독교 방송국에서 TV스케줄을 가져옵니다")
        self.get_tv_schedule_thread = threading.Thread(target=tt.main, args=())
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
            pass

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

        self.master.log_scrt.insert("tk.INSERT", txt + '\n', flag)
        self.master.log_scrt.see(tk.END)

    def on_closing(self):
        self.master.quit()
        exit(0)
