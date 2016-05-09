import time
import ui
from uiobject import UiObj, click_clipboard_command
from helper import connection, logger
from helper.android import android_device as device
from config import settings
from wrapped import Wrapped
from webviewapp import WebViewApp


class SecureWebApp(Wrapped, WebViewApp):
    def __init__(self, key, packbund, username=None, password=None):
        Wrapped.__init__(self,
                         packbund=packbund,
                         activity='com.nukona.WebVille.WebVilleActivity',
                         username=username,
                         password=password)
        self._key = key

    def startup_once(self, param=None):
        Wrapped.startup_once(self, param=param)
        time.sleep(5)
        return self

    def refresh(self):
        if not self.is_app_foreground():
            raise Exception('Failed to refresh Secure Web App page: App is not on screen')
        device.send_key(device.KEY_MENU)
        time.sleep(0.5)
        menu = UiObj('/TextView[@text=%s]' % ui.SWA.get('Refresh'))
        if not menu.exists():
            raise Exception('Failed to refresh Secure Web App page: Refresh menu is not on screen')
        menu.click()
        time.sleep(2)
        return self


class TWTextCore(SecureWebApp):
    def __init__(self, key, packbund, username=None, password=None, htmltext=False):
        SecureWebApp.__init__(self, key=key, packbund=packbund, username=username, password=password)
        self._htmltext = htmltext

    def copy_text(self, text, block=False):
        if not self.enter_text(text):
            raise Exception('Failed to copy text on Secure Web App: Cannot enter text to copy')
        if self._htmltext:
            device.send_key(device.KEY_ENTER)
        if not self.get_content_object().select_text():
            raise Exception('Failed to copy text on Secure Web App: Cannot select text to copy')
        if not click_clipboard_command(ui.Android.get('Copy')):
            raise Exception('Failed to copy text on Secure Web App: Cannot choose Copy command')
        # for ET#3817884
        if self._htmltext:
            if self.paste_from_prompt().exists():
                raise Exception('Failed to copy text on Secure Web App: Paste From is prompted unexpectedly')
        if self.is_android_error():
            raise Exception('Failed to copy text on Secure Web App: Android error')
        if not self.is_app_foreground():
            raise Exception('Failed to copy text on Secure Web App: Eventually app is not on screen')
        return self

    def paste_text(self, clipboard='none', verify=None, block=False):
        if not self.enter_text('DUMMYTEXT'):
            raise Exception('Failed to paste text on Secure Web App: Cannot enter dummy text')
        if not self.get_content_object().select_text():
            raise Exception('Failed to paste text on Secure Web App: Cannot select dummy text')
        if not click_clipboard_command(ui.Android.get('Paste')):
            raise Exception('Failed to paste text on Secure Web App: Cannot choose Paste command')
        self.paste_from_clipboard('none')
        if verify:
            if not self.is_webview_content():
                edit = self.get_content_object().get_child('/EditText')
                if edit.get_content_description() == verify:
                    if block:
                        raise Exception('Failed to paste text on Secure Web App: Text was pasted unexpectedly --- should NOT be pasted')
                else:
                    if not block:
                        raise Exception('Failed to paste text on Secure Web App: Text was NOT pasted successfully')
            else:
                logger.info(''' >> WARNING: Cannot verify the pasted text programmatically.
Check the screen capture if its text is %s equal to %s''' % (('NOT' if block else ''), verify))
        if self.is_android_error():
            raise Exception('Failed to paste text on Secure Web App: Android error')
        if not self.is_app_foreground():
            raise Exception('Failed to paste text on Secure Web App: Eventually app is not on screen')
        return self

    def share_document(self, text):
        if not self.enter_text(text):
            raise Exception('Failed to share text on Secure Web App: Cannot enter text to share')
        device.send_key(device.KEY_ENTER)
        if not self.get_content_object().select_text():
            raise Exception('Failed to share text on Secure Web App: Cannot select text to share')
        if not click_clipboard_command(ui.Android.get('Share')):
            raise Exception('Failed to share text on Secure Web App: Cannot choose Share command')
        if self.is_android_error():
            raise Exception('Failed to share text on Secure Web App: Android error')
        return self

    def enter_text(self, text):
        content = self.get_content_object()
        if not self.is_webview_content():
            logger.debug('TWText.enter_text: handling Web content elements directly...')
            edit = content.get_child('/EditText')
            if not edit.exists():
                logger.debug('TWText.enter_text: EditText does not exist in WebView')
                return False
            edit.click()
            edit.set_text(text)
        else:
            logger.debug('TWText.enter_text: handling WebView...')
            device.send_key(device.KEY_TAB)
            device.input_text(text)
        return True

    def get_content_object(self):
        UiObj('/*').dump_ui_objects(retry=3)
        content = UiObj('/LinearLayout[@instance=0]/FrameLayout[@index=1]/View[@package=%s][@instance=1]' % self._packbund)
        if not content.exists():
            content = UiObj('/LinearLayout/FrameLayout/WebView[@package=%s]' % self._packbund)
        return content

    def is_webview_content(self):
        UiObj('/*').dump_ui_objects()
        if UiObj('/LinearLayout[@instance=0]/FrameLayout[@index=1]/View[@package=%s][@instance=1]' % self._packbund).exists():
            return False
        return UiObj('/LinearLayout/FrameLayout/WebView[@package=%s]' % self._packbund).exists()


