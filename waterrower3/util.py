import datetime


def format_sec(time_sec):
    return("{0:02}:{1:02}".format(time_sec / 60, time_sec % 60))

def format_timedelta(timestamp):
    return("{}s ago".format((datetime.datetime.now() - timestamp).seconds))

def format_longest(longest):
    if longest:
        return("{} at {}".format(
            format_sec(
                longest[0]), format_timedelta(longest[1])))
    else:
        return("")
