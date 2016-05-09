import time
import ui
from helper import logger
from apps.ios.iosapp import iOSApp


class WorkHub(iOSApp):
    XP_SIGNIN_USERNAME = '//UIAApplication[1]/UIAWindow[1]/UIAScrollView[1]/UIATextField[1]'
    XP_SIGNIN_PASSWORD = '//UIAApplication[1]/UIAWindow[1]/UIAScrollView[1]/UIASecureTextField[1]'
    XP_SIGNIN_BUTTON = '//UIAApplication[1]/UIAWindow[1]/UIAScrollView[1]/UIAButton[3]'
    XP_NAVIGATION_BACK = '//UIAApplication[1]/UIAWindow[1]/UIANavigationBar[1]/UIAButton[1]'

    def __init__(self, packbund, path, username=None, password=None):
        iOSApp.__init__(self, packbund, path)
        self._username = username
        self._password = password

    def is_signin_prompted(self):
        time.sleep(1)
        return self.find_element_until(self.XP_SIGNIN_BUTTON, text=ui.workhub['Sign In']) is not None

    def signin(self, username=None, password=None):
        if self.is_signin_prompted():
            if not username:
                username = self._username
            if not password:
                password = self._password
            e1 = self.find_element(self.XP_SIGNIN_USERNAME)
            if not e1:
                raise Exception('No username box on Work Hub Sign-In page')
            e1.clear()
            e1.send_keys(username)
            self.find_element(self.XP_SIGNIN_PASSWORD).send_keys(password)
            self.find_element(self.XP_SIGNIN_BUTTON).click()
            time.sleep(5)
        return self

    def is_home_page(self):
        return self.find_element_until(self.XP_NAVIGATION_BACK,
                                       text='iOS6SidebarReveal',
                                       timeout=self.AUTH_TIMEOUT) is not None

    def startup(self, username=None, password=None):
        for i in range(0, 5):
            logger.debug('WorkHub.startup: try=%s' % i)
            self.initiate()
            self.signin(username, password)
            if not self.is_frozen():
                if not self.is_home_page():
                    raise Exception('Work Hub Home is not on screen')
                return self
            self.stop()
        raise Exception('Work Hub freezes after startup')

    def is_frozen(self):
        we = self.find_element(self.XP_APPLICATION)
        return True if we is None or not we.is_displayed() else False
