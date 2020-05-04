import queue
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import scrolledtext as tkst
from tkinter import messagebox as msg
from tkinter import Menu
import timetable as tt
import timetable_business_logic as tbl
import choi_confighandler as ccfg
import choi_logger as clog
import logging
from datetime import datetime, timedelta

wx = 50
wy = 10
padx = 5
pady = 5

run_button_color = "#00B32C"
exit_button_color = "#DC3D2A"
path_button_color = "#6b7a8f"


class MasterWindow(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.title("TV프로그램 스케줄 다운로드 프로그램")
        self.resizable(False, False)
        self.geometry("+100+100")
        self.iconbitmap("img/tvtable.ico")

        self.logger = clog.ChoiLogger(log_level=logging.DEBUG).log()
        self.conf = ccfg.TimeTableConfig()
        self.msg_queue = queue.Queue()
        self.log_scrt = None
        self.progress_bar = None
        self.output_directory = tk.StringVar()
        self.date_value = tk.StringVar()
        self.bl = tbl.BusinessLogic(self)
        self.date_entry = None
        self.path_entry = None

        self.create_widget()
        self.date_entry.configure(fg='gray')

        self.bl.init_config(self.conf)
        if self.output_directory.get() == "":
            msg.showerror("바로가기 설정", "엑셀파일을 저장할 폴더 경로가 설정되어있지 않습니다.\n" +
                          "지금 파일을 저장할 폴더 경로를 설정하세요.\n(처음 1회만 필요)")
            self.bl.set_output_dir()

        self.bind('<F2>', lambda event: self.bl.f2_callback())
        self.bind('<F4>', lambda event: self.bl.f4_callback())
        self.bind('<Return>', lambda event: self.bl.enter_callback())

        self.protocol("WM_DELETE_WINDOW", lambda: self.bl.on_closing())
        self.bl.start_record_log()

    def create_widget(self):
        config_frame = tk.Frame(self)
        config_frame.grid(row=0, column=0, padx=padx, pady=(pady, pady/2), columnspan=3, rowspan=2, sticky='nesw')

        date_label = tk.Label(config_frame, text="목표 날짜")
        date_label.grid(row=0, column=0, padx=(padx, padx/2), pady=pady, sticky='nesw')

        self.date_entry = tk.Entry(config_frame, textvariable=self.date_value, width=30)
        self.date_entry.grid(row=0, column=1, padx=padx/2, pady=pady, sticky='nesw')
        self.date_entry.insert(0, "YYYY-MM-DD 형식")
        self.date_entry.bind("<FocusIn>", self.bl.date_callback)
        # date_entry.config(text=datetime.strftime(datetime.today() + timedelta(days=1), "%Y-%m-%d"))

        date_btn = tk.Button(config_frame, text="내일날짜", bg=path_button_color, fg='white',
                             activebackground=path_button_color, command=(lambda: self.bl.set_next_day()))
        date_btn.grid(row=0, column=2, padx=(padx/2, padx), pady=pady, sticky='nesw')

        path_label = tk.Label(config_frame, text="저장 경로")
        path_label.grid(row=1, column=0, padx=(padx, padx/2), pady=pady, sticky='nesw')

        self.path_entry = tk.Entry(config_frame, textvariable=self.output_directory, width=30)
        self.path_entry.grid(row=1, column=1, padx=padx/2, pady=pady, sticky='nesw')

        path_btn = tk.Button(config_frame, text="저장경로 설정", bg=path_button_color, fg='white',
                             activebackground=path_button_color, command=(lambda: self.bl.set_output_dir()))
        path_btn.grid(row=1, column=2, padx=(padx/2, padx), pady=pady, sticky='nesw')

        button_frame = tk.Frame(self)
        button_frame.grid(row=2, column=0, padx=padx, pady=pady/2, columnspan=3, sticky='nesw')
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)

        scrap_btn = tk.Button(button_frame, text="실행 (F2 or 엔터키)", bg=run_button_color,
                              activebackground=run_button_color)
        scrap_btn.configure(command=(lambda: self.bl.start_tv_schedule_thread()))
        scrap_btn.grid(row=0, column=0, sticky='nesw', padx=padx/2)

        exit_btn = tk.Button(button_frame, text="     종료 (F4)    ", bg=exit_button_color,
                             activebackground=exit_button_color)
        exit_btn.configure(command=(lambda: self.bl.on_closing()))
        exit_btn.grid(row=0, column=1, sticky='nesw', padx=padx/2)

        log_frame = tk.Frame(self)
        log_frame.grid(row=3, column=0, padx=padx, pady=pady/2, columnspan=3, rowspan=4, sticky='nesw')

        self.log_scrt = tkst.ScrolledText(log_frame, width=wx, height=wy, wrap=tk.WORD)
        self.log_scrt.pack(fill="both", expand=True)

        self.log_scrt.tag_config("error", foreground='red', font=('Malgun Gothic', 10, 'normal'))
        self.log_scrt.tag_config("ok", foreground='blue', font=('Malgun Gothic', 10, 'normal'))
        self.log_scrt.tag_config("info", foreground='gray', font=('Malgun Gothic', 10, 'normal'))
        self.log_scrt.insert(tk.INSERT, "이 곳에 매크로 진행상황이 나타납니다\n")

        progress_bar_frame = tk.Frame(self)
        progress_bar_frame.grid(row=7, column=0, padx=padx, pady=(pady/2, pady), columnspan=3, sticky='nesw')

        self.progress_bar = ttk.Progressbar(progress_bar_frame, mode="indeterminate", orient=tk.HORIZONTAL)
        self.progress_bar.pack(fill="both", expand=True)


if __name__ == "__main__":
    master = MasterWindow()
    master.mainloop()
