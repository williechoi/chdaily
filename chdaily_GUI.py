import tkinter as tk
import tkinter.font as font
from datetime import datetime
from tkinter import messagebox
from urllib.parse import urlparse
import logging

from dateutil.parser import parse

import chdaily_basic as cb
import sermon as sm
import timetable as tb

MAIN_HEIGHT = 400
MAIN_WIDTH = 900

SUB_HEIGHT = 200
SUB_WIDTH = 400

SUB2_HEIGHT = 250
SUB2_WIDTH = 700

VALID_URLS = ["www.christiandaily.co.kr", "kr.christianitydaily.com", "www.newsis.com"]

mylogger = logging.getLogger(__name__)
mylogger.setLevel(logging.INFO)

myformatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')

file_handler = logging.FileHandler('tmp.log')
file_handler.setFormatter(myformatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(myformatter)

mylogger.addHandler(file_handler)
mylogger.addHandler(stream_handler)


def is_valid(url):
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)


def open_TVtable():
    frm_width = 0.92
    frm_height = 0.44
    lbl_width = 0.05
    lbl_height = 0.2
    cbx_width = 0.33
    cbx_height = 0.15
    entry_width = 0.2
    entry_height = 0.2

    is_cgntv = tk.IntVar()
    is_ctstv = tk.IntVar()
    is_cbstv = tk.IntVar()
    is_goodtv = tk.IntVar()
    is_cchannel = tk.IntVar()

    is_cgntv.set(1)
    is_ctstv.set(1)
    is_cbstv.set(1)
    is_goodtv.set(1)
    is_cchannel.set(1)

    tvtable_window = tk.Toplevel()
    tvtable_window.title("기독교방송국 TV스케줄표 다운받기")
    tvtable_window.iconbitmap('favicon.ico')
    tvtable_canvas = tk.Canvas(tvtable_window, height=200, width=400)
    tvtable_canvas.pack()
    myfont = font.Font(family="맑은 고딕", size=10)

    tv_upper_frame = tk.Frame(tvtable_window)
    tv_upper_frame.place(relx=0.04, rely=0.04, relwidth=frm_width, relheight=frm_height)

    tvdate_label = tk.Label(tv_upper_frame, text="날짜를 입력하세요:", anchor='sw')
    tvdate_label.place(relx=0.04, rely=0.1, relwidth=0.45, relheight=0.2)

    yr_entry = tk.Entry(tv_upper_frame)
    yr_entry.place(relx=0.04, rely=0.5, relwidth=entry_width, relheight=entry_height)
    yr_label = tk.Label(tv_upper_frame, text="년")
    yr_label.place(relx=0.25, rely=0.5, relwidth=lbl_width, relheight=lbl_height)

    mon_entry = tk.Entry(tv_upper_frame)
    mon_entry.place(relx=0.32, rely=0.5, relwidth=entry_width, relheight=entry_height)
    mon_label = tk.Label(tv_upper_frame, text="월")
    mon_label.place(relx=0.53, rely=0.5, relwidth=lbl_width, relheight=lbl_height)

    day_entry = tk.Entry(tv_upper_frame)
    day_entry.place(relx=0.60, rely=0.5, relwidth=entry_width, relheight=entry_height)
    day_label = tk.Label(tv_upper_frame, text="일")
    day_label.place(relx=0.81, rely=0.5, relwidth=lbl_width, relheight=lbl_height)


    # tv_lower_frame = tk.Frame(tvtable_window)
    # tv_lower_frame.place(relx=0.02, rely=0.51, relwidth=frm_width, relheight=frm_height)
    # tvchannel_label = tk.Label(tv_lower_frame, text="다운받을 방송국을 체크하세요", anchor='sw')
    # tvchannel_label.place(relx=0.04, rely=0.04, relwidth=0.45, relheight=lbl_height)
    #
    # c_cgntv = tk.Checkbutton(tv_lower_frame, text="CGN TV", variable=is_cgntv, onvalue=1, offvalue=0, anchor='sw')
    # c_cgntv.place(relx=0.04, rely=0.16, relwidth=cbx_width, relheight=cbx_height)
    # c_ctstv = tk.Checkbutton(tv_lower_frame, text="CTS TV", variable=is_ctstv, onvalue=1, offvalue=0, anchor='sw')
    # c_ctstv.place(relx=0.04, rely=0.31, relwidth=cbx_width, relheight=cbx_height)
    # c_cbstv = tk.Checkbutton(tv_lower_frame, text="CBS TV", variable=is_cbstv, onvalue=1, offvalue=0, anchor='sw')
    # c_cbstv.place(relx=0.04, rely=0.46, relwidth=cbx_width, relheight=cbx_height)
    # c_goodtv = tk.Checkbutton(tv_lower_frame, text="Good TV", variable=is_goodtv, onvalue=1, offvalue=0, anchor='sw')
    # c_goodtv.place(relx=0.04, rely=0.61, relwidth=cbx_width, relheight=cbx_height)
    # c_cchannel = tk.Checkbutton(tv_lower_frame, text="Cchannel", variable=is_cchannel, onvalue=1, offvalue=0, anchor='sw')
    # c_cchannel.place(relx=0.04, rely=0.76, relwidth=cbx_width, relheight=cbx_height)

    show_btn = tk.Button(tvtable_window, text="실행", font=myfont, bg="#b6dcb6", command=(lambda: run_timetable(year=yr_entry.get(), month=mon_entry.get(), day=day_entry.get())))
    show_btn.place(relx=0.15, rely=0.8, relwidth=0.30, relheight=0.15)

    close_btn = tk.Button(tvtable_window, text="창 닫기", font=myfont, command=tvtable_window.destroy)
    close_btn.place(relx=0.55, rely=0.8, relwidth=0.30, relheight=0.15)

    tvtable_window.bind("<Return>", lambda e: run_timetable(year=yr_entry.get(), month=mon_entry.get(), day=day_entry.get()))
    tvtable_window.bind("<Escape>", lambda e: tvtable_window.destroy())


