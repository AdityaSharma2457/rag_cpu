from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv()

class Config:
    database_path = Path(
        os.getenv("SQLITE_DATABASE_PATH", "instance/rag_cpu.sqlite3")
    )
    SQLITE_DATABASE_PATH = str(
        database_path
        if database_path.is_absolute()
        else Path(__file__).resolve().parent / database_path
    )
    
