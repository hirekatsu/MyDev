# -*- coding: utf-8 -*-
import re
import time
import json

import ui
from helper import uiautomator, logger
from helper.android import android_device


class UiObj():
    def __init__(self, path):
        if isinstance(path, unicode):
            path = path.encode('utf-8', 'ignore')
        self._path = path

    def get_child(self, path):
        return UiObj(self._path + path)

    def exists(self):
        logger.debug('UiObj.exists: path=%s' % self._path)
        return uiautomator.test('TestUiObject', dict(path=self._path, action='Exists'))

    def is_enabled(self):
        logger.debug('UiObj.is_enabled: path=%s' % self._path)
        result = self.get_result('IsEnabled')
        return (result == 'true') if result is not None else False

    def get_text(self):
        logger.debug('UiObj.get_text: path=%s' % self._path)
        return self.get_result('GetText')

    def set_text(self, text, hint=None):
        if isinstance(text, unicode):
            text = text.encode('utf-8', 'ignore')
        if hint and isinstance(hint, unicode):
            hint = hint.encode('utf-8', 'ignore')
        logger.debug('UiObj.set_text: path=%s, text=%s, hint=%s' % (self._path, text, hint))
        current = self.get_text()
        logger.debug('UiObj.set_text: current text: %s' % current)
        if current != text:
            if current != '' and current != hint:
                self.clear_text(hint)
            return uiautomator.test('TestUiObject', dict(path=self._path, action='SetText', text=text))
        return True

    def clear_text(self, hint=None):
        if hint and isinstance(hint, unicode):
            hint = hint.encode('utf-8', 'ignore')
        logger.debug('UiObj.clear_text: path=%s, hint=%s' % (self._path, hint))
        if not uiautomator.test('TestUiObject', dict(path=self._path, action='ClearTextField')):
            return False
        text = self.get_text()
        logger.debug('UiObj.clear_text: text after ClearTextField: %s' % text)
        if text != '':
            if hint is None or text != hint:
                if self.select_text():
                    android_device.send_key(android_device.KEY_DEL)
        return True

    def select_text(self):
        logger.debug('UiObj.select_text: path=%s' % self._path)
        if not select_text_for_clipboard_command(self._path):
            return False
        return click_clipboard_command(ui.Android.get('Select all'))

    def get_content_description(self):
        logger.debug('UiObj.get_content_description: path=%s' % self._path)
        return self.get_result('GetContentDescription')

    def click(self):
        logger.debug('UiObj.click: path=%s' % self._path)
        return uiautomator.test('TestUiObject', dict(path=self._path, action='Click'))

    def click_topleft(self):
        logger.debug('UiObj.click_topleft: path=%s' % self._path)
        return uiautomator.test('TestUiObject', dict(path=self._path, action='ClickTopLeft'))

    def click_at(self, x, y):
        logger.debug('UiObj.click_at: path=%s, x=%s, y=%s' % (self._path, x, y))
        return uiautomator.test('TestUiObject', dict(path=self._path, action='ClickAt', x=x, y=y))

    def get_bounds(self):
        logger.debug('UiObj.get_bounds: path=%s' % self._path)
        result = self.get_result('GetBounds')
        if not result:
            return dict(top=0, left=0, bottom=0, right=0, width=0, height=0)
        return json.loads(result)

    def wait_for_exists(self, timeout):
        logger.debug('UiObj.wait_for_exists: path=%s, timeout=%s' % (self._path, timeout))
        result = uiautomator.test('TestUiObject',
                                  dict(path=self._path,
                                       action='WaitForExists',
                                       timeout=(timeout * 1000)))
        logger.debug('UiObj.wait_until_gone: result=%s' % result)
        return result

    def wait_until_gone(self, timeout):
        logger.debug('UiObj.wait_until_gone: path=%s, timeout=%s' % (self._path, timeout))
        result = uiautomator.test('TestUiObject',
                                  dict(path=self._path,
                                       action='WaitUntilGone',
                                       timeout=(timeout * 1000)))
        logger.debug('UiObj.wait_until_gone: result=%s' % result)
        return result

    def dump_ui_objects(self, retry=0):
        logger.debug('UiObj.dump_ui_objects: path=%s, retry=%s' % (self._path, retry))
        uiautomator.test('TestUiObject', dict(path=self._path, action='DumpUiObjects', retry=retry))

    def find_app_chooser_text(self, text, click=False):
        if isinstance(text, unicode):
            text = text.encode('utf-8', 'ignore')
        logger.debug('UiObj.find_app_chooser_text: path=%s, text=%s, click=%s' % (self._path, text, click))
        return uiautomator.test('TestUiObject', dict(path=self._path, action='FindAppChooserText', text=text, click=click))

    def get_result(self, action, param={}):
        param['path'] = self._path
        param['action'] = action
        if not uiautomator.test('TestUiObject', param):
            return None
        match = re.search(r'^TestUiObject.RESULT:(.*)', uiautomator.lastout(), flags=re.MULTILINE)
        if not match:
            return None
        logger.debug('UiObj.get_result: result=%s' % match.group(1))
        return match.group(1)