def open_chdaily():
    entry_width = 0.7
    entry_height = 0.12
    lbl_width = 0.25
    lbl_height = 0.12

    chdaily_window = tk.Toplevel()
    chdaily_window.title("기독일보 기사스크랩")
    chdaily_window.iconbitmap('favicon.ico')
    chdaily_canvas = tk.Canvas(chdaily_window, height=SUB2_HEIGHT, width=SUB2_WIDTH)
    chdaily_canvas.pack()

    url_label = tk.Label(chdaily_window, text="URL을 입력하세요:", anchor='w')
    url_label.place(relx=0.02, rely=0.10, relwidth=lbl_width, relheight=lbl_height)
    url_entry = tk.Entry(chdaily_window, text='url 입력')
    url_entry.place(relx=0.25, rely=0.10, relwidth=entry_width, relheight=entry_height)
    myfont = font.Font(family="맑은 고딕", size=12)

    kw_label = tk.Label(chdaily_window, text="키워드를 입력하세요:", anchor='w')
    kw_label.place(relx=0.02, rely=0.32, relwidth=lbl_width, relheight=lbl_height)
    kw_entry = tk.Entry(chdaily_window, text='키워드 입력')
    kw_entry.place(relx=0.25, rely=0.32, relwidth=entry_width, relheight=entry_height)

    order_label = tk.Label(chdaily_window, text="(선택) 순서를 입력하세요:", anchor='w')
    order_label.place(relx=0.02, rely=0.54, relwidth=lbl_width, relheight=lbl_height)
    order_entry = tk.Entry(chdaily_window, text='순서 입력')
    order_entry.place(relx=0.25, rely=0.54, relwidth=entry_width, relheight=entry_height)

    # show_btn = tk.Button(chdaily_window, text="실행", font=myfont, command=(lambda: run_chdaily_basic(url=url_entry.get(), kw=kw_entry.get(), order=order_entry.get())))
    # show_btn.place(relx=0.76, rely=0.4, relwidth=0.2, relheight=0.1)
    #
    # close_btn = tk.Button(chdaily_window, text="창 닫기", font=myfont, command=chdaily_window.destroy)
    # close_btn.place(relx=0.45, rely=0.9, relwidth=0.1, relheight=0.07)

    show_btn = tk.Button(chdaily_window, text="실행", font=myfont, bg="#b6dcb6", command=(lambda: run_chdaily_basic(url=url_entry.get(), kw=kw_entry.get(), order=order_entry.get())))
    show_btn.place(relx=0.25, rely=0.80, relwidth=0.20, relheight=0.15)

    close_btn = tk.Button(chdaily_window, text="창 닫기", font=myfont, command=chdaily_window.destroy)
    close_btn.place(relx=0.55, rely=0.80, relwidth=0.20, relheight=0.15)

    chdaily_window.bind("<Return>", lambda e: run_chdaily_basic(url=url_entry.get(), kw=kw_entry.get(), order=order_entry.get()))
    chdaily_window.bind("<Escape>", lambda e: chdaily_window.destroy())


