from flask import Flask, render_template
from blueprints.user.__init__ import user_bp
from database import db_session

app = Flask(__name__)
app.register_blueprint(user_bp, url_prefix="/user")


@app.route("/")
def welcome_page():
    return render_template("index.html")


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

if __name__ == "__main__":
    app.run(host="0.0.0.0",debug=True)