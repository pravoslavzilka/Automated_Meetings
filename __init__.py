from flask import Flask, render_template
from blueprints.user.__init__ import user_bp

app = Flask(__name__)
app.register_blueprint(user_bp, url_prefix="/user")


@app.route("/")
def welcome_page():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0",debug=True)