def select_text_for_clipboard_command(path):
    if isinstance(path, unicode):
        path = path.encode('utf-8', 'ignore')
    logger.debug('uiobject.select_text_for_clipboard_command: path=%s' % path)
    # long click
    logger.debug('uiobject.select_text_for_clipboard_command: long-clicking...')
    if uiautomator.test('TestUiObject', dict(path=path, action='LongClick')):
        if clipboard_command_exists():
            return True
    # long click at top left
    logger.debug('uiobject.select_text_for_clipboard_command: long-clicking at top left...')
    if uiautomator.test('TestUiObject', dict(path=path, action='LongClickTopLeft')):
        if clipboard_command_exists():
            return True
    # long click emulated by swipe
    logger.debug('uiobject.select_text_for_clipboard_command: long-clicking by swipe...')
    if uiautomator.test('TestUiObject', dict(path=path, action='Swipe',
                                             startx=15, starty=15, endx=15, endy=15, steps=400)):
        if clipboard_command_exists():
            return True
    # double click
    logger.debug('uiobject.select_text_for_clipboard_command: double-clicking...')
    if uiautomator.test('TestUiObject', dict(path=path, action='DoubleClick', x=10, y=10)):
        if clipboard_command_exists():
            return True
    # swipe slowly
    logger.debug('uiobject.select_text_for_clipboard_command: swiping slowly...')
    if uiautomator.test('TestUiObject', dict(path=path, action='Swipe',
                                             startx=15, starty=15, endx=100, endy=15, steps=400)):
        if clipboard_command_exists():
            return True
    return False


def clipboard_command_exists():
    UiObj('/*').dump_ui_objects()
    if not UiObj('/LinearLayout[@index=0][@description=%s]/ImageView[@index=0]' % ui.Android.get('Done')).exists() and not UiObj('/LinearLayout[@index=0][matches(@resource,".*action_mode_close_button")]/ImageView[@index=0]').exists():
        logger.debug('clipboard_command_exists: DONE container does not exist.')
        return False
    logger.debug('clipboard_command_exists: DONE container exists.')
    logger.debug('clipboard_command_exists: dumping the container children...')
    UiObj('/LinearLayout[@index=0][@description=%s]' % ui.Android.get('Done')).dump_ui_objects()
    p1 = '/LinearLayout/TextView[@description=%s]' % ui.Android.get('Select all')
    if UiObj(p1).exists():
        logger.debug('clipboard_command_exists: Select All exists.')
        return True
    p2 = '/LinearLayout/TextView[@description=%s]' % ui.Android.get('Cut')
    if UiObj(p2).exists():
        logger.debug('clipboard_command_exists: Cut exists.')
        return True
    p3 = '/LinearLayout/TextView[@description=%s]' % ui.Android.get('Copy')
    if UiObj(p3).exists():
        logger.debug('clipboard_command_exists: Copy exists.')
        return True
    logger.debug('clipboard_command_exists: none of Select All, Cut, and Copy exists.')
    return False


def click_clipboard_command(command):
    if isinstance(command, unicode):
        command = command.encode('utf-8', 'ignore')
    logger.debug('click_clipboard_command: command=%s' % command)
    cbutton = UiObj('/TextView[@description=%s]' % command)
    if cbutton.exists():
        logger.debug('click_clipboard_command: command button exists -- clicking it...')
        return cbutton.click()
    else:
        opath = '/ImageButton[@description=%s]' % ui.Android.get('Other Options')
        if UiObj(opath).click():
            UiObj('/*').dump_ui_objects()
            if cbutton.exists():
                if cbutton.click():
                    return True
                logger.debug('click_clipboard_command: cannot choose %s command for unknown reason' % command)
            else:
                logger.debug('click_clipboard_command: no %s command to choose' % command)
            android_device.send_key(android_device.KEY_ESCAPE)
        else:
            logger.debug('click_clipboard_command: no %s command found' % command)
    return False
