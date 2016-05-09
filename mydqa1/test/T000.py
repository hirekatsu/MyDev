import json
import re

from helper import connection, logger
from helper.android import android_device
from apps.android.workhub import WorkHub
from apps.android.workweb import WorkWeb
from apps.android.workmail import WorkMail
from apps.android.swa import TWText, GoogleSWA
from apps.android.taoneapp import TAoneApp, TAoneBuddy, TAoneUtil
from testbase import TestBase

_device_id = None


def get_device_id():
    global _device_id
    if _device_id is None:
        _device_id = connection.get_device_id(android_device.get_serial())
    return _device_id


class C0000_Launch_WorkHub(TestBase):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Launch Work Hub and verify device enrollment'
        self._no_workhub_dependency = True

    def run(self):
        try:
            self.start()
            logger.info('Installing and launching Work Hub')
            WorkHub().prep().startup()
            self.set_named_result('launch', True)

            logger.info('Checking device enrollment info on server...')
            log_file = self.get_log_file()
            log_info = get_device_info_from_log(log_file)
            if 'IMEI' not in log_info:
                log_info['IMEI'] = ''
            logger.debug('log_info:')
            logger.debug(str(log_info))
            logger.debug('checking device serial...')
            if 'serial_number' not in log_info:
                raise Exception('Serial number is not logged in device log file')
            if android_device.get_serial() != log_info['serial_number']:
                raise Exception('Serial number does not match: device=%s != log=%s' %
                                (android_device.get_serial(), log_info['serial_number']))
            logger.debug('getting device info from server...')
            if 'mac_address' not in log_info:
                raise Exception('MAC address is not logged in device log file')
            server_info = connection.get_device_info_by_mac(log_info['mac_address'])
            if not server_info:
                raise Exception('failed to retrieve device info from server')
            logger.debug('server_info:')
            logger.debug(json.dumps(server_info, indent=2))
            if log_info['serial_number'].upper() != server_info['serial_number'].upper():
                raise Exception('Serial number does not match between server info and device log')
            if log_info['mac_address'].upper() != server_info['mac_address'].upper():
                raise Exception('MAC address does not match between server info and device log')
            if log_info['IMEI'].upper() != server_info['IMEI'].upper():
                raise Exception('IMEI does not match between server info and device log')
            keys_to_check = {'acid', 'phone_id', 'is_rooted', 'platform', 'mobility_manager_id', 'identifier',
                             'secure_email_eas_device_id'}
            if not keys_to_check.issubset(server_info.keys()):
                raise Exception('One or more of %s are not in server info' % ', '.join(keys_to_check))
            self.set_named_result('enroll', True)

            android_device.send_key(android_device.KEY_HOME)
            self.complete()
        except Exception as e:
            self.abend(e, take_log=True, take_screenshot=True)
            self.post_error()


class C0011_Launch_WorkWeb(TestBase):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Launch Sealed Work Web'

    def run(self):
        try:
            self.start()
            ww = WorkWeb().prep('xTA - default')
            connection.set_app_on_device(get_device_id(), ww.packbund(), 'enable')
            ww.startup(param=dict(to_bookmarks=True))
            self.complete()
        except Exception as e:
            self.abend(e, take_log=True, take_screenshot=True)
            self.post_error()
        WorkWeb().stop()


class C0012_Launch_WorkMail(TestBase):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Launch Sealed Work Mail'

    def run(self):
        try:
            self.start()
            wm = WorkMail().prep('xTA - default')
            connection.set_app_on_device(get_device_id(), wm.packbund(), 'enable')
            wm.startup()
            self.complete()
        except Exception as e:
            self.abend(e, take_log=True, take_screenshot=True)
            self.post_error()
        WorkMail().stop()


class C0021_Launch_SWA(TestBase):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Launch Secure Web App'

    def run(self):
        try:
            self.start()
            wa = TWText().prep('xTA - default')
            connection.set_app_on_device(get_device_id(), wa.packbund(), 'enable')
            if not wa.startup().is_page_up('symc_logo'):
                raise Exception('Secure Web App main page does not show up')
            self.complete()
        except Exception as e:
            self.abend(e, take_log=True, take_screenshot=True)
            self.post_error()
        TWText().stop()


class C0022_Launch_SWA_Google(TestBase):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Launch Secure Web App for https://www.google.com'

    def run(self):
        try:
            self.start()
            wa = GoogleSWA().prep('xTA - default').startup()
            self.get_screenshot(prefix='CHECK_', suffix='_1')
            if not wa.is_page_up('google_main', 'google_main2'):
                raise Exception('Secure Web App for Google main page does not show up')
            self.complete()
        except Exception as e:
            self.abend(e, take_log=True, take_screenshot=True)
            self.post_error()
        GoogleSWA().stop()


class C0031_Launch_WrappedApp(TestBase):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Launch Wrapped Native App'

    def run(self):
        try:
            self.start()
            wa = TAoneApp().prep('xTA - default')
            connection.set_app_on_device(get_device_id(), wa.packbund(), 'enable')
            if not wa.startup().is_main_page():
                raise Exception('Native App main page does not show up')
            self.complete()
        except Exception as e:
            self.abend(e, take_log=True, take_screenshot=True)
            self.post_error()
        TAoneApp().stop()


class C0040_Prep_Other_Apps(TestBase):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Prepare other test Apps on server and install them on device'

    def run(self):
        try:
            self.start()
            logger.info('Preparing Secure Web App (text)')
            connection.set_app_on_device(get_device_id(), TWText().prep().packbund(), 'enable')

            logger.info('Preparing Wrapped Native App (TAoneBuddy)')
            connection.set_app_on_device(get_device_id(), TAoneBuddy().prep().packbund(), 'enable')

            logger.info('Preparing Plain Native App (TAoneUtil)')
            TAoneUtil().prep()
            self.complete()
        except Exception as e:
            self.abend(e, take_log=True, take_screenshot=True)
            self.post_error()


def get_device_info_from_log(log_file):
    info = {}
    with open(log_file, 'r') as f:
        rx = re.compile('E NukonaConnect: *"(?P<key>serial_number|mac_address|IMEI)": *"(?P<val>[^"]*)",')
        for line in f:
            match = rx.search(line)
            if match:
                info[match.group('key')] = match.group('val')
                logger.debug('get_device_info_from_log: %s=%s' % (match.group('key'), match.group('val')))
    return info
