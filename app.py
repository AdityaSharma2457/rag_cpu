from flask import Flask 
import db_init_
from transcription import transcription_bp
from config import Config 
from dotenv import load_dotenv
load_dotenv()


# Initialize the Flask application
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)


    db.init_app(app)
    app.register_blueprint(transcription_bp,url_prefix="/transcription")

    with app.app_context():
        db.create_all()
    
    return app

db = db_init_.db
app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000,debug=True)