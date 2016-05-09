# -*- coding: utf-8 -*-
import time
import os.path
import ui
from uiobject import UiObj
from config import settings
from helper import uiautomator, logger
from helper.android import android_device
from apps.app import App
from webviewapp import WebViewApp


class AndroidApp(App):
    def __init__(self, packbund, activity=None):
        App.__init__(self, packbund)
        self._activity = activity

    def prep(self, policy=None, reinstall=False):
        logger.debug('AndroidApp.prep: policy=%s, reinstall=%s' % (policy, reinstall))
        if self._packbund in settings.local.apk_files:
            if not android_device.is_app_installed(self._packbund) or reinstall is True or reinstall == 'always':
                apk_file = os.path.join(settings.local.apk_folder, settings.local.apk_files[self._packbund])
                if not android_device.install_app(self._packbund, apk_file, reinstall=True):
                    raise Exception('Failed to install app "%s" on device' % self._packbund)
        else:
            raise Exception('Unknown app %s to prepare' % self._packbund)
        return self

    def uninstall(self):
        android_device.uninstall_app(self._packbund)

    def initiate(self, activity=None, extras=None, restart=None):
        if not activity:
            activity = self._activity
        param = dict(packbund=self._packbund, activity=activity)
        if restart is not None:
            param['restart'] = restart
        if extras:
            param.update(extras)
        if not uiautomator.test('TestAppLaunch', param):
            raise Exception('Failed to launch App %s: %s' % (self._packbund, uiautomator.lasterror()))
        return self

    def startup_once(self, param=None):
        activity = param['activity'] if param and 'activity' in param else None
        extras = param['extras'] if param and 'extras' in param else None
        restart = param['restart'] if param and 'restart' in param else None
        return self.initiate(activity=activity, extras=extras, restart=restart)

    def startup(self, param=None):
        retry_count = 0
        retry_max = 2
        while retry_count < retry_max:
            try:
                self.startup_once(param=param)
                break
            except Exception as e:
                if retry_count >= retry_max - 1:
                    raise e
                logger.info(' > WARNING: Failed to launch app. Trying again with re-install.')
                self.prep(policy=None, reinstall=True)
                retry_count += 1
        return self

    def stop(self):
        if self._packbund:
            android_device.stop_app(self._packbund)
        return self

    def is_app_foreground(self):
        return UiObj('/*[@package=%s]' % self._packbund).wait_for_exists(App.TIMEOUT_LAUNCH)

    def wait_for_complete(self, timeout=App.TIMEOUT_AUTH):
        return UiObj('/ProgressBar[@package=%s]' % self._packbund).wait_until_gone(timeout)

    def app_chooser(self):
        olist = UiObj('/ListView[@package=android]')
        ogrid = UiObj('/GridView[@package=android]')
        alist = UiObj('/ListView[@package=%s]' % self._packbund)
        label = UiObj('/TextView[contains(@text,%s)]' % ui.WrapLib.get('Send data to'))
        elapsed = 0
        while elapsed < App.TIMEOUT_LAUNCH:
            if olist.exists():
                logger.debug('AndroidApp.app_chooser: Android ListView found')
                return olist
            if ogrid.exists():
                logger.debug('AndroidApp.app_chooser: Android GridView found')
                return ogrid
            if alist.exists() and label.exists():
                logger.debug('AndroidApp.app_chooser: Wrap Lib ListView found')
                return alist
            elapsed += 1
            time.sleep(1)
            logger.debug('AndroidApp.app_chooser: elapsed=%s' % elapsed)
        logger.debug('AndroidApp.app_chooser: No app chooser found')
        return None

    def openable(self, workspace=False, block=False, noapp=False, bypass=False, usable=None, unusable=None):
        errmsg = 'Error on sharing document'
        if UiObj('/TextView[@package=%s][contains(@text,"%s")]' % (self._packbund, ui.WrapLib.get('sharing is not allowed'))).exists() and UiObj('/Button[@text=%s]' % ui.WrapLib.get('Exit')).exists():
            if not block:
                raise Exception('%s: Sharing is unexpectedly blocked' % errmsg)
        else:
            if block:
                raise Exception('%s: Could not block sharing' % errmsg)
            if UiObj('/TextView[contains(@text,%s)]' % ui.WrapLib.get('There is no proper app to open the data')).exists():
                if not noapp:
                    raise Exception('%s: No app to share text' % errmsg)
                UiObj('/Button[@text=%s]' % ui.WrapLib.get('OK')).click()
            else:
                if noapp:
                    raise Exception('%s: No app is expected to be available' % errmsg)
                chooser = self.app_chooser()
                if chooser:
                    if bypass:
                        raise Exception('%s: App Chooser shows up unexpectedly' % errmsg)
                    if usable:
                        for app in usable:
                            if not chooser.find_app_chooser_text(app):
                                raise Exception('%s: App %s cannot be found in app chooser' % (errmsg, app))
                    if unusable:
                        for app in unusable:
                            if chooser.find_app_chooser_text(app):
                                raise Exception('%s: App %s is found in app chooser unexpectedly' % (errmsg, app))
                else:
                    if usable is not None and len(usable) > 1:
                        raise Exception('%s: App Choorse does NOT show up although two or more apps are supposed to be available' % errmsg)
        if self.is_android_error():
            raise Exception('%s: Android error' % errmsg)
        return self

    def open_with(self, app, workspace=False):
        chooser = self.app_chooser()
        if chooser:
            if not chooser.find_app_chooser_text(app, click=True):
                raise Exception('Failed to open the data with %s' % app)
        else:
            logger.debug('AndroidApp.open_with: No app chooser found --- probably the app has already started up')
        if self.is_android_error():
            raise Exception('Failed to open the data with %s: Android error' % app)
        return self

    def paste_from_prompt(self):
        return UiObj('/TextView[@package=%s][@text=%s]' % (self._packbund, ui.WrapLib.get('Paste From...')))

    def paste_from_clipboard(self, clipboard):
        if self.paste_from_prompt().wait_for_exists(3):
            if clipboard == 'none':
                raise Exception('Failed to paste text on App: Paste From dialog appears unexpectedly')
            if clipboard == 'stop':
                logger.debug('Paste operation is paused.')
            else:
                from_workspace = UiObj('/Button[@text=%s]' % ui.WrapLib.get('Workspace'))
                from_system = UiObj('/Button[@text=%s]' % ui.WrapLib.get('System'))
                if not from_workspace.exists() or not from_system.exists():
                    raise Exception('Failed to paste text on App: Buttons for System and/or Workspace do not exist')
                if clipboard == 'system':
                    from_system.click()
                elif clipboard == 'workspace':
                    from_workspace.click()
                else:
                    raise Exception('Failed to paste text on App: Unknown Paste From option %s' % clipboard)
        else:
            if clipboard == 'workspace' or clipboard == 'stop':
                raise Exception('Failed to paste text on App: Paste from dialog is not on screen')

    @staticmethod
    def is_android_error():
        return UiObj('/TextView[@package=android][contains(@text,%s)]' % ui.Android.get('Unfortunately')).exists()

    @staticmethod
    def hide_android_error():
        if AndroidApp.is_android_error():
            UiObj('/Button[@package=android][@text=%s]' % ui.Android.get('OK')).click()


class Chrome(AndroidApp, WebViewApp):
    def __init__(self):
        AndroidApp.__init__(self, packbund='com.android.chrome')
        self._name = 'Chrome'

    def is_page_up(self, *templates):
        time.sleep(5)
        return WebViewApp.is_page_up(self, *templates)
