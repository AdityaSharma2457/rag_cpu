import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ffmpeg_bin = os.getenv("FFMPEG_BIN")
_ffmpeg_dll_directory = None
if os.name == "nt" and ffmpeg_bin:
    ffmpeg_bin_path = Path(ffmpeg_bin)
    if not ffmpeg_bin_path.is_dir():
        raise RuntimeError(f"FFMPEG_BIN does not exist: {ffmpeg_bin_path}")
    os.environ["PATH"] = str(ffmpeg_bin_path) + os.pathsep + os.environ.get("PATH", "")
    _ffmpeg_dll_directory = os.add_dll_directory(str(ffmpeg_bin_path))

from flask import Flask
from flask_cors import CORS
from config import Config
from model_loader import load_models
from db_init_ import init_db
from transcription import transcription_bp
from contributors import avatar_sync

# Initialize the Flask application
def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(Config)

    init_db(app)
    app.register_blueprint(transcription_bp, url_prefix="/transcribe")
    app.register_blueprint(avatar_sync, url_prefix="/contributors")

    return app

# Load models before creating app (whisper model needs to be loaded first)
load_models()

app = create_app()



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)