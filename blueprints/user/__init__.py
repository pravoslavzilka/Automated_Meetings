from flask import Blueprint, render_template, request, flash, redirect, url_for
from datetime import timedelta, datetime, time
from flask_login import login_user, login_required, logout_user, current_user
from database import db_session
from models import User, Schedule
import requests
import json
import os


user_bp = Blueprint("user_bp",__name__,template_folder="templates")

# google login consts
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)


schedule2 = {
    "mat":datetime(2021,4,11,23,35),
    "sjl":datetime(2021,4,10,23,35),
    "fyz":datetime(2021,4,11,2,35)
}
times = [time(23,59),time(14,20),time(16)]




def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL, verify=False).json()


@user_bp.route("/sign_in/",methods=["GET"])
def login_page():
    if current_user.is_authenticated:
        return redirect(url_for("user_bp.main_app"))

    return render_template("user/login_page.html")


@user_bp.route("/sign_in/",methods=["POST"])
def login_page2():
    user = User.query.filter(User.email == request.form["email"]).first()
    if user and user.check_password(request.form["password"]):
        login_user(user,remember=True)
        flash("Welcome back to our page","success")
        return redirect(url_for("user_bp.main_app"))
    flash("Your email or password is incorrect","danger")
    return render_template("user/login_page.html",email=request.form["email"])


@user_bp.route("/sign_out/")
@login_required
def logout():
    logout_user()
    flash("We looking forward to see you again !","success")
    return redirect(url_for("welcome_page"))


@user_bp.route("/sign_up/",methods=["GET"])
def sign_up():
    if current_user.is_authenticated:
        return redirect(url_for("user_bp.main_app"))

    return render_template("user/register_page.html")


@user_bp.route("/sign_up/",methods=["POST"])
def sign_up2():
    username = request.form["username"]
    email = request.form["email"]
    password = request.form["password"]
    user = User.query.filter(User.email == email).first()
    if user:
        flash("User with this email address already exists","danger")
        return render_template("user/register_page.html",username=username)

    user = User.query.filter(User.username == username).first()
    if user:
        flash("User with this username already exists", "danger")
        return render_template("user/register_page.html", email=email)

    user = User(username=username, email=email, permit=0)
    user.set_password(password)
    db_session.add(user)
    db_session.commit()
    flash("Welcome to Automated Meetings!","success")
    login_user(user)
    return redirect(url_for("user_bp.main_app"))


@user_bp.route("/main_app/")
@login_required
def main_app():
    date_time = find_the_lesson(schedule2)

    date_time = datetime(datetime.now().year,datetime.now().month,datetime.now().day,times[0].hour,times[0].minute)
    return render_template("user/main_app.html", count_down=date_time)


def find_the_lesson(times2):
    times3 = []
    for item in times2.values():
        item = datetime(int(datetime.now().year), int(datetime.now().month), int(datetime.now().day),item.hour,item.minute,item.second)
        times3.append(item)

    later = filter(lambda d: d > datetime.now(), times3)
    try:
        nearest_lesson = min(later, key=lambda d: abs(d - datetime.now()))
    except ValueError:
        nearest_lesson = False
    return nearest_lesson


@user_bp.route("/your_schedules/")
@login_required
def user_schedules():
    own_tables = Schedule.query.filter(Schedule.admin_user == current_user.username).all()
    tables = current_user.tables
    return render_template("user/schedules.html",tables=tables,own_tables=own_tables)


@user_bp.route("/table/<token>/")
def view_table(token):
    table = Schedule.query.filter(Schedule.key == token).first()
    lessons = {
        "mon": [var if var.day == "mon" else "none" for var in table.lessons],
        "thu": [var if var.day == "thu" else "none" for var in table.lessons],
        "wen": [var if var.day == "wen" else "none" for var in table.lessons],
        "thur": [var if var.day == "thur" else "none" for var in table.lessons],
        "fri": [var if var.day == "fri" else "none" for var in table.lessons],
        "sat": [var if var.day == "sat" else "none" for var in table.lessons],
        "sun": [var if var.day == "sun" else "none" for var in table.lessons],
    }
    return render_template("user/view_table.html", table=table, lessons=lessons)


@user_bp.route("change_lesson/",methods=["POST"])
def change_lesson():
    return redirect(url_for("user_bp.view_table",token=request.form["token"]))


