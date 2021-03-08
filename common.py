import datetime
import requests
from bs4 import BeautifulSoup

DAYS_ADD_WITH_LEFT_PLACE = {
    "103": 0,
    "122": 1,
    "141": 2,
    "161": 3,
    "180": 4
}


def get_str_date_from_date(date):
    return date.strftime("%m/%d/%Y")


def get_date_from_edt_date(str_date):
    month, day, year = str_date.split('/')
    return datetime.date(int(year), int(month), int(day))


def get_dtdeb_dtend_from_course(course):
    date = get_date_from_edt_date(course['date'])

    hdeb, mdeb = course['hdeb'].split(':')
    hend, mend = course['hend'].split(':')

    dt_deb = datetime.datetime(year=date.year, month=date.month, day=date.day, hour=int(hdeb), minute=int(mdeb))
    dt_end = datetime.datetime(year=date.year, month=date.month, day=date.day, hour=int(hend), minute=int(mend))

    return dt_deb, dt_end


def get_all_course_from_str_date(str_date):
    rsp = requests.get(
        "https://edtmobiliteng.wigorservices.net//WebPsDyn.aspx?action=posEDTBEECOME&serverid=C&Tel=theo.oiry&date=" + str_date)
    sp_page = BeautifulSoup(rsp.text, 'html.parser')
    week_courses = []

    for case in sp_page.find_all('div', {"class": "Case"}):
        time = case.find('td', {"class": "TChdeb"})
        if time is not None:
            teams_div = case.find('div', {"class": "Teams"})
            page_link = None
            for link in teams_div.find_all('a', href=True):
                if link.find('img', {'style': "height:2.5em"}) is not None:
                    page_link = link['href']

            left_place = case['style'].split("left:")[-1].split('%')[0].strip()[0:3]
            case_date = get_date_from_edt_date(str_date) + datetime.timedelta(days=DAYS_ADD_WITH_LEFT_PLACE[left_place])
            place = case.find('td', {"class": "TCSalle"}).text
            teacher, classe = case.find('td', {"class": "TCProf"}).text.split('B')
            course = case.find('td', {"class": "TCase"}).text.split('>')[-1]
            hdeb, hend = time.text.split(' - ')

            week_courses.append(
                {"course": course,
                 "place": place,
                 "teacher": teacher,
                 "class": 'B' + classe,
                 "date": get_str_date_from_date(case_date),
                 "hdeb": hdeb, "hend": hend,
                 "link": page_link})

    return week_courses
