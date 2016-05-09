# -*- coding: utf-8 -*-
import os.path
import ui
from uiobject import UiObj
from helper import connection, logger
from helper.android import android_device as device
from config import settings
from androidapp import AndroidApp


class MobileSecurity(AndroidApp):
    def __init__(self):
        AndroidApp.__init__(self,
                            packbund='com.symantec.mobilesecurity',
                            activity='com.symantec.mobilesecurity.ui.g4.Startor')
        self._name = 'Norton Mobile Security'

    def prep(self, policy=None, reinstall=False):
        logger.debug('MobileSecurity.prep: reinstall=%s' % reinstall)
        apk_file = settings.local.nms_path
        if not os.path.exists(apk_file):
            logger.debug('MobileSecurity.prep: msn has not been downloaded yet')
            if not connection.download_nms(apk_file):
                raise Exception('Failed to download nms')
        if not device.install_app(self._packbund, apk_file, reinstall):
            raise Exception('Failed to install nms')
        return self

    def startup_once(self, param=None):
        AndroidApp.startup_once(self, param=param)
        button = UiObj('/Button[@package=%s][@text=%s]' % (self._packbund, ui.MobileSecurity.get('Agree & Launch')))
        if not button.click():
            raise Exception('Failed to start Mobile Security: No Agree & Launch button')
        title = UiObj('/TextView[@package=%s][@text=%s]' % (self._packbund, ui.MobileSecurity.get('Norton Mobile Security')))
        if not title.wait_for_exists(5 * 60):
            raise Exception('Failed to start Mobile Security: Mobile Security does not show up')
        if self.is_android_error():
            raise Exception('Failed to start Mobile Security: Android error')
        return self

    def is_trial(self):
        # index=4 is "About"
        button = UiObj('/HorizontalScrollView[@package=%s][@instance=0]/LinearLayout[@index=4]/ImageView[@index=0]' % self._packbund)
        if not button.click():
            raise Exception('Failed to switch pane on Mobile Security')
        if self.is_android_error():
            raise Exception('Failed to switch pane on Mobile Security: Android error')
        return UiObj('/Button[@package=%s][@text=%s]' % (self._packbund, ui.MobileSecurity.get('Buy Now'))).exists()
