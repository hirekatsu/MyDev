import config
from config import argument
import sys
import traceback

try:
    config.initiate_ios(argument.init_parser().parse_args())
    import time
    time.sleep(10)

    from apps.ios.myapps import MyWorkHub
    wh = MyWorkHub().prep().startup()
    print 'SUCCESS'
    time.sleep(10)
    wh.stop()

    print 'STOPPED'
    wh.startup()
    print 'SUCCESS (2)'
    time.sleep(10)


except Exception as e:
    exc_type, exc_value, exc_tb = sys.exc_info()
    print traceback.format_exception(exc_type, exc_value, exc_tb)
finally:
    config.terminate_ios()