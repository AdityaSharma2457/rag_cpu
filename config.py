
# from dotenv import load_dotenv   # type: ignore[import]
# import os
# load_dotenv()
# class Config:
#     username=os.getenv("DB_USERNAME")
#     password=os.getenv("DB_PASSWORD")
#     dbhost = os.getenv("DB_HOST")
#     dbname = os.getenv{"DB_N  AME"}
#     app.config["SQLALCHEMY_DATABASE_URI"] = \
#     f"mysql+pymysql://{username}:{password}@{dbhost}/{dbname}"
#     app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{os.getenv('DB_USERNAME')}:"
        f"{os.getenv('DB_PASSWORD')}@"
        f"{os.getenv('DB_HOST')}/"
        f"{os.getenv('DB_NAME')}"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False