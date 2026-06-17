from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    username=os.getenv("DB_USERNAME")
    dbhost=os.getenv("DB_HOST")
    dbname=os.getenv("DB_NAME")
    password=os.getenv("DB_PASSWORD")
    