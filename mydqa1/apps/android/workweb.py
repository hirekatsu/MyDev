import time
from datetime import datetime

import ui
from uiobject import UiObj, click_clipboard_command
from helper import uiautomator, connection, logger
from helper.android import android_device as device
from config import settings
from apps.app import App
from sealed import Sealed
from webviewapp import WebViewApp


class WorkWebCore(Sealed, WebViewApp):
    def __init__(self, username=None, password=None, workspace=None):
        Sealed.__init__(self,
                        packbund='com.symantec.mobile.securebrowser',
                        activity='com.example.safebrowser.EntryActivity',
                        username=username,
                        password=password,
                        workspace=workspace)
        self._bar = None
        self._wide = False
        self._address_bar_edit_path = '/RelativeLayout/RelativeLayout/RelativeLayout/TextView[@package=%s][@instance=1]' % self._packbund
        self._address_bar_exit_path = '/ImageButton[@package=%s][@instance=0]' % self._packbund
        self._content_path = '/LinearLayout[@instance=1]/FrameLayout[@index=1]/FrameLayout[@index=0]/*[@index=0]'

    def is_page_up(self, *templates):
        self.wait_while_loading()
        return WebViewApp.is_page_up(self, *templates)

    def move_to_bookmark(self):
        if not self.is_bookmarks_page():
            icon = UiObj('/ImageButton[@package=%s][@description=%s]' % (self._packbund,
                                                                         ui.WorkWeb.get('Settings menu icon')))
            if not icon.click():
                raise Exception('Failed to show menu to move to Bookmarks page: Error on showing menu')
            (left, top), (right, bottom) = self.search_image_template('_sc.ww_%s' % datetime.today().strftime('%H%M%S'),
                                                                      'ww_bookmarks_icon')
            if left is None:
                raise Exception('Failed to move to Bookmarks page: No Bookmarks icon found on screen')
            x = left + int((right - left) / 2)
            y = top + int((bottom - top) / 2)
            if not uiautomator.test('TestDeviceClick', dict(x=x, y=y)):
                raise Exception('Failed to move to Bookmarks page: Error on clicking coordinate on screen')
            time.sleep(1)
            if not self.is_bookmarks_page():
                raise Exception('Failed to move to Bookmarks page')
        return self

    # def initiate(self, extras=None, restart=None):
    #     Sealed.initiate(self, activity=self._activity, extras=extras, restart=restart)

    def startup_once(self, param=None):
        Sealed.startup_once(self, param=param)
        time.sleep(1)

        self.dismiss_initial_page()
        self.is_device_location_popup()
        auth_required = param['auth_required'] if param and 'auth_required' in param else False
        if not auth_required:
            self.is_web_auth_prompted()
        if param and 'to_bookmarks' in param and param['to_bookmarks'] == True:
            self.move_to_bookmark()
        self._wide = UiObj('/HorizontalScrollView[@package=%s]' % self._packbund).exists()
        if self._wide:
            self._address_bar_edit_path = '/FrameLayout/RelativeLayout/RelativeLayout/TextView[@package=%s][@instance=0]' % self._packbund
            self._address_bar_exit_path = '/FrameLayout/FrameLayout[@package=%s][@instance=0]' % self._packbund
            self._content_path = '/LinearLayout[@instance=1]/FrameLayout[@index=1]/FrameLayout[@index=1]/*[@index=0]'
        return self

    def dismiss_initial_page(self):
        if UiObj('/TextView[@package=%s][contains(@text,%s)]' % (self._packbund, ui.WorkWeb.get('The app found information about previous crashes'))).exists():
            UiObj('/Button[@text=%s]' % ui.WorkWeb.get('Dismiss')).click()
            time.sleep(2)
        if UiObj('/TextView[@package=%s][contains(@text,%s)]' % (self._packbund, ui.WorkWeb.get('SYMANTEC SOFTWARE LICENSE AGREEMENT'))).exists():
            UiObj('/Button[@text=%s]' % ui.WorkWeb.get('I Agree')).click()
            time.sleep(3)

        view = UiObj('/WebView[@package=%s][matches(@resource,".*tutorial_webview")]' % self._packbund)
        if view.exists():
            UiObj('/*').dump_ui_objects()
            view.wait_until_gone(timeout=App.TIMEOUT_WEB_LOAD)
        UiObj('/*').dump_ui_objects()
        view = UiObj('/View[@package=%s][@description=%s]' % (self._packbund, ui.WorkWeb.get('Tutorial')))
        if view.exists():
            view.get_child('/View[@index=0]').click()
            time.sleep(3)
            if view.exists():
                raise Exception('Failed to dismiss initial page: Could not find Close button')
        self.wait_while_loading()
        if self.is_android_error():
            raise Exception('Failed to dismiss initial page: Android error')

    def address_bar_edit(self):
        if not self._bar:
            self._bar = UiObj('/RelativeLayout/RelativeLayout/LinearLayout/EditText[@package=%s]' % self._packbund)
        return self._bar

    def switch_address_bar_mode(self, mode):
        edit = self.address_bar_edit()
        if not edit.exists():
            if mode == 'editable':
                UiObj(self._address_bar_edit_path).click()
                if not edit.exists():
                    return False
        else:
            if mode == 'static':
                UiObj(self._address_bar_exit_path).click()
        return True

    def wait_while_loading(self):
        path = '/RelativeLayout/FrameLayout/ProgressBar[@package=%s][@index=0]' % self._packbund
        UiObj(path).wait_until_gone(timeout=60)

    def navigate(self, url):
        if not self.switch_address_bar_mode('editable'):
            raise WorkWebNavigationException('Failed to navigate on Work Web: Address bar cannot be editable')
        edit = self.address_bar_edit()
        if edit.get_text() != url:
            edit.set_text(url, hint=ui.WorkWeb.get('Search or type a URL'))
            device.send_key(device.KEY_ENTER)
            time.sleep(1)
            self.wait_while_loading()
        else:
            self.switch_address_bar_mode('static')
        if self.is_android_error():
            raise WorkWebNavigationException('Failed to navigate on Work Web: Android error')
        time.sleep(1.5)
        self.is_device_location_popup()
        return self

    def refresh(self):
        button = UiObj('/ImageButton[@package=%s][@description="%s"]' % (self._packbund, ui.WorkWeb.get('Reload page')))
        if not button.exists():
            raise Exception('Failed to refresh Work Web page: No Refresh button')
        button.click()
        time.sleep(1)
        self.wait_while_loading()
        if self.is_android_error():
            raise Exception('Failed to refresh Work Web page: Android error')
        time.sleep(1.5)
        self.is_device_location_popup()
        return self

    def is_bookmarks_page(self):
        if not UiObj('/TextView[@package=%s][@text=%s]' % (self._packbund, ui.WorkWeb.get('Bookmarks'))).exists():
            return False
        if not UiObj('/TextView[@package=%s][@text=%s]' % (self._packbund, ui.WorkWeb.get('Tap to search or type a URL'))).exists():
            return False
        return True

    def is_error_page(self):
        return UiObj('/TextView[@package=%s][@text=error_page.html]' % self._packbund).exists()

    def is_web_auth_prompted(self):
        title = UiObj('/TextView[@package=%s][@text=%s]' % (self._packbund, ui.WorkWeb.get('Authentication Required')))
        if not title.exists():
            return False
        return UiObj('/Button[@text=%s]' % ui.WorkWeb.get('Cancel')).click()

    def copy_text(self, text, block=False):
        if not self.is_bookmarks_page():
            if not self.move_to_bookmark():
                raise Exception('Failed to copy text on Work Web: Cannot move to Bookmarks')
        if not self.switch_address_bar_mode('editable'):
            raise Exception('Failed to copy text on Work Web: Cannot switch address bar mode')
        edit = self.address_bar_edit()
        edit.set_text(text, hint=ui.WorkWeb.get('Search or type a URL'))
        if not edit.select_text():
            raise Exception('Failed to copy text on Work Web: Cannot select text')
        if not click_clipboard_command(ui.Android.get('Copy')):
            raise Exception('Failed to copy text on Work Web: Cannot choose Copy on Clipboard commands')
        ## Blocking copy cannot be verified in this method...
        self.switch_address_bar_mode('static')
        if self.is_android_error():
            raise Exception('Failed to copy text on Work Web: Android error')
        if not self.is_app_foreground():
            raise Exception('Failed to copy text on Work Web: Eventually app is not on screen')
        return self

    def paste_text(self, clipboard='workspace', verify=None, block=False):
        if not self.is_bookmarks_page():
            if not self.move_to_bookmark():
                raise Exception('Failed to paste text on Work Web: Cannot move to Bookmarks')
        if not self.switch_address_bar_mode('editable'):
            raise Exception('Failed to paste text on Work Web: Cannot switch address bar mode')
        edit = self.address_bar_edit()
        edit.set_text('DUMMYTEXT', hint=ui.WorkWeb.get('Search or type a URL'))
        if not edit.select_text():
            raise Exception('Failed to paste text on Work Web: Cannot select text')
        if not click_clipboard_command(ui.Android.get('Paste')):
            raise Exception('Failed to paste text on Work Web: Cannot choose Paste on Clipboard commands')
        self.paste_from_clipboard(clipboard)
        if verify:
            current = edit.get_text()
            logger.debug('WorkWeb.paste_text: AddressBar.getText()=%s' % current)
            logger.debug('WorkWeb.paste_text: verify=%s' % verify)
            if current == verify:
                if block:
                    raise Exception('Failed to paste text on Work Web: Text was pasted unexpectedly --- should NOT be pasted')
            else:
                if not block:
                    raise Exception('Failed to paste text on Work Web: Text was NOT pasted successfully')
        self.switch_address_bar_mode('static')
        if self.is_android_error():
            raise Exception('Failed to paste text on Work Web: Android error')
        if not self.is_app_foreground():
            raise Exception('Failed to paste text on Work Web: Eventually app is not on screen')
        return self

    def share_document(self, text):
        if not self.navigate('http://testweb1.ac.symantec.com/plaintext/input.html'):
            raise Exception('Failed to share text on Work Web: Cannot move to URL to share text')
        content = UiObj(self._content_path)
        if not content.wait_for_exists(App.TIMEOUT_WEB_LOAD):
            raise Exception('Failed to share text on Work Web: Cannot locate Web content view')
        content.click_topleft()
        time.sleep(0.5)
        device.input_text(text)
        device.send_key(device.KEY_ENTER)
        if not content.select_text():
            raise Exception('Failed to share text on Work Web: Cannot select text')
        if not click_clipboard_command(ui.Android.get('Share')):
            raise Exception('Failed to share text on Work Web: Cannot choose Share on Clipboard commands')
        if self.is_android_error():
            raise Exception('Failed to share text on Work Web: Android error')
        return self


class WorkWeb(WorkWebCore):
    def __init__(self):
        WorkWebCore.__init__(self,
                             username=settings.server.username,
                             password=settings.server.password,
                             workspace=dict(packbund=connection.workhub_packbund(),
                                            name=settings.server.workhub))


class WorkWebNavigationException(Exception):
    pass
