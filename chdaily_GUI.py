import tkinter as tk
from tkinter import messagebox
import chdaily_basic as cb
import timetable as tb
import sermon as sm
from urllib.parse import urljoin, urlparse
from dateutil.parser import parse
from datetime import datetime, timedelta

HEIGHT = 400
WIDTH = 900
VALID_URLS = ["www.christiandaily.co.kr", "kr.christianitydaily.com"]


def is_valid(url):
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)


def open_TVtable():
    frm_width = 0.96
    frm_height = 0.47
    lbl_width = 0.02
    lbl_height = 0.10
    cbx_width = 0.33
    cbx_height = 0.15
    entry_width = 0.1
    entry_height = 0.10

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
    tvtable_canvas = tk.Canvas(tvtable_window, height=400, width=WIDTH)
    tvtable_canvas.pack()

    tv_upper_frame = tk.Frame(tvtable_window)
    tv_upper_frame.place(relx=0.02, rely=0.02, relwidth=frm_width, relheight=frm_height)
    tvdate_label = tk.Label(tv_upper_frame, text="날짜를 입력하세요", anchor='sw')
    tvdate_label.place(relx=0.04, rely=0.04, relwidth=0.45, relheight=lbl_height)

    yr_label = tk.Label(tv_upper_frame, text="년")
    yr_label.place(relx=0.15, rely=0.2, relwidth=lbl_width, relheight=lbl_height)
    yr_entry = tk.Entry(tv_upper_frame)
    yr_entry.place(relx=0.04, rely=0.2, relwidth=entry_width, relheight=entry_height)

    mon_label = tk.Label(tv_upper_frame, text="월")
    mon_label.place(relx=0.31, rely=0.2, relwidth=lbl_width, relheight=lbl_height)
    mon_entry = tk.Entry(tv_upper_frame)
    mon_entry.place(relx=0.20, rely=0.2, relwidth=entry_width, relheight=entry_height)

    day_label = tk.Label(tv_upper_frame, text="일")
    day_label.place(relx=0.47, rely=0.2, relwidth=lbl_width, relheight=lbl_height)
    day_entry = tk.Entry(tv_upper_frame)
    day_entry.place(relx=0.36, rely=0.2, relwidth=entry_width, relheight=entry_height)

    tv_lower_frame = tk.Frame(tvtable_window)
    tv_lower_frame.place(relx=0.02, rely=0.51, relwidth=frm_width, relheight=frm_height)
    tvchannel_label = tk.Label(tv_lower_frame, text="다운받을 방송국을 체크하세요", anchor='sw')
    tvchannel_label.place(relx=0.04, rely=0.04, relwidth=0.45, relheight=lbl_height)

    c_cgntv = tk.Checkbutton(tv_lower_frame, text="CGN TV", variable=is_cgntv, onvalue=1, offvalue=0, anchor='sw')
    c_cgntv.place(relx=0.04, rely=0.16, relwidth=cbx_width, relheight=cbx_height)
    c_ctstv = tk.Checkbutton(tv_lower_frame, text="CTS TV", variable=is_ctstv, onvalue=1, offvalue=0, anchor='sw')
    c_ctstv.place(relx=0.04, rely=0.31, relwidth=cbx_width, relheight=cbx_height)
    c_cbstv = tk.Checkbutton(tv_lower_frame, text="CBS TV", variable=is_cbstv, onvalue=1, offvalue=0, anchor='sw')
    c_cbstv.place(relx=0.04, rely=0.46, relwidth=cbx_width, relheight=cbx_height)
    c_goodtv = tk.Checkbutton(tv_lower_frame, text="Good TV", variable=is_goodtv, onvalue=1, offvalue=0, anchor='sw')
    c_goodtv.place(relx=0.04, rely=0.61, relwidth=cbx_width, relheight=cbx_height)
    c_cchannel = tk.Checkbutton(tv_lower_frame, text="Cchannel", variable=is_cchannel, onvalue=1, offvalue=0, anchor='sw')
    c_cchannel.place(relx=0.04, rely=0.76, relwidth=cbx_width, relheight=cbx_height)

    btn_show = tk.Button(tvtable_window, text="실행", command=(lambda: run_timetable(year=yr_entry.get(), month=mon_entry.get(), day=day_entry.get())))
    btn_show.place(relx=0.76, rely=0.45, relwidth=0.2, relheight=0.1)

    btn_exit = tk.Button(tvtable_window, text="창 닫기", command=tvtable_window.destroy)
    btn_exit.place(relx=0.45, rely=0.9, relwidth=0.1, relheight=0.07)