def run_timetable(year, month, day):
    maybe_datetime = "-".join([year, month, day])
    try:
        mylogger.info('will search tv timetable on {}'.format(maybe_datetime))
        maybe_datetime_in_datetime = parse(maybe_datetime)
        if (maybe_datetime_in_datetime - datetime.today()).days > 3 or maybe_datetime_in_datetime.year - datetime.today().year < -2:
            raise ValueError

    except ValueError as e:
        tk.messagebox.showinfo("Error", "유효한 날짜를 입력하세요")

    tb.main(maybe_datetime)


def run_chdaily_basic(url, kw, order=1):
    if not is_valid(url) or urlparse(url).netloc not in VALID_URLS:
        tk.messagebox.showinfo("Error", "You entered wrong URL! Please try again!")

    else:
        mylogger.info('will search url: {} keyword: {} order: {}'.format(url, kw, order))
        try:
            int_order = int(order)
            if int_order < 1:
                raise ValueError
            cb.main(url=url, keyword=kw, order=int_order)

        except ValueError:
            tk.messagebox.showinfo("Error", "order variable should be an positive integer (>0)!")


def open_sermon():
    pastor_options = {
        "조용기 목사 (여의도순복음교회)": '조용기',
        "조성노 목사 (푸른교회)": '조성노',
        "석기현 목사 (경향교회)": '석기현',
        "김명혁 목사 (강변교회)": '김명혁',
        "김병삼 목사 (만나교회)": '김병삼'
    }

    frm_width = 0.92
    frm_height = 0.35

    pastor_name_w_church = tk.StringVar()
    pastor_name = tk.StringVar()
    limit_num = tk.IntVar()
    limit_num.set(10)

    is_duplicates_allowed = tk.BooleanVar()
    is_duplicates_allowed.set(True)
    page_num = tk.StringVar()
    page_num.set(1)

    sermon_window = tk.Toplevel()
    sermon_window.title("유명목사 설교 다운받기")
    sermon_window.iconbitmap('favicon.ico')
    sermon_canvas = tk.Canvas(sermon_window, height=SUB_HEIGHT, width=SUB_WIDTH)
    sermon_canvas.pack()
    myfont = font.Font(family="맑은 고딕", size=10)

    sermon_upper_frame = tk.Frame(sermon_window)
    sermon_upper_frame.place(relx=0.04, rely=0.04, relwidth=frm_width, relheight=frm_height)

    sermon_lower_frame = tk.Frame(sermon_window)
    sermon_lower_frame.place(relx=0.04, rely=0.38, relwidth=frm_width, relheight=frm_height)

    pastor_label = tk.Label(sermon_upper_frame, text="목회자를 선택하세요:", anchor='w')
    pastor_label.place(relx=0.02, rely=0.18, relwidth=frm_width, relheight=0.5)
    drop_pastor = tk.OptionMenu(sermon_upper_frame, pastor_name_w_church, *pastor_options)
    drop_pastor.place(relx=0.37, rely=0.18, relwidth=0.60, relheight=0.5)
    # c_allowduplicates = tk.Checkbutton(sermon_upper_frame, text="이미 다운받은 자료라도 중복해서 다운로드하기", variable=is_duplicates_allowed, anchor='sw')
    # c_allowduplicates.place(relx=0.04, rely=0.38, relwidth=0.60, relheight=0.16)

    pgnum_label = tk.Label(sermon_lower_frame, text="▶ 스크랩할 페이지 수:", anchor='w')
    pgnum_label.place(relx=0.02, rely=0.04, relwidth=frm_width, relheight=0.4)
    pgnum_entry = tk.Spinbox(sermon_lower_frame, from_=1, to=50, textvariable=page_num)
    pgnum_entry.place(relx=0.65, rely=0.04, relwidth=0.20, relheight=0.35)

    lmt_label = tk.Label(sermon_lower_frame, text="▶ (선택) 최대 다운받을 설교 갯수:", anchor='w')
    lmt_label.place(relx=0.02, rely=0.54, relwidth=frm_width, relheight=0.4)
    lmt_entry = tk.Entry(sermon_lower_frame, textvariable=limit_num)
    lmt_entry.place(relx=0.65, rely=0.54, relwidth=0.20, relheight=0.35)

    show_btn = tk.Button(sermon_window, text="실행", font=myfont, bg="#b6dcb6", command=(lambda: run_sermon(pastor_name=pastor_name.get(), page_num_s=pgnum_entry.get(), allowduplicates=is_duplicates_allowed.get(), limit_num=lmt_entry.get())))
    show_btn.place(relx=0.15, rely=0.8, relwidth=0.30, relheight=0.15)

    close_btn = tk.Button(sermon_window, text="창 닫기", font=myfont, command=sermon_window.destroy)
    close_btn.place(relx=0.55, rely=0.8, relwidth=0.30, relheight=0.15)

    def change_pastor(*args):
        pastor_name_ = pastor_options[pastor_name_w_church.get()]
        pastor_name.set(pastor_name_)
        mylogger.info('pastor name has been changed to  {}'.format(pastor_name_))

    pastor_name_w_church.trace('w', change_pastor)

    sermon_window.bind("<Return>", lambda *_: run_sermon(pastor_name=pastor_name.get(), page_num_s=pgnum_entry.get(), allowduplicates=is_duplicates_allowed.get()))
    sermon_window.bind("<Escape>", lambda *_: sermon_window.destroy())


