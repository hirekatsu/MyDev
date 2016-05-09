# -*- coding: utf-8 -*-
import time
from config import settings
from helper import logger, connection
from helper.android import android_device as device
from apps.android.uiobject import UiObj
from apps.android import ui
from androidapp import AndroidApp


class Wrapped(AndroidApp):
    def __init__(self, packbund, activity=None, username=None, password=None):
        AndroidApp.__init__(self, packbund=packbund, activity=activity)
        self._username = username
        self._password = password

    def prep(self, policy=None, reinstall=False):
        logger.debug('Wrapped.prep: policy=%s, reinstall=%s' % (policy, reinstall))
        if self._key in settings.info.apps:
            if not connection.assure_app(self._key, policy):
                raise Exception('Failed to prepare app "%s" on server' % self._key)
            self._packbund = settings.info.apps[self._key]['metadata']['bundle-identifier']
            do_install = reinstall is True or reinstall == 'always'
            policy_changed = settings.info.apps[self._key]['policy_changed'] is True
            if not device.is_app_installed(self._packbund) or do_install or policy_changed:
                apk_file = connection.download_app(self._key, settings.tempfile(self._packbund + '.apk'))
                if not apk_file:
                    raise Exception('Failed to download app "%s" from server' % self._key)
                if not device.install_app(self._packbund, apk_file, reinstall=True):
                    raise Exception('Failed to install app "%s" (%s) on device' % (self._key, self._packbund))
            self._name = settings.info.apps[self._key]['name']
        else:
            raise Exception('Unknown app %s to prepare' % self._key)
        return self

    def is_login_prompted(self, retry_at_network_issue=5):
        logger.debug('Wrapped.is_login_prompted: retry_at_network_issue=%s' % retry_at_network_issue)
        time.sleep(1)
        retry = 0
        while retry <= retry_at_network_issue:
            if not self.wait_for_complete():
                raise Exception('Failed login prompt: Timeout before login prompt appears')
            if not UiObj('/TextView[@package=%s][@text=%s]' % (self._packbund, ui.WrapLib.get('Network Issue'))).exists():
                if not UiObj('/TextView[@package=%s][@text=%s]' % (self._packbund, ui.WrapLib.get('Username:'))).exists():
                    return False
                if not UiObj('/TextView[@text=%s]' % ui.WrapLib.get('Password:')).exists():
                    return False
                if not UiObj('/Button[@text=%s]' % ui.WrapLib.get('Login')).exists():
                    return False
                return True
            if retry < retry_at_network_issue:
                if not UiObj('/TextView[@text=%s]' % ui.WrapLib.get('Retry')).click():
                    raise Exception('Failed login prompt: Error on retrying at Network Issue')
            retry += 1
        raise Exception('Failed login prompt: Continuous Network Issue')

    def login(self, username=None, password=None, negative=False):
        if not username:
            username = self._username
        if not password:
            password = self._password

        if not self.is_login_prompted():
            return self
        retry = 0
        retry_on_error = 4
        while retry <= retry_on_error:
            UiObj('/EditText[@instance=0]').set_text(username)
            UiObj('/EditText[@instance=1]').set_text(password)
            UiObj('/Button[@text=%s]' % ui.WrapLib.get('Login')).click()
            if not self.wait_for_complete():
                raise WrappedLoginException('Failed to login: Timeout after entering credential')
            early_failure = self.is_login_failed(hide=False)
            errmsg2 = UiObj('/TextView[@package=%s][contains(@text,%s)]' % (self._packbund,
                                                                            ui.WrapLib.get('in the input box to continue')))
            if early_failure or errmsg2.exists():
                if negative:
                    return self  # success
                logger.debug('Wrapped.login: Login failed due to unknown reason.')
                if retry >= retry_on_error:
                    break
                logger.debug('Wrapped.login: Retrying @ %s' % (retry + 1))
                if not early_failure:
                    UiObj('/EditText[@instance=0]').set_text('continue')
                UiObj('/Button[@text=%s' % ui.WrapLib.get('OK')).click()
            elif self.is_android_error():
                logger.debug('Wrapped.login: Android error.')
                if retry >= retry_on_error:
                    break
                self.hide_android_error()
                if not self.is_login_prompted():
                    raise WrappedLoginException('Failed to login: Unexpected Android error with no login prompt any longer')
                logger.info(' > WARNING: Android error on login -- retrying @ %s' % (retry + 1))
            else:
                if negative:
                    raise WrappedLoginException('Failed to login: Login was expected to fail but succeeded')
                return self  # success
            retry += 1
        raise WrappedLoginException('Finally failed to login due to unknown reason')

    def is_login_failed(self, hide=True):
        errmsg = UiObj('/TextView[@package=%s][contains(@text,%s)]' % (self._packbund,
                                                                       ui.WrapLib.get('Authentication failed')))
        if not errmsg.exists():
            return False
        if hide:
            UiObj('/Button[@text=%s]' % ui.WrapLib.get('OK')).click()
        return True

    def startup_once(self, param=None):
        AndroidApp.startup_once(self, param=param)
        if param and 'login_required' in param and param['login_required'] == True:
            if not self.is_login_prompted():
                raise Exception('Login is not prompted')
        username = param['username'] if param and 'username' in param and param['username'] else self._username
        password = param['password'] if param and 'password' in param and param['password'] else self._password
        self.login(username, password)
        return self


class WrappedLoginException(Exception):
    pass

