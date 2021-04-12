from flask import Blueprint, render_template
from datetime import timedelta, datetime
from time import sleep
from threading import Thread
import webbrowser


user_bp = Blueprint("user_bp",__name__,template_folder="templates")

schedule = {
    1:{"start":datetime(2021,4,10,23,35),"end":datetime(2021,4,11,5)}
}

schedule2 = {
    "mat":datetime(2021,4,11,23,35),
    "sjl":datetime(2021,4,10,23,35),
    "fyz":datetime(2021,4,11,2,35)
}
times = [datetime(2021,4,10,23,35),datetime(2021,4,11,23,35),datetime(2021,4,11,2,35)]


@user_bp.route("/sign_in/")
def login_page():
    return render_template("user/login_page.html")


@user_bp.route("/main_app/")
def main_app():

    date_time = datetime.now() + timedelta(days=1)
    start_time = schedule[1]["start"]
    value, name = find_the_lesson(schedule2)
    print(name," : ",value)
    date_time = schedule[1]["start"]
    sleep_for = (date_time - date_time.now()).total_seconds()
    name_of_day = date_time.strftime("%A")
    print(name_of_day)
    if sleep_for < 0:
        date_time = schedule[1]["end"]

    return render_template("user/main_app.html", count_down=date_time)


def find_the_lesson(kwargs):
    times2 = []
    times2_names = []
    for name,value in kwargs.items():
        times2_names.append(name)
        times2.append(value)
    later = filter(lambda d: d > datetime.now(), times2)
    nearest_lesson = min(later, key=lambda d: abs(d - datetime.now()))
    index = times2.index(nearest_lesson)
    return nearest_lesson, times2_names[index]