def run_sermon(pastor_name, page_num_s, allowduplicates, limit_num):
    mylogger.info('will search pastor {}\'s sermons of {} pages: limit number {}'.format(pastor_name, page_num_s, limit_num))
    try:
        page_num = int(page_num_s)
        limit_num = int(limit_num)
        if page_num < 1 or page_num > 50:
            raise ValueError

        elif limit_num < 1:
            raise ValueError

        sm.main(name=pastor_name, number=page_num, allowduplicates=allowduplicates, limit=limit_num)
    except ValueError:
        tk.messagebox.showinfo("Error", "Oops! You typed in wrong number")


def main():
    root = tk.Tk()
    root.title("기독일보 어플리케이션")
    root.iconbitmap('favicon.ico')
    canvas = tk.Canvas(root, height=MAIN_HEIGHT, width=MAIN_WIDTH)
    canvas.pack()
    mylogger.info('Application started!')

    company_image = tk.PhotoImage(file='company_CI.png')
    company_label = tk.Label(root, image=company_image)
    company_label.place(relx=0.05, rely=0.4, relwidth=0.4, relheight=0.1)

    myfont = font.Font(family="맑은 고딕", size=15, weight="bold")

    info_label = tk.Label(root, text="""!주의!
- 크롬드라이버(chromedriver.exe)파일이 C:\에 있어야 제대로 동작합니다.
- 필요한 크롬버전 확인: 크롬브라우저 주소창에 chrome://version입력
- 크롬드라이버 다운로드 주소 (위의 버전과 일치하는 파일 다운로드):
https://sites.google.com/a/chromium.org/chromedriver/downloads""", anchor='w', justify='left', relief='groove', padx=5, pady=5)
    info_label.place(relx=0.02, rely=0.60, relwidth=0.50, relheight=0.22)

    right_frame = tk.Frame(root)
    right_frame.place(relx=0.52, rely=0.05, relwidth=0.45, relheight=0.90)

    tvtable_btn = tk.Button(right_frame, text='TV 스케줄표 다운받기', command=open_TVtable, relief='raised', bd=3, bg="#f4dcd6", font=myfont)
    tvtable_btn.place(relx=0.05, rely=0.07, relwidth=0.9, relheight=0.24)

    article_scrap_btn = tk.Button(right_frame, text='기독일보 기사 스크랩하기', command=open_chdaily, relief='raised', bd=3, bg="#b2d9ea", font=myfont)
    article_scrap_btn.place(relx=0.05, rely=0.38, relwidth=0.9, relheight=0.24)

    sermon_scrap_btn = tk.Button(right_frame, text='유명목사 설교 스크랩하기', command=open_sermon, relief='raised', bd=3, bg="#84b4c8", font=myfont)
    sermon_scrap_btn.place(relx=0.05, rely=0.69, relwidth=0.9, relheight=0.24)

    exit_btn = tk.Button(root, text='종료', bg='red', fg='white', command=root.quit)
    exit_btn.place(relx=0.02, rely=0.88, relwidth=0.1, relheight=0.08)

    root.mainloop()


if __name__ == "__main__":
    main()
