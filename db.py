from flask_sqlalchemy import SQLAlchemy
from db_init_ import db

class transcription_table(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    filename = db.Column(db.String(50))
    path_in_webserver = db.Column(db.String(100))
    status = db.Column(db.String(15))
