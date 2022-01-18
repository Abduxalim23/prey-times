
def CurrentTimeAsStr():
    # this function return time in given location for Tashkent 
    # return time as string format
    import datetime
    import pytz
    import time
    from timezonefinder import TimezoneFinder
    lat = 41.29945201839658
    long = 69.24605471327733
    tf = TimezoneFinder()
    datez = tf.timezone_at(lat=lat,lng=long)
    datez = str(datez)
    timez = datetime.datetime.now(pytz.timezone(datez))
    times = datetime.datetime.strftime(timez,"%Y:%m:%d %H:%M:%S")
    return times
    
def CurrentDate():
    import datetime
    times = CurrentTimeAsStr()
    timep = datetime.datetime.strptime(times,"%Y:%m:%d %H:%M:%S")
    return timep

def CurrentDateTime():
    import datetime
    tp = CurrentDateTime()
    dt = datetime.datetime(tp.year,tp.month,tp.day,tp.hour,tp.minute,tp.second)
    return dt
def today():
    import datetime
    time = CurrentDate()
    today = datetime.date(time.year,time.month,time.day)
    return today

def add5minut(satr):
    import datetime
    d = datetime.datetime.strptime(satr,"%H:%M")
    h = 0
    m = 5 + d.minute
    if m - 59 > 0 :
        h = h + 1
        m = m - 59
    m_s = ""
    if m <= 9:
        return str(d.hour + h) + ":" +"0" + str(m)
    else:
        return str(d.hour + h) + ":" + str(m)

    

