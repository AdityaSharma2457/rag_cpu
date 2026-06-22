from flask import Flask 
import db_init_
from transcription import transcription_bp
import os
from dotenv import load_dotenv
load_dotenv()

mysql_connector = os.getenv("SQLALCHEMY_DATABASE_URI")

# Initialize the Flask application
def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = mysql_connector
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    app.register_blueprint(transcription_bp,url_prefix="/transcription")




    with app.app_context():
        db.create_all()

    return app


app = create_app()





if __name__ == "__main__":
    app.run(debug=True)