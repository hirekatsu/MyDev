# -*- coding: utf-8 -*-
import time
from selenium.common.exceptions import NoSuchElementException
from helper import logger
from helper import appiummanager
from apps.app import App

class iOSApp(App):
    XP_APPLICATION = '//UIAApplication[1]'

    def __init__(self, packbund, path):
        App.__init__(self, packbund)
        self._path = path
        self._wd = None

    def ipapath(self):
        return self._path

    def find_element(self, xpath, text=None):
        logger.debug('iOSApp.find_element: xpath=%s, text=%s' % (xpath, text))
        try:
            we = self._wd.find_element_by_xpath(xpath)
            if we:
                logger.debug('id: %s, text: %s' % (we.id, we.text))
            if we is not None and text is not None and we.text != text:
                we = None
        except NoSuchElementException as e:
            we = None
        return we

    def find_element_until(self, xpath, text=None, timeout=App.TIMEOUT_LAUNCH_MS):
        logger.debug('iOSApp.find_element_until: xpath=%s, text=%s, timeout=%s' % (xpath, text, timeout))
        elapsed = 0
        while elapsed < timeout:
            we = self.find_element(xpath, text)
            if we:
                return we
            time.sleep(0.5)
            elapsed += 500
            logger.debug('iOSApp.find_element_until: elapsed=%s' % elapsed)
        return None

    def prep(self, reinstall=False):
        logger.debug('iOSApp.prep: reinstall=%s' % reinstall)
        if reinstall:
            try:
                self.initiate()
                self._wd.remove_app(self._packbund)
                self.stop()
            except Exception as e:
                if not appiummanager.is_launch_failure(self._packbund):
                    raise e

    def initiate(self, port=None):
        self._wd = appiummanager.start_driver(self._packbund, path=self.ipapath(), port=port)
        return self

    def stop(self):
        if self._wd:
            self._wd.close_app()
            appiummanager.stop_driver(self._wd)
            self._wd = None
        return self
