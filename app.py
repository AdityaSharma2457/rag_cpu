from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from db import transcription
# Initialize the Flask application


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = \
    "mysql+pymysql://root:@di.kota@localhost/transcription_path"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

with app.app_context():
    db.create_all()

# @app.route("/")


if __name__ == "__main__":
    app.run(debug=True)