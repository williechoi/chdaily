
"""
    Cchannel: https://www.cchannel.com/format/format_main?bs_date={YYYY-MM-DD}
    (e.g., https://www.cchannel.com/format/format_main?bs_date=2020-01-24)

    CTS TV: https://www.cts.tv/table?f_yymmdd={YYYY-MM-DD}
    (e.g., https://www.cts.tv/table?f_yymmdd=2020-01-21)

    CBS TV: https://www.cbs.co.kr/tv/timetable/?gubun=&sdate=&cdate={YYYY-MM-DD}
    (e.g., https://www.cbs.co.kr/tv/timetable/?gubun=&sdate=&cdate=2020-01-23)

    GoodTV: http://tv.goodtv.co.kr/schedule.asp?select_date={YYYY-MM-DD}
    (e.g., http://tv.goodtv.co.kr/schedule.asp?select_date=2020-01-23)

    CGN TV: http://www.cgntv.net/center/programschedule.cgn?date={YYYY-MM-DD}
    (e.g., http://www.cgntv.net/center/programschedule.cgn?date=2020-01-22)

"""


TIMETABLES = {'CBS':
                  {'url': 'https://www.cbs.co.kr/tv/timetable/',
                   'name': 'CBS TV'},
              'CTS':
                  {'url': 'https://www.cts.tv/table',
                   'name': 'CTS 기독교TV'},
              'CGN':
                  {'url': 'http://www.cgntv.net/center/programschedule.cgn?mode=tv',
                   'name': 'CGN TV'},
              'GoodTV':
                  {'url': 'http://tv.goodtv.co.kr/schedule.asp',
                   'name': 'GoodTV'},
              'Cchannel':
                  {'url': 'https://www.cchannel.com/format/format_main',
                   'name': 'C채널'}
              }



