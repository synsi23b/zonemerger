import mysql.connector
from dotenv import load_dotenv
import os
from datetime import datetime



_db = None

def get_db() -> mysql.connector.CMySQLConnection:
    global _db
    if _db is None:
        load_dotenv()
        _db = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        database=os.getenv("DB_NAME")
        )
    if not _db.is_connected():
        _db.connect()
    return _db


def get_events(mon_id:int, start:datetime, end:datetime) -> list:
    db = get_db()
    crs = db.cursor(dictionary=True)
    crs.execute(f"SELECT Name, StartDateTime, EndDateTime, Width, Height, `Length`, Frames, DefaultVideo FROM Events WHERE MonitorId = {mon_id} AND StartDateTime > '{start}' AND EndDateTime < '{end}' ORDER BY id;")
    return list(crs)