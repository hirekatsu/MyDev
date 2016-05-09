# -*- coding: utf-8 -*-
import time
import os.path
import ui
from uiobject import UiObj
from config import settings
from helper import uiautomator, connection, logger
from helper.android import android_device as device
from androidapp import AndroidApp
from apps.android import uninstall_wrapped_apps


class WorkHubCore(AndroidApp):
    def __init__(self, packbund, username=None, password=None):
        AndroidApp.__init__(self, packbund)
        self._username = username
        self._password = password

    def prep(self, policy=None, reinstall=False):
        logger.debug('WorkHubCore.prep: reinstall=%s' % reinstall)
        apk_file = settings.local.android_workhub_path
        if not os.path.exists(apk_file):
            logger.debug('WorkHubCore.prep: workhub has not been downloaded yet')
            if not connection.download_workhub('android', apk_file):
                raise Exception('Failed to download workhub')
        if not device.install_app(connection.workhub_packbund(), apk_file, reinstall):
            raise Exception('Failed to install workhub')
        return self

    def reset(self, startup=False):
        logger.debug('WorkHubCore.reset: startup=%s' % startup)
        uninstall_wrapped_apps()
        self.prep(reinstall=True)
        if startup:
            self.startup()
            device.send_key(device.KEY_HOME)
        return self

    def initiate(self, restart=None):
        param = dict(packbund=self._packbund,
                     activity='com.nukona.installer.activity.LoginActivity')
        if restart:
            param['restart'] = restart
        if not uiautomator.test('TestAppLaunch', param):
            raise Exception(self.__class__, 'Failed to launch Work Hub: %s' % uiautomator.lasterror())
        return self

    def is_signin_prompted(self):
        logger.debug('WorkHubCore.is_signin_prompted: starting...')
        time.sleep(1)  # waiting for a while
        button = UiObj('/Button[@package=%s][@text=%s]' % (self._packbund, ui.WorkHub.get('Sign In')))
        edit = UiObj('/EditText[@instance=0]')
        for rr in range(0, 10):
            if not button.exists() or not edit.exists():
                break
            if edit.is_enabled():
                logger.debug('WorkHubCore.is_signin_prompted: Button and EditText exist and EditText is enabled.')
                return True
            logger.debug('WorkHubCore.is_signin_prompted: Waiting for EditText enabled for another 3 seconds (%s)' % (rr + 1))
            time.sleep(3)
        return False

    def signin(self, username=None, password=None):
        logger.debug('WorkHubCore.signin: username=%s, password=%s' % (username, password))
        if not username:
            username = self._username
        if not password:
            password = self._password

        if self.is_signin_prompted():
            if not UiObj('/EditText[@instance=0]').set_text(username.decode(), hint=ui.WorkHub.get('User Name')):
                raise Exception('Failed to sign in to Work Hub: Username input')
            if not UiObj('/EditText[@instance=1]').set_text(password.decode(), hint=ui.WorkHub.get('Password')):
                raise Exception('Failed to sign in to Work Hub: Password input')
            if not UiObj('/Button[@text=%s]' % ui.WorkHub.get('Sign In')).click():
                raise Exception('Failed to sign in to Work Hub: Sign-in click')
            if not self.wait_for_complete():
                raise Exception('Failed to sign in to Work Hub: Timeout after entering credential')
            if UiObj('/TextView[@package=%s][@text=%s]' % (self._packbund, ui.WorkHub.get('Device Ownership'))).exists():
                if not UiObj('/RadioButton[@text=%s]' % ui.WorkHub.get('No')).click():
                    raise Exception('Failed to sign in to Work Hub: Device Ownership option selection')
                if not UiObj('/Button[@text=%s]' % ui.WorkHub.get('Continue')).click():
                    raise Exception('Failed to sign in to Work Hub: Device Ownership continue')
                if not self.wait_for_complete():
                    raise Exception('Failed to sign in to Work Hub: Timeout after choosing device ownership')
            errmsg = UiObj('/TextView[@package=%s][@text="%s"]' % (self._packbund,
                                                                    ui.WorkHub.get('An error occurred during sign in')))
            if errmsg.exists():
                raise Exception('Failed to sign in to Work Hub: Sign-in error')
            if self.is_signin_prompted():
                raise Exception('Failed to sign in to Work Hub: Unknown error, sign-in is still being prompted')
            if not self.wait_for_complete():
                raise Exception('Failed to sign in to Work Hub: Timeout after signing')

        if self.is_android_error():
            raise Exception('Failed to sign in to Work Hub: Android error')
        return self

    def is_workspace_request_prompted(self):
        title = UiObj('/TextView[@package=%s][contains(@text,%s)]' % (self._packbund,
                                                                      ui.WorkHub.get('requesting to join WorkSpace')))
        if not title.exists():
            return False
        if not UiObj('/Button[@text=%s]' % ui.WorkHub.get('Allow')).exists():
            return False
        if not UiObj('/Button[@text=%s]' % ui.WorkHub.get('Deny')).exists():
            return False
        return True

    def allow_workspace_request(self):
        self.signin()
        if self.is_workspace_request_prompted():
            if not UiObj('/Button[@text=%s]' % ui.WorkHub.get('Allow')).click():
                raise Exception('Failed to allow Workspace request: Error on selecting Allow button')
            if not self.wait_for_complete():
                raise Exception('Failed to allow Workspace request: Timeout after allowing')
        if self.is_android_error():
            raise Exception('Failed to allow Workspace request: Android error')
        return self

    def is_home_page(self):
        if not UiObj('/TextView[@package=%s][@text=%s]' % (self._packbund, ui.WorkHub.get('Home'))).exists():
            return False
        if not UiObj('/ImageButton').exists() and not UiObj('/ImageView').exists():
            return False
        return True

    def startup_once(self, param=None):
        restart = param['restart'] if param and 'restart' in param else None
        self.initiate(restart=restart)
        username = param['username'] if param and 'username' in param and param['username'] else self._username
        password = param['password'] if param and 'password' in param and param['password'] else self._password
        self.signin(username, password)
        if not self.is_home_page():
            raise Exception('Work Hub Home is not on screen: %s' % uiautomator.lasterror())
        return self


class WorkHub(WorkHubCore):
    def __init__(self):
        WorkHubCore.__init__(self,
                             packbund=connection.workhub_packbund(),
                             username=settings.server.username,
                             password=settings.server.password)
