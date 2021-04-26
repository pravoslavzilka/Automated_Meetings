from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager
from blueprints.user.__init__ import user_bp
from blueprints.table.__init__ import table_bp
from database import db_session
from models import User
import os


app = Flask(__name__)
app.register_blueprint(user_bp, url_prefix="/user")
app.register_blueprint(table_bp, url_prefix="/table")
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(16)

# flask-login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "user_bp.login_page"
login_manager.login_message = "Please sign in to access this page"
login_manager.login_message_category = "info"


@app.route("/")
def welcome_page():
    return render_template("index.html")


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter(User.id == user_id).first()


if __name__ == "__main__":
    app.run(host="0.0.0.0",debug=True)