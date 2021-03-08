import os
import discord
from dotenv import load_dotenv
import asyncio
import datetime
import common
import json
import requests
import urllib

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
CUTTLY_TOKEN = os.getenv('CUTTLY_TOKEN')


def get_all_course_with_link_now():
    return sorted(common.get_all_course_from_str_date(common.get_str_date_from_date(datetime.datetime.now()))
                  , key=lambda course: (common.get_date_from_edt_date(course['date']), course['hdeb']))


def shorten_link(url):
    url = urllib.parse.quote(url)
    api_url = 'http://cutt.ly/api/api.php?key={}&short={}'.format(CUTTLY_TOKEN, url)
    data = requests.get(api_url).json()["url"]
    if data["status"] == 7:
        shortened_url = data["shortLink"]
        return shortened_url
    else:
        print("[!] Error Shortening URL:", data)
        return url


def time_delta_to_str(timedelta):
    return ':'.join(str(timedelta).split(':')[:2])


def get_last_course_with_link(course_links):
    all_with_links = [course for course in course_links if course['link'] is not None]
    return all_with_links[-1] if len(all_with_links) > 0 else None


def get_adjacent_courses(all_courses, selected_course):
    adjacent_courses = [selected_course]
    index = all_courses.index(selected_course)

    for i in range(index - 1, -1, -1):
        if all_courses[i]['course'] == selected_course['course']:
            adjacent_courses.append(all_courses[i])
        else:
            break
    for i in range(index + 1, len(all_courses)):
        if all_courses[i]['course'] == selected_course['course']:
            adjacent_courses.append(all_courses[i])
        else:
            break
    return adjacent_courses


def build_infos(all_courses, selected_course):
    adjacent_courses = get_adjacent_courses(all_courses, selected_course)
    max_date = None
    total_time = None
    for course in adjacent_courses:

        if course['date'] != selected_course['date']:
            continue

        dt_deb, dt_end = common.get_dtdeb_dtend_from_course(course)
        if max_date is None or dt_end > max_date:
            max_date = dt_end
        if total_time is None:
            total_time = dt_end - dt_deb
        else:
            total_time += dt_end - dt_deb

    rest_time_course = None
    with open('../courses.json', 'r') as courses_file:
        data = json.load(courses_file)
        same_next_courses = [course for course in data if course['course'] == selected_course['course']]
        for course in same_next_courses:
            dt_deb, dt_end = common.get_dtdeb_dtend_from_course(course)
            if dt_end > max_date:
                if rest_time_course is None:
                    rest_time_course = dt_end - dt_deb
                else:
                    rest_time_course += dt_end - dt_deb

    return {'course_time': total_time, 'rest_time': rest_time_course}


client = discord.Client()


async def timer():
    await client.wait_until_ready()
    channel = client.get_channel(811206115911401502)

    last_showed_course = None

    while True:
        try:
            all_week_courses = get_all_course_with_link_now()
            last_course_with_link = get_last_course_with_link(all_week_courses)
            if last_course_with_link is not None:
                if last_showed_course is None or (
                        last_showed_course['course'] != last_course_with_link['course']
                        or last_showed_course['date'] != last_course_with_link['date']):

                    last_showed_course = last_course_with_link
                    supp_infos = build_infos(all_week_courses, last_showed_course)

                    message = "Module: " + last_showed_course['course'] + " par " + last_showed_course['teacher'] + "\n"
                    message += "Durée du cours: " + time_delta_to_str(supp_infos['course_time']) + "\n"
                    if supp_infos['rest_time'] is None:
                        message += "Durée restante du module après ce cour: 0:00\n"
                    else:
                        message += "Durée restante du module après ce cour: " + time_delta_to_str(
                            supp_infos['rest_time']) + "\n"
                    message += "Lien du cour: " + shorten_link(last_showed_course['link'])

                    await channel.send(message)
        except:
            pass
        await asyncio.sleep(1)


client.loop.create_task(timer())
client.run(TOKEN)
