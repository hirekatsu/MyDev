# -*- coding: utf-8 -*-
from apps.android.workweb import WorkWeb
from apps.android.workmail import WorkMail
from apps.android.taoneapp import TAoneApp
from apps.android.androidapp import Chrome
from helper.android import android_device as device
from testbase import TestBase


class C0000_Browser_Apps(TestBase):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Launch Work Web to register in workspace and check Chrome installed'

    def run(self):
        status = True
        try:
            self.start()
            WorkWeb().prep('xTA - default').startup(param=dict(to_bookmarks=False))
            if not device.is_app_installed(Chrome().packbund()):
                raise Exception('Chrome is not installed on the device')
            self.complete()
        except Exception as e:
            self.abend(e, take_log=True, take_screenshot=True)
            self.post_error()
            status = False
        WorkWeb().stop()
        return status


class C0001_Browse_WorkMail_All_With_WorkWeb(TestBase):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Browse Web site from Work Mail (browser_preference=system) with Work Web'
        self._dependencies.append('T033.C0000_Browser_Apps')

    def run(self):
        try:
            self.start()
            wa = WorkMail().prep('xTA - default').startup(param=dict(extras=dict(do='openurl')))
            wa.browse_web(url='http://m.symantec.com')
            wa.openable(workspace=False, block=False, usable=['Work Web', 'Chrome'])
            wa.open_with(app='Work Web', workspace=False)
            if not WorkWeb().login().is_page_up('symantec_logo'):
                raise Exception('Failed to open URL with Work Web')
            self.complete()
        except Exception as e:
            self.abend(e, take_log=True, take_screenshot=True)
            self.post_error()
        WorkWeb().stop()
        WorkMail().stop()


class C0002_Browse_WorkMail_All_With_Unwrapped(TestBase):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Browse Web site from Work Mail (browser_preference=system) with Unwrapped App'
        self._dependencies.append('T033.C0000_Browser_Apps')

    def run(self):
        try:
            self.start()
            wa = WorkMail().prep('xTA - default').startup(param=dict(extras=dict(do='openurl')))
            wa.browse_web(url='http://m.symantec.com')
            wa.openable(workspace=False, block=False, usable=['Work Web', 'Chrome'])
            wa.open_with(app='Chrome', workspace=False)
            if not Chrome().is_page_up('symantec_logo'):
                raise Exception('Failed to open URL with Chrome')
            self.complete()
        except Exception as e:
            self.abend(e, take_log=True, take_screenshot=True)
            self.post_error()
        Chrome().stop()
        WorkMail().stop()


class C0021_Browse_WrappedApp_All_With_WorkWeb(TestBase):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Browse Web site from Wrapped App (browser_preference=system) with Work Web'
        self._dependencies.append('T033.C0000_Browser_Apps')

    def run(self):
        try:
            self.start()
            wa = TAoneApp().prep('xTA - default').startup(param=dict(extras=dict(do='openurl')))
            wa.browse_web(url='http://m.symantec.com')
            wa.openable(workspace=False, block=False, usable=['Work Web', 'Chrome'])
            wa.open_with(app='Work Web', workspace=False)
            if not WorkWeb().login().is_page_up('symantec_logo'):
                raise Exception('Failed to open URL with Work Web')
            self.complete()
        except Exception as e:
            self.abend(e, take_log=True, take_screenshot=True)
            self.post_error()
        WorkWeb().stop()
        TAoneApp().stop()


class C0022_Browse_WrappedApp_All_With_Unwrapped(TestBase):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Browse Web site from Wrapped App (browser_preference=system) with Unwrapped App'
        self._dependencies.append('T033.C0000_Browser_Apps')

    def run(self):
        try:
            self.start()
            wa = TAoneApp().prep('xTA - default').startup(param=dict(extras=dict(do='openurl')))
            wa.browse_web(url='http://m.symantec.com')
            wa.openable(workspace=False, block=False, usable=['Work Web', 'Chrome'])
            wa.open_with(app='Chrome', workspace=False)
            if not Chrome().is_page_up('symantec_logo'):
                raise Exception('Failed to open URL with Chrome')
            self.complete()
        except Exception as e:
            self.abend(e, take_log=True, take_screenshot=True)
            self.post_error()
        Chrome().stop()
        TAoneApp().stop()


class C0101_Browse_WorkMail_WS_With_WorkWeb(TestBase):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Browse Web site from Work Mail (browser_preference=workspace) with Work Web'
        self._dependencies.append('T033.C0000_Browser_Apps')

    def run(self):
        try:
            self.start()
            wa = WorkMail().prep('xTA - browser - workspace').startup(param=dict(extras=dict(do='openurl')))
            wa.browse_web(url='http://m.symantec.com')
            wa.openable(workspace=True, block=False, bypass=True, usable=['Work Web'], unusable=['Chrome'])
            if not WorkWeb().login().is_page_up('symantec_logo'):
                raise Exception('Failed to open URL with Work Web')
            self.complete()
        except Exception as e:
            self.abend(e, take_log=True, take_screenshot=True)
            self.post_error()
        WorkWeb().stop()
        WorkMail().stop()


class C0121_Browse_WrappedApp_WS_With_WorkWeb(TestBase):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Browse Web site from Wrapped App (browser_preference=workspace) with Work Web'
        self._dependencies.append('T033.C0000_Browser_Apps')

    def run(self):
        try:
            self.start()
            wa = TAoneApp().prep('xTA - browser - workspace').startup(param=dict(extras=dict(do='openurl')))
            wa.browse_web(url='http://m.symantec.com')
            wa.openable(workspace=True, block=False, bypass=True, usable=['Work Web'], unusable=['Chrome'])
            if not WorkWeb().login().is_page_up('symantec_logo'):
                raise Exception('Failed to open URL with Work Web')
            self.complete()
        except Exception as e:
            self.abend(e, take_log=True, take_screenshot=True)
            self.post_error()
        TAoneApp().stop()
        WorkWeb().stop()


class C0201_Browse_WorkMail_WS_With_None(TestBase):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Browse Web site from Work Mail (browser_preference=workspace) but no app to open'

    def run(self):
        try:
            self.start()
            WorkWeb().uninstall()
            wa = WorkMail().prep('xTA - browser - workspace').startup(param=dict(extras=dict(do='openurl')))
            wa.browse_web(url='http://m.symantec.com')
            wa.openable(workspace=True, block=False, noapp=True, unusable=['Work Web', 'Chrome'])
            self.complete()
        except Exception as e:
            self.abend(e, take_log=True, take_screenshot=True)
            self.post_error()
        WorkMail().stop()


class C0221_Browse_WrappedApp_WS_With_None(TestBase):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Browse Web site from Work Mail (browser_preference=workspace) but no app to open'

    def run(self):
        try:
            self.start()
            WorkWeb().uninstall()
            wa = TAoneApp().prep('xTA - browser - workspace').startup(param=dict(extras=dict(do='openurl')))
            wa.browse_web(url='http://m.symantec.com')
            wa.openable(workspace=True, block=False, noapp=True, unusable=['Work Web', 'Chrome'])
            self.complete()
        except Exception as e:
            self.abend(e, take_log=True, take_screenshot=True)
            self.post_error()
        TAoneApp().stop()
