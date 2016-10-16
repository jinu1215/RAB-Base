import time
import calendar

from backend.libs.decorators import api_call

@api_call(['GET'], auth_required=False)
def datetime(request):
    now = time.gmtime()
    date_value = time.strftime("%a, %d %b %Y %H:%M:%S +0000", now)
    timestamp = str(calendar.timegm(now))

    response = dict()
    response.update({"date" : date_value})
    response.update({"timestamp" : timestamp})

    return response