def packbund_for_swa(key):
    if key not in settings.info.apps:
        raise Exception('Invalid app key: %s' % key, __name__)
    metadata = settings.info.apps[key]['metadata']
    if not metadata:
        if not connection.assure_app(name=key, policy=None):
            return None
        metadata = settings.info.apps[key]['metadata']
    return metadata['bundle-identifier']


class TWEdit(TWTextCore):
    def __init__(self):
        key = 'swa:text'
        TWTextCore.__init__(self, key, packbund_for_swa(key),
                            username=settings.server.username,
                            password=settings.server.password)


class TWText(TWTextCore):
    def __init__(self):
        key = 'swa:text'
        TWTextCore.__init__(self, key, packbund_for_swa(key),
                            username=settings.server.username,
                            password=settings.server.password,
                            htmltext=True)


class TWTextByIPAddr(TWTextCore):
    def __init__(self):
        key = 'swa:ipaddr'
        TWTextCore.__init__(self, key, packbund_for_swa(key),
                            username=settings.server.username,
                            password=settings.server.password)


class TWBasicAuth(TWTextCore):
    def __init__(self):
        key = 'swa:basic'
        TWTextCore.__init__(self, key, packbund_for_swa(key),
                            username=settings.server.username,
                            password=settings.server.password)


class TWDigestAuth(TWTextCore):
    def __init__(self):
        key = 'swa:digest'
        TWTextCore.__init__(self, key, packbund_for_swa(key),
                            username=settings.server.username,
                            password=settings.server.password)



class SymantecSWA(SecureWebApp):
    def __init__(self):
        key = 'swa:symantec'
        SecureWebApp.__init__(self, key, packbund_for_swa(key),
                              username=settings.server.username,
                              password=settings.server.password)


class GoogleSWA(SecureWebApp):
    def __init__(self):
        key = 'swa:google'
        SecureWebApp.__init__(self, key, packbund_for_swa(key),
                              username=settings.server.username,
                              password=settings.server.password)


class LinkedinSWA(SecureWebApp):
    def __init__(self):
        key = 'swa:linkedin'
        SecureWebApp.__init__(self, key, packbund_for_swa(key),
                              username=settings.server.username,
                              password=settings.server.password)


class YahooSWA(SecureWebApp):
    def __init__(self):
        key = 'swa:yahoo'
        SecureWebApp.__init__(self, key, packbund_for_swa(key),
                              username=settings.server.username,
                              password=settings.server.password)
