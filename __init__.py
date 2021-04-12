from flask import Flask, render_template
from blueprints.user.__init__ import user_bp
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

app = Flask(__name__)
app.register_blueprint(user_bp, url_prefix="/user")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128))
    permit = db.Column(db.Integer)

    def __repr__(self):
        return self.name

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def is_active(self):
        return True

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id


class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    admin = db.Column(db.String(80))
    key = db.Column(db.String(80), default=uuid.uuid4().hex)
    name = db.Column(db.String(80), db.ForeignKey('user.id'),nullable=False)
    user = db.relationship('User', backref=db.backref('schedules', lazy=True))


class Lessons(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    link = db.Column(db.String(80))
    start = db.Column(db.String(80))
    end = db.Column(db.Time)
    table_id = db.Column(db.Integer, db.ForeignKey('schedule.id'),nullable=False)
    schedule = db.relationship('Schedule',backref=db.backref('lessons', lazy=True))


@app.route("/")
def welcome_page():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0",debug=True)