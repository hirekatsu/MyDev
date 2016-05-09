# -*- coding: utf-8 -*-
import time
import ui
from uiobject import UiObj, click_clipboard_command
from helper import logger
from config import settings
from androidapp import AndroidApp
from wrapped import Wrapped
from webviewapp import WebViewApp


class TAoneCore(AndroidApp):
    def __init__(self, packbund):
        AndroidApp.__init__(self, packbund=packbund, activity='com.symantec.jdc.taoneapp.MainActivity')

    def is_main_page(self):
        return UiObj('/Button[@package=%s][@text="Copy text"]' % self._packbund).exists()

    def click_function(self, func):
        UiObj('/Button[@package=%s][@description=%s]' % (self._packbund, func)).click()
        return self

    def copy_text(self, text, block=False):
        errmsg = 'Failed to copy text on Test App'
        if not UiObj('/EditText[@package=%s][@description="Copying text:"]' % self._packbund).set_text(text):
            raise Exception('%s: EditText does not exist' % errmsg)
        if not UiObj('/Button[@text="Copy text"]').click():
            raise Exception('%s: Cannot click Copy button' % errmsg)
        if self.is_android_error():
            raise Exception('%s: Android error' % errmsg)
        if not self.is_app_foreground():
            raise Exception('%s: Eventually app is not on screen' % errmsg)
        return self

    def paste_text(self, clipboard='workspace', verify=None, block=False):
        errmsg = 'Failed to paste text on Test App'
        button = UiObj('/Button[@package=%s][@text="Paste text"]' % self._packbund)
        if not button.click():
            raise Exception('%s: No command button to paste' % errmsg)
        self.paste_from_clipboard('none')
        if UiObj('/TextView[@description=Result:]').get_text() != 'Success':
            raise Exception('%s: Failed to paste text due to any reason' % errmsg)
        if verify:
            self.verify_pasted_text(verify, block, errmsg)
        if self.is_android_error():
            raise Exception('%s: Android error' % errmsg)
        if not self.is_app_foreground():
            raise Exception('%s: Eventually app is not on screen' % errmsg)

        self.paste_text_from_menu(clipboard, verify, block)
        return self

    def paste_text_from_menu(self, clipboard='workspace', verify=None, block=False):
        errmsg = 'Failed to paste text via clipboard menu on Test App'
        edit = UiObj('/EditText[@package=%s][@description="Pasted text:"]' % self._packbund)
        edit.set_text('DUMMYTEXT')
        if not edit.select_text():
            raise Exception('%s: Cannot select text' % errmsg)
        if not click_clipboard_command(ui.Android.get('Paste')):
            raise Exception('%s: Cannot choose Paste on Clipboard commands' % errmsg)
        self.paste_from_clipboard(clipboard)
        if verify:
            self.verify_pasted_text(verify, block, errmsg)
        if self.is_android_error():
            raise Exception('%s: Android error' % errmsg)
        if not self.is_app_foreground():
            raise Exception('%s: Eventually app is not on screen' % errmsg)
        return self

    def select_paste_from(self, clipboard='workspace', verify=None, block=False):
        errmsg = 'Failed to paste text through Paste From dialog on Test App'
        if not self.paste_from_prompt().exists():
            raise Exception('%s: Paste From dialog does not exist' % errmsg)
        self.paste_from_clipboard(clipboard)
        if verify:
            self.verify_pasted_text(verify, block, errmsg)
        if self.is_android_error():
            raise Exception('%s: Android error' % errmsg)
        if not self.is_app_foreground():
            raise Exception('%s: Eventually app is not on screen' % errmsg)
        return self

    def verify_pasted_text(self, verify, block, errmsg):
        current = UiObj('/EditText[@description="Pasted text:"]').get_text()
        logger.debug('TAoneApp.paste_text: EditText.getText()=%s' % current)
        logger.debug('TAoneApp.paste_text: verify=%s' % verify)
        if current == verify:
            if block:
                raise Exception('%s: Text was pasted unexpectedly --- should NOT be pasted' % errmsg)
        else:
            if not block:
                raise Exception('%s: Text was NOT pasted successfully' % errmsg)

    def share_document(self, text):
        errmsg = 'Failed to share text on Test App'
        if not UiObj('/EditText[@package=%s][@description="Sharing text:"]' % self._packbund).set_text(text):
            raise Exception('%s: EditText does not exist' % errmsg)
        if not UiObj('/Button[@text="Share text"]').click():
            raise Exception('%s: Cannot click Share button' % errmsg)
        time.sleep(1)
        if self.is_android_error():
            raise Exception('%s: Android error' % errmsg)
        return self

    def receive_document(self, verify):
        errmsg = 'Failed to receive text on Test App'
        if UiObj('/TextView[@package=%s][@description=Result:]' % self._packbund).get_text() != 'Success':
            raise Exception('%s: Receive status is not SUCCESS' % errmsg)
        if verify:
            received = UiObj('/TextView[@description="Received text:"]').get_text()
            logger.debug('TAoneApp.receive_document: EditText.getText()=%s' % received)
            logger.debug('TAoneApp.receive_document: verify=%s' % verify)
            if received != verify:
                raise Exception('%s: Text was NOT received successfully' % errmsg)
        if self.is_android_error():
            raise Exception('%s: Android error' % errmsg)
        return self

    def browse_web(self, url):
        errmsg = 'Failed to open URL on Test App'
        if not UiObj('/EditText[@package=%s][@description="URL:"]' % self._packbund).set_text(url):
            raise Exception('%s: EditText does not exist' % errmsg)
        if not UiObj('/Button[@text="Open"]').click():
            raise Exception('%s: Cannot click Open button' % errmsg)
        time.sleep(1)
        if self.is_android_error():
            raise Exception('%s: Android error' % errmsg)
        return self

    def set_storage_mode(self, mode):
        mode_switch = {'appdata': 0, 'xstorage': 1, 'fullpath': 2}
        if mode in mode_switch:
            if not UiObj('/RadioButton[@package=%s][@instance=%s]' % (self._packbund, mode_switch[mode])).click():
                raise Exception('Storage operation on Test App: Cannot select mode %s' % mode)
        else:
            logger.debug('TAoneApp.set_storage_mode: storage mode kept unchanged.')

    def set_storage_path(self, path):
        if path:
            if not UiObj('/EditText[@package=%s][@instance=0]' % self._packbund).set_text(path):
                raise Exception('Storage operation on Test App: Cannot set path in EditText')
        else:
            logger.debug('TAoneApp.set_storage_path: storage path kept unchanged.')

    def get_storage_result(self):
        logger.debug('TAoneApp.get_storage_result')
        return UiObj('/TextView[@description=Result:]').get_text()

    def write_storage(self, mode=None, path=None, content='TEST', block=False):
        logger.debug('TAoneApp.write_storage: mode=%s, path=%s, content=%s, block=%s' % (mode, path, content, block))
        errmsg = 'Failed to write file on storage'
        self.set_storage_mode(mode)
        self.set_storage_path(path)
        if not UiObj('/EditText[@package=%s][@instance=1]' % self._packbund).set_text(content):
            raise Exception('%s: Cannot set content text in EditText' % errmsg)
        if not UiObj('/Button[@text=Write]').click():
            raise Exception('%s: Cannot click Write button' % errmsg)
        result = self.get_storage_result()
        if not block:
            if result != 'Success':
                raise Exception('%s: Error on writing file' % errmsg)
        else:
            if result.startswith('Failure'):
                if result.find('Permission denied') == -1:
                    raise Exception('%s: Write process failed, but not due to permission' % errmsg)
            else:
                raise Exception('%s: Writing to storage should be blocked with Permission Denied' % errmsg)
        if self.is_android_error():
            raise Exception('%s: Android error' % errmsg)
        if not self.is_app_foreground():
            raise Exception('%s: Eventually app is not on screen' % errmsg)
        return self

    def read_storage(self, mode=None, path=None, verify='TEST', block=False):
        logger.debug('TAoneApp.read_storage: mode=%s, path=%s, verify=%s, block=%s' % (mode, path, verify, block))
        errmsg = 'Failed to read file on storage'
        self.set_storage_mode(mode)
        self.set_storage_path(path)
        edit = UiObj('/EditText[@package=%s][@instance=1]' % self._packbund)
        if not edit.clear_text():
            raise Exception('%s: Cannot clear text in EditText' % errmsg)
        if not UiObj('/Button[@text=Read]').click():
            raise Exception('%s: Cannot click Read button' % errmsg)
        result = self.get_storage_result()
        if not block:
            if result != 'Success':
                raise Exception('%s: Error on reading file. %s' % (errmsg, result))
            if edit.get_text() != verify:
                raise Exception('%s: Read content does not match')
        else:
            if result == 'Success':
                raise Exception('%s: Could block from reading file' % errmsg)
        if self.is_android_error():
            raise Exception('%s: Android error' % errmsg)
        if not self.is_app_foreground():
            raise Exception('%s: Eventually app is not on screen' % errmsg)
        return self

    def delete_storage(self, mode=None, path=None, block=False):
        logger.debug('TAoneApp.delete_storage: mode=%s, path=%s, block=%s' % (mode, path, block))
        errmsg = 'Failed to delete file on storage'
        self.set_storage_mode(mode)
        self.set_storage_path(path)
        if not UiObj('/Button[@text=Delete]').click():
            raise Exception('%s: Cannot click Delete button' % errmsg)
        result = self.get_storage_result()
        if not block:
            if result != 'Success':
                raise Exception('%s: Error on deleting file. %s' % (errmsg, result))
        else:
            if result == 'Success':
                raise Exception('%s: Could block from deleting file' % errmsg)
        if self.is_android_error():
            raise Exception('%s: Android error' % errmsg)
        if not self.is_app_foreground():
            raise Exception('%s: Eventually app is not on screen' % errmsg)
        return self

    def get_external_dir(self):
        dir_info = dict(storageDir='', filesDir='')
        if not UiObj('/Button[@package=%s][@text=XStrgDir]' % self._packbund).click():
            raise Exception('Failed to get external directory path: Cannot click XStrgDir button')
        dir_info['storageDir'] = self.get_storage_result()
        if not UiObj('/Button[@package=%s][@text=XFileDir]' % self._packbund).click():
            raise Exception('Failed to get external directory path: Cannot click XFileDir button')
        dir_info['filesDir'] = self.get_storage_result()
        if self.is_android_error():
            raise Exception('Failed to get external directory path: Android error')
        return dir_info


class WrappedTAoneCore(Wrapped, TAoneCore, WebViewApp):
    def __init__(self, packbund, username=None, password=None):
        TAoneCore.__init__(self, packbund=packbund)
        self._username = username
        self._password = password
        self._key = packbund

    def receive_document(self, verify):
        self.login()
        TAoneCore.receive_document(self, verify)
        return self


class TAoneApp(WrappedTAoneCore):
    def __init__(self):
        WrappedTAoneCore.__init__(self,
                                  packbund='com.symantec.jdc.taoneapp',
                                  username=settings.server.username,
                                  password=settings.server.password)


class TAoneBuddy(WrappedTAoneCore):
    def __init__(self):
        WrappedTAoneCore.__init__(self,
                                  packbund='com.symantec.jdc.taonebuddy',
                                  username=settings.server.username,
                                  password=settings.server.password)


class TAoneUtil(TAoneCore):
    def __init__(self):
        TAoneCore.__init__(self,  packbund='com.symantec.jdc.taoneutil')
        self._name = 'TAoneUtil'
        self._temp = settings.local.out_path

