import app
from dotenv import load_dotenv
import os
load_dotenv()
class Config:
    username=os.getenv("DB_USERNAME")
    paswword=os.getenv("DB_PASSWORD")
    app.config["SQLALCHEMY_DATABASE_URI"] = \
    f"mysql+pymysql://{username}:{paswword}@localhost/transcription_path"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False