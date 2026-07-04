from db_init_ import db



class transcription_table(db.Model):
    session_id = db.Column(db.String(50), primary_key=True)
    path_in_webserver = db.Column(db.String(1000))
    report_path_in_webserver =db.Column(db.String(1000))
    status = db.Column(db.String(15))

class history_table(db.Model):
    session_id = db.Column(db.String(50), primary_key=True)
    history = db.Column(db.JSON)   # poora [{"question":..,"answer":..}, ...] ek hi jagah
    updated_at = db.Column(db.DateTime, onupdate=db.func.now(), server_default=db.func.now())
