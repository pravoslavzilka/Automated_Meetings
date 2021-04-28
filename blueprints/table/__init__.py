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
        lesson = Lessons(name=name, link=link, start=start, end=end, col=color, number=order_l, day=day_l,
                         table_id=table_id)
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
            lesson = Lessons(name="none",table_id=s.id,day=day,number=i+1)
            db_session.add(lesson)

    current_user.tables.append(s)
    current_user.active_table_id = s.id
    db_session.commit()

    flash("Now you can add your lessons","info")
    return redirect(url_for("table_bp.edit_table",token=s.key))


@table_bp.route("/activate/<token>/")
@login_required
def activate_table(token):
    table = Schedule.query.filter(Schedule.key == token).first()
    current_user.activate_table_id = table.id
    current_user.active_table = table
    db_session.commit()

    flash("Schedule activated","success")
    return redirect(url_for("user_bp.user_schedules"))


@table_bp.route("/add/",methods=["POST"])
def add_table():
    token = request.form["key"]
    table = Schedule.query.filter(Schedule.key == token).first()

    if table:
        if table in current_user.tables:
            flash("You already have this table saved","info")
            return redirect(url_for("user_bp.user_schedules"))
        current_user.tables.append(table)
        current_user.active_table_id = table.id
        current_user.active_table = table
        db_session.commit()
        flash("Schedule added successfully","success")
        return redirect(url_for("user_bp.user_schedules"))

    else:
        flash("No such a schedule, make sure you entered the right key","danger")
        return redirect(url_for("user_bp.user_schedules"))


@table_bp.route("/remove/<token>/")
@login_required
def remove_table(token):
    table = Schedule.query.filter(Schedule.key == token).first()
    current_user.tables.remove(table)
    if current_user.active_table_id == table.id:
        if current_user.tables:
            current_user.active_table_id = current_user.tables[0].id
        else:
            current_user.active_table_id = None
    db_session.commit()
    flash("Schedule removed successfully","success")
    return redirect(url_for("user_bp.user_schedules"))


@table_bp.route("/delete/<token>/")
def delete_table(token):
    table = Schedule.query.filter(Schedule.key == token).first()
    if current_user.username == table.admin_user:

        db_session.delete(table)

        if current_user.active_table_id == table.id:
            if current_user.tables:
                current_user.active_table_id = current_user.tables[0].id
            else:
                current_user.active_table_id = None

        Lessons.query.filter(Lessons.table_id == table.id).delete()
        db_session.commit()
        flash("Schedule deleted successfully","success")
        return redirect(url_for("user_bp.user_schedules"))
    else:
        flash("You haven't permission to delete this table","danger")
        return redirect(url_for("user_bp.user_schedules"))


@table_bp.route("/clone/<token>/")
@login_required
def clone_table(token):
    table = Schedule.query.filter(Schedule.key == token).first()
    new_table = Schedule(name=table.name + " clone", admin_user=current_user.username)

    db_session.add(new_table)
    for lesson in table.lessons:
        new_lesson = Lessons(name=lesson.name,link=lesson.link,start=lesson.start,end=lesson.end,day=lesson.day,
                             col=lesson.col, number=lesson.number,table_id=new_table.id)
        db_session.add(new_lesson)

    db_session.commit()
    flash("Schedule cloned successfully","success")
    return redirect(url_for("table_bp.edit_table",token=table.key))
