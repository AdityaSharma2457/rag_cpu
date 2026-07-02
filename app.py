from flask import Flask
from flask_cors import CORS
from config import Config
from model_loader import load_models
import db_init_
from transcription import transcription_bp
from contributors import avatar_sync

# Initialize the Flask application
def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(Config)

    db.init_app(app)
    app.register_blueprint(transcription_bp, url_prefix="/transcribe")
    app.register_blueprint(avatar_sync, url_prefix="/contributors")

    with app.app_context():
        db.create_all()

    return app

# Load models before creating app (whisper model needs to be loaded first)
load_models()

db = db_init_.db
app = create_app()



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000,debug=True)