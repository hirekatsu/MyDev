import time

from apps.android.workweb import WorkWeb
from apps.android.workmail import WorkMail
from apps.android.taoneapp import TAoneApp, TAoneUtil
from apps.android.swa import TWText
from helper import settings, logger
from helper.android import android_device
from testbase import TestBase


class C0001_Auth_Required_WorkWeb(TestBase):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Authentication required on Work Web startup'

    def run(self):
        try:
            self.start()
            WorkWeb().prep(policy='xTA - default', reinstall=True).startup(param=dict(login_required=True))
            self.complete()
        except Exception as e:
            self.abend(e, take_log=True, take_screenshot=True)
            self.post_error()
        WorkWeb().stop()


class C0002_Auth_Required_SWA(TestBase):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Authentication required on Secure Web App startup'

    def run(self):
        try:
            self.start()
            wa = TWText().prep(policy='xTA - default', reinstall=True).startup(param=dict(login_required=True))
            if not wa.is_page_up('symc_logo'):
                raise Exception('Secure Web App main page does not show up')
            self.complete()
        except Exception as e:
            self.abend(e, take_log=True, take_screenshot=True)
            self.post_error()
        TWText().stop()


class C0003_Auth_Required_WrappedApp(TestBase):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Authentication required on Wrapped Native App startup'

    def run(self):
        try:
            self.start()
            wa = TAoneApp().prep(policy='xTA - default', reinstall=True).startup(param=dict(login_required=True))
            if not wa.is_main_page():
                raise Exception('Native App main page does not show up')
            self.complete()
        except Exception as e:
            self.abend(e, take_log=True, take_screenshot=True)
            self.post_error()
        TAoneApp().stop()


class C0101_Auth_Timeout_One_Minute_WorkMail(TestBase):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Re-authentication required (re-auth = 1 minute) on Work Mail'

    def run(self):
        try:
            self.start()
            ua = TAoneUtil().prep()
            wa = WorkMail().prep('xTA - reauth - one minute').startup()
            android_device.send_key(android_device.KEY_HOME)
            ua.startup()
            logger.info('Waiting one-minute idle time...')
            time.sleep(60)
            wa.initiate(restart=False)
            wa.switch_pane('email')
            if not wa.is_login_prompted():
                raise Exception('Login is NOT prompted unexpectedly after one-minute idle time')
            self.complete()
        except Exception as e:
            self.abend(e, take_log=True, take_screenshot=True)
            self.post_error()
        WorkMail().stop()
        TAoneUtil().stop()


class C0103_Auth_Timeout_One_Minute_WrappedApp(TestBase):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Re-authentication required (re-auth = 1 minute) on Wrapped Native App'

    def run(self):
        try:
            self.start()
            ua = TAoneUtil().prep()
            wa = TAoneApp().prep('xTA - reauth - one minute').startup()
            android_device.send_key(android_device.KEY_HOME)
            ua.startup()
            logger.info('Waiting one-minute idle time...')
            time.sleep(60)
            wa.initiate(restart=False)
            wa.click_function('copytext2')
            if not wa.is_login_prompted():
                raise Exception('Login is NOT prompted unexpectedly after one-minute idle time')
            self.complete()
        except Exception as e:
            self.abend(e, take_log=True, take_screenshot=True)
            self.post_error()
        TAoneApp().stop()
        TAoneUtil().stop()


class C0111_Auth_Not_Timeout_WorkMail(TestBase):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Re-authentication not required (re-auth disabled) on Work Mail'

    def run(self):
        try:
            self.start()
            ua = TAoneUtil().prep()
            wa = WorkMail().prep('xTA - default').startup()
            android_device.send_key(android_device.KEY_HOME)
            ua.startup()
            logger.info('Waiting one-minute idle time...')
            time.sleep(60)
            wa.initiate(restart=False)
            wa.switch_pane('email')
            if wa.is_login_prompted():
                raise Exception('Login is prompted unexpectedly after one-minute idle time')
            self.complete()
        except Exception as e:
            self.abend(e, take_log=True, take_screenshot=True)
            self.post_error()
        WorkMail().stop()
        TAoneUtil().stop()


class C0113_Auth_Not_Timeout_WrappedApp(TestBase):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Re-authentication not required (re-auth disabled) on Wrapped Native App'

    def run(self):
        try:
            self.start()
            ua = TAoneUtil().prep()
            wa = TAoneApp().prep('xTA - default').startup()
            android_device.send_key(android_device.KEY_HOME)
            ua.startup()
            logger.info('Waiting one-minute idle time...')
            time.sleep(60)
            wa.initiate(restart=False)
            wa.click_function('copytext2')
            if wa.is_login_prompted():
                raise Exception('Login is prompted unexpectedly after one-minute idle time')
            self.complete()
        except Exception as e:
            self.abend(e, take_log=True, take_screenshot=True)
            self.post_error()
        TAoneApp().stop()
        TAoneUtil().stop()


class C9003_Auth_Attempt_With_Wrong_Password_Five_Times_WrappedApp(TestBase):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = '''Attempt to log in to Wrapped Native App with wrong password five times.
No password lockout or "type to continue" message is expected.'''

    def run(self):
        try:
            self.start()
            wa = TAoneApp().prep('xTA - default').initiate()
            for retry in range(0, 5):
                logger.debug('login retry=%s' % retry)
                wa.login(password=settings.server.password + 'wrong', negative=True)
                if not wa.is_login_failed(hide=True):
                    raise Exception('No other messages expected but "Authentication Failed"')
            self.complete()
        except Exception as e:
            self.abend(e, take_log=True, take_screenshot=True)
            self.post_error()
        TAoneApp().stop()
