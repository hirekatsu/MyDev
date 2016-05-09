from datetime import datetime
from uiobject import UiObj
from helper.android import android_device as device
from config import settings
import os
import os.path


class WebViewApp():
    def __init__(self):
        pass

    def is_device_location_popup(self):
        if not UiObj('/TextView[matches(@resource,".*dialog_message")][contains(@text,"your device\'s location")]').exists():
            return False
        return UiObj('/Button[@text=Deny]').click()

    def is_page_up(self, *templates):
        return self.match_image_template('_sc_%s' % datetime.today().strftime('%H%M%S'), *templates)

    def screenshot(self, basename='screenshot'):
        folder = os.path.join(settings.local.out_path, 'ss')
        if not os.path.exists(folder):
            os.mkdir(folder)
        png_file = os.path.join(folder, '%s.png' % basename)
        device.get_screenshot(png_file)
        return png_file

    def search_image_template(self, screenshot_name, *template_names):
        result = (None, None), (None, None)
        png_file = self.screenshot(screenshot_name)
        from apps.android import screenmatch
        for template_name in template_names:
            result = screenmatch.match(template_name, png_file)
            if result[0][0] is not None:
                break
        # if result[0][0] is not None:
        #     os.remove(png_file)
        return result

    def match_image_template(self, screenshot_name, *template_names):
        (left, _), (_, _) = self.search_image_template(screenshot_name, *template_names)
        return True if left is not None else False
