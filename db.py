from flask_sqlalchemy import SQLAlchemy
import app
db = SQLAlchemy(app)

class transcription(db.Model):
    id = db.Column(db.integer, primary_key=True,autoincrement=True)
    filename = db.Column(db.string(50))
    path_in_webserver = db.Column(db.String(100))
    status = db.Column(db.string(15))






