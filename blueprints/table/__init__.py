from flask import Blueprint, render_template, url_for, redirect, request, flash
from flask_login import current_user
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


@table_bp.route("change_lesson/",methods=["POST"])
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
    return redirect(url_for("table_bp.view_table",token=request.form["token"]))

