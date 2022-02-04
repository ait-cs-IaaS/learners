import time
from datetime import datetime
from datetime import timedelta

def datetime_from_utc_to_local(utc_datetime, date=True):
    if (utc_datetime is not None):
        now_timestamp = time.time()
        offset = datetime.fromtimestamp(
            now_timestamp) - datetime.utcfromtimestamp(now_timestamp)
        if (date):
            timestamp = (utc_datetime + offset).strftime("%m/%d/%Y, %H:%M:%S")
        else:
            timestamp = (utc_datetime + offset).strftime("%H:%M:%S")
        return timestamp
    else:
        return None