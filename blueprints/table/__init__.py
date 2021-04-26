from flask import Blueprint, render_template, url_for, redirect, request, flash
from flask_login import current_user, login_required
from models import Schedule, Lessons
from database import db_session
from datetime import time


table_bp = Blueprint("table_bp",__name__,template_folder="templates")


@table_bp.route("view/<token>/")
def view_table(token):
    table = Schedule.query.filter(Schedule.key == token).first()
    lessons = {
        "mon": [var for var in table.lessons if var.day == "mon"],
        "thu": [var for var in table.lessons if var.day == "thu"],
        "wen": [var for var in table.lessons if var.day == "wen"],
        "thur": [var for var in table.lessons if var.day == "thur"],
        "fri": [var for var in table.lessons if var.day == "fri"],
        "sat": [var for var in table.lessons if var.day == "sat"],
        "sun": [var for var in table.lessons if var.day == "sun"],
    }
    return render_template("table/view_table.html", table=table, lessons=lessons)


@table_bp.route("edit/<token>/")
@login_required
def edit_table(token):
    table = Schedule.query.filter(Schedule.key == token).first()
    if table.admin_user == current_user.username:
        lessons = {
            "mon": [var for var in table.lessons if var.day == "mon"],
            "thu": [var for var in table.lessons if var.day == "thu"],
            "wen": [var for var in table.lessons if var.day == "wen"],
            "thur": [var for var in table.lessons if var.day == "thur"],
            "fri": [var for var in table.lessons if var.day == "fri"],
            "sat": [var for var in table.lessons if var.day == "sat"],
            "sun": [var for var in table.lessons if var.day == "sun"],
        }
        return render_template("table/edit_table.html", table=table, lessons=lessons)
    else:
        flash("You haven't permission to modify this schedule","danger")
        return redirect(url_for("table_bp.view_table"))


@table_bp.route("change_lesson/",methods=["POST"])
@login_required
def change_lesson():
    table_id = request.form["id-table"]

    # lesson info
    order_l = request.form["num"]
    day_l = request.form["day"]
    name = request.form["name"]
    link = request.form["link"]

    start = request.form["start"]
    start = start.split(":")
    start = time(int(start[0]), int(start[1]))

    end = request.form["end"]
    end = end.split(":")
    end = time(int(end[0]),int(end[1]))

    color = request.form["col"]

    lesson = Lessons.query.filter(Lessons.table_id == table_id, Lessons.number == order_l, Lessons.day == day_l).first()

    if lesson:
        lesson.name = name
        lesson.link = link
        lesson.start = start
        lesson.end = end
        lesson.col = color

    else:
        lesson = Lessons(name=name, link=link, start=start, end=end, col=color, number=order_l, day=day_l, table_id=table_id)
        db_session.add(lesson)

    db_session.commit()

    flash("Lesson updated successfully","success")
    return redirect(url_for("table_bp.edit_table",token=request.form["token"]))


@table_bp.route("/create/", methods=["POST"])
@login_required
def create_table():
    name = request.form["name"]
    s = Schedule(name=name, admin_user=current_user.username)
    db_session.add(s)
    db_session.commit()

    days = ["mon","thu","wen","thur","fri","sat","sun"]
    for day in days:
        for i in range(7):
            l = Lessons(name="none",table_id=s.id,day=day,number=i+1)
            db_session.add(l)

    db_session.commit()
    current_user.tables.append(s)
    current_user.active_table_id = s.id
    flash("Now you can add your lessons","info")
    return redirect(url_for("table_bp.edit_table",token=s.key))
