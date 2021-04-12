from flask import Blueprint, render_template
from datetime import timedelta, datetime, time
from flask_login import LoginManager
from models import User


login_manager = LoginManager()
user_bp = Blueprint("user_bp",__name__,template_folder="templates")

schedule = {
    1:{"start":datetime(2021,4,10,23,35),"end":datetime(2021,4,11,5)}
}

schedule2 = {
    "mat":datetime(2021,4,11,23,35),
    "sjl":datetime(2021,4,10,23,35),
    "fyz":datetime(2021,4,11,2,35)
}
times = [time(23,59),time(14,20),time(16)]


@user_bp.route("/sign_in/",methods=["GET"])
def login_page():
    return render_template("user/login_page.html")


@user_bp.route("/sign_in/",methods=["POST"])
def login_page2():
    return render_template("user/login_page.html")


@user_bp.route("/main_app/")
def main_app():
    print(User.query.all())

    date_time = schedule[1]["start"]
    sleep_for = (date_time - date_time.now()).total_seconds()
    name_of_day = date_time.strftime("%A")

    date_time = datetime(datetime.now().year,datetime.now().month,datetime.now().day,times[0].hour,times[0].minute)
    print(find_the_lesson(times))
    return render_template("user/main_app.html", count_down=date_time)


def find_the_lesson(times2):
    times3 = []
    for item in times2:
        item = datetime(int(datetime.now().year), int(datetime.now().month), int(datetime.now().day),item.hour,item.minute,item.second)
        times3.append(item)
        print(item)
    print(times3)
    later = filter(lambda d: d > datetime.now(), times3)
    print(later)
    nearest_lesson = min(later, key=lambda d: abs(d - datetime.now()))
    return nearest_lesson


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)
