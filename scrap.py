import requests
from bs4 import BeautifulSoup
import threading
import datetime
import json
import common

ALL_COURSES = []


def get_week__from_page(str_date):
    ALL_COURSES.extend(common.get_all_course_from_str_date(str_date))


print("Loading all weeks...")
response = requests.get(
    "https://edtmobiliteng.wigorservices.net//WebPsDyn.aspx?action=posEDTBEECOME&serverid=C&Tel=theo.oiry&date=03/02/2021")

soup = BeautifulSoup(response.text, 'html.parser')

dates = []
threads = []
today = datetime.date.today()
for week in soup.find_all('div', {"class": "I_Du_SemCal"}):
    str_date = week["onclick"][20:30]

    thread = threading.Thread(target=get_week__from_page, args=(str_date,))
    thread.start()
    threads.append(thread)

for thread in threads:
    thread.join()

ALL_COURSES = sorted(ALL_COURSES, key=lambda course: common.get_date_from_edt_date(course["date"]))

with open('courses.json', 'w') as outfile:
    json.dump([dict(t) for t in {tuple(d.items()) for d in ALL_COURSES}], outfile)

print("All weeks date have been loaded")
