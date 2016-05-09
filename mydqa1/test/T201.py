from apps.android.mobilesecurity import MobileSecurity
from testbase import TestBase


class C0000_Mobile_Security(TestBase):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Launch Mobile Security with multi-use token'

    def run(self):
        try:
            self.start()
            ms = MobileSecurity().prep(reinstall=True).startup()
            if ms.is_trial():
                raise Exception('Mobile Security is not installed with multi-use token')
            self.complete()
        except Exception as e:
            self.abend(e, take_log=True, take_screenshot=True)
            self.post_error()
        MobileSecurity().stop()