def open_chdaily():
    entry_width = 0.4
    entry_height = 0.08
    lbl_width = 0.2
    lbl_height = 0.08

    chdaily_window = tk.Toplevel()
    chdaily_window.title("기독일보 기사스크랩")
    chdaily_canvas = tk.Canvas(chdaily_window, height=HEIGHT, width=WIDTH)
    chdaily_canvas.pack()

    url_label = tk.Label(chdaily_window, text="URL을 입력하세요: ")
    url_label.place(relx=0.05, rely=0.2, relwidth=lbl_width, relheight=lbl_height)
    url_entry = tk.Entry(chdaily_window, text='url 입력')
    url_entry.place(relx=0.3, rely=0.2, relwidth=entry_width, relheight=entry_height)

    kw_label = tk.Label(chdaily_window, text="키워드를 입력하세요: ")
    kw_label.place(relx=0.05, rely=0.4, relwidth=lbl_width, relheight=lbl_height)
    kw_entry = tk.Entry(chdaily_window, text='키워드 입력')
    kw_entry.place(relx=0.3, rely=0.4, relwidth=entry_width, relheight=entry_height)

    order_label = tk.Label(chdaily_window, text="(선택) 순서를 입력하세요: ")
    order_label.place(relx=0.05, rely=0.6, relwidth=lbl_width, relheight=lbl_height)
    order_entry = tk.Entry(chdaily_window, text='순서 입력')
    order_entry.place(relx=0.3, rely=0.6, relwidth=entry_width, relheight=entry_height)

    btn_show = tk.Button(chdaily_window, text="실행", command=(lambda: run_chdaily_basic(url=url_entry.get(), kw=kw_entry.get(), order=order_entry.get())))
    btn_show.place(relx=0.76, rely=0.4, relwidth=0.2, relheight=0.1)

    btn_exit = tk.Button(chdaily_window, text="창 닫기", command=chdaily_window.destroy)
    btn_exit.place(relx=0.45, rely=0.9, relwidth=0.1, relheight=0.07)


def run_timetable(year, month, day):
    maybe_datetime = "-".join([year, month, day])
    try:
        maybe_datetime_in_datetime = parse(maybe_datetime)
        if (maybe_datetime_in_datetime - datetime.today()).days > 3 or maybe_datetime_in_datetime.year - datetime.today().year < -2:
            raise ValueError
        tb.main(maybe_datetime)
    except ValueError as e:
        tk.messagebox.showinfo("Error", "유효한 날짜를 입력하세요")


def run_chdaily_basic(url, kw, order=1):
    if not is_valid(url) or urlparse(url).netloc not in VALID_URLS:
        tk.messagebox.showinfo("Error", "You entered wrong URL! Please try again!")

    else:
        try:
            a = int(order)
            if a < 1:
                raise ValueError
            cb.main(url=url, keyword=kw, order=order)

        except ValueError:
            tk.messagebox.showinfo("Error", "order variable should be integer larger than 0!")


def open_sermon():
    tk.messagebox.showinfo("Info", "준비중입니다")


def main():
    root = tk.Tk()
    root.title("기독일보 어플리케이션")
    root.iconbitmap('favicon.ico')
    canvas = tk.Canvas(root, height=HEIGHT, width=WIDTH)
    canvas.pack()

    company_image = tk.PhotoImage(file='company_CI.png')
    company_label = tk.Label(root, image=company_image)
    company_label.place(relx=0.05, rely=0.4, relwidth=0.4, relheight=0.1)

    right_frame = tk.Frame(root, bg='gray')
    right_frame.place(relx=0.52, rely=0.05, relwidth=0.45, relheight=0.90)

    tvtable_btn = tk.Button(right_frame, text='TV 스케줄표 다운받기', command=open_TVtable)
    tvtable_btn.place(relx=0.05, rely=0.07, relwidth=0.9, relheight=0.24)

    article_scrap_btn = tk.Button(right_frame, text='기독일보 기사 스크랩하기', command=open_chdaily)
    article_scrap_btn.place(relx=0.05, rely=0.38, relwidth=0.9, relheight=0.24)

    sermon_scrap_btn = tk.Button(right_frame, text='유명목사 설교 스크랩하기', command=open_sermon)
    sermon_scrap_btn.place(relx=0.05, rely=0.69, relwidth=0.9, relheight=0.24)

    exit_btn = tk.Button(root, text='종료', bg='red', fg='white', command=root.quit)
    exit_btn.place(relx=0.02, rely=0.88, relwidth=0.1, relheight=0.08)

    root.mainloop()


if __name__ == "__main__":
    main()
