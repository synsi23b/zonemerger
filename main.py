from dotenv import load_dotenv
import json
import os
from datetime import datetime, timedelta
import db
import logging
from pathlib import Path
from ffmpeg import combine

load_dotenv()

this_file = Path(__file__).resolve()
log = this_file.parent / "logs" / f"{int(datetime.now().timestamp())}.log"
logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', filename=str(log),level=logging.INFO)


monitors = json.loads(os.getenv("CONV_MONITOR_PAIRS"))
logging.info(f"Monitor pairs: {monitors}")

start_day = datetime.strptime(os.getenv("CONV_START_DAY"), "%Y-%m-%d")
end_day = datetime.strptime(os.getenv("CONV_END_DAY"), "%Y-%m-%d")

times = os.getenv("CONV_TIME_RANGE").split(" - ")

def make_dt(day, time):
    hour = int(time.split(":")[0])
    minute = int(time.split(":")[1])
    return datetime(day.year, day.month, day.day, hour, minute)

logging.info(f"First Day: {make_dt(start_day, times[0])} - {make_dt(start_day, times[1])}")
logging.info(f"Last Day: {make_dt(end_day, times[0])} - {make_dt(end_day, times[1])}")

while start_day <= end_day:
    start = make_dt(start_day, times[0])
    end = make_dt(start_day, times[1])
    for mon_left, mon_right in monitors:
        logging.info(f"Working on {mon_left} + {mon_right} for day {start_day.date()}")
        mon_left_ev = db.get_events(mon_left, start, end)
        if len(mon_left_ev) == 0:
            # no events on this day (weekend?) -> skip
            logging.info("Left Monitor no events, skipping")
            continue
        mon_right_ev = db.get_events(mon_right, start, end)
        logging.info(f"Event count left {len(mon_left_ev)} right {len(mon_right_ev)}")
        if len(mon_left_ev) != len(mon_right_ev):
            logging.error("!!! Event count is not equal. No implementation for this yet !!!")
            continue
        combine(mon_left_ev, mon_right_ev)
    # go to next day for loopin
    start_day += timedelta(days=1)
