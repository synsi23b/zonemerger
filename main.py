from dotenv import load_dotenv
import json
import os
from datetime import datetime, timedelta
import db

load_dotenv()


monitors = json.loads(os.getenv("CONV_MONITOR_PAIRS"))
print("Monitor pairs: ", monitors)

start_day = datetime.strptime(os.getenv("CONV_START_DAY"), "%Y-%m-%d")
end_day = datetime.strptime(os.getenv("CONV_END_DAY"), "%Y-%m-%d")

times = os.getenv("CONV_TIME_RANGE").split(" - ")

def make_dt(day, time):
    hour = int(time.split(":")[0])
    minute = int(time.split(":")[1])
    return datetime(day.year, day.month, day.day, hour, minute)

print("First Day: ", make_dt(start_day, times[0]), " - ", make_dt(start_day, times[1]))
print("Last Day: ", make_dt(end_day, times[0]), " - ", make_dt(end_day, times[1]))

while start_day <= end_day:
    start = make_dt(start_day, times[0])
    end = make_dt(start_day, times[1])
    for mon_left, mon_right in monitors:
        print(f"Working on {mon_left} + {mon_right} for day {start_day.date()}")
        mon_left_ev = db.get_events(mon_left, start, end)
        if len(mon_left_ev) == 0:
            # no events on this day (weekend?) -> skip
            print("Left no events, skipping")
            continue
        mon_right_ev = db.get_events(mon_right, start, end)
        print(f"Event count left {len(mon_left_ev)} right {len(mon_right_ev)}")
        if len(mon_left_ev) != len(mon_right_ev):
            print("!!! Event count is not equal. No implementation for this yet !!!")
            continue
        


    start_day += timedelta(days=1)
