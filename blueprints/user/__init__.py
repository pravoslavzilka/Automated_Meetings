from flask import Blueprint, render_template, request, flash, redirect, url_for
from datetime import timedelta, datetime, time
from flask_login import login_user, login_required, logout_user
from database import db_session
from models import User
from oauthlib.oauth2 import WebApplicationClient
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

# OAuth 2 client setup
client = WebApplicationClient(GOOGLE_CLIENT_ID)

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
    return render_template("user/login_page.html")


@user_bp.route("/sign_in/",methods=["POST"])
def login_page2():
    user = User.query.filter(User.email == request.form["email"]).first()
    if user and user.check_password(request.form["password"]):
        login_user(user)
        flash("Welcome back to our page","success")
        return redirect(url_for("user_bp.main_app"))
    return render_template("user/login_page.html")


@user_bp.route("/sign_in-google/")
def sign_in_google():
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    res = google_provider_cfg.json()
    authorization_endpoint = res["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)


@user_bp.route("/sign_in-google/callback")
def callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")

    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400

    user = User(
        id_=unique_id, username=users_name, email=users_email, permit=0)

    if not User.query.filter(User.id == unique_id).first():
        db_session.add(user)
        db_session.commit()

    login_user(user)
    flash("Welcome !","success")
    return redirect(url_for("user_bp.main_app"))


@user_bp.route("/sign_out/")
@login_required
def logout():
    logout_user()
    flash("We looking forward to see you again !","success")
    return redirect(url_for("welcome_page"))


@user_bp.route("/sign_up/",methods=["GET"])
def sign_up():
    return render_template("user/register_page.html")


@user_bp.route("/main_app/")
def main_app():
    date_time = schedule[1]["start"]
    sleep_for = (date_time - date_time.now()).total_seconds()
    name_of_day = date_time.strftime("%A")

    date_time = datetime(datetime.now().year,datetime.now().month,datetime.now().day,times[0].hour,times[0].minute)
    return render_template("user/main_app.html", count_down=date_time)


def find_the_lesson(times2):
    times3 = []
    for item in times2:
        item = datetime(int(datetime.now().year), int(datetime.now().month), int(datetime.now().day),item.hour,item.minute,item.second)
        times3.append(item)

    later = filter(lambda d: d > datetime.now(), times3)
    nearest_lesson = min(later, key=lambda d: abs(d - datetime.now()))
    return nearest_lesson


