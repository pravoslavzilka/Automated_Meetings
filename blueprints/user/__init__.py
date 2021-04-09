from flask import Blueprint, render_template


user_bp = Blueprint("user_bp",__name__,template_folder="templates")


@user_bp.route("/login_page/")
def login_page():
    return render_template("user/login_page.html")