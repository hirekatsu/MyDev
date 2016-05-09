import time
from helper import logger, connection
from helper.android import android_device as device
from testbase import TestBase
from apps.android.workweb import WorkWeb
from apps.android.swa import TWText
from apps.android.taoneapp import TAoneApp

device_id = None


class CABST_Enable_App_On_Device(TestBase):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = ''
        self._myapp = None

    def run(self):
        global device_id
        try:
            self.start()
            if not device_id:
                logger.info('Retrieving device identifier...')
                device_id = connection.get_device_id(device.get_serial())
                if not device_id:
                    raise Exception('Device ID unidentified - none from server')
            logger.debug('Device ID=%s' % device_id)

            wa = self._myapp()
            logger.info('Preparing %s' % wa.appname())
            wa.prep()
            if not connection.set_app_on_device(device_id, wa.packbund(), 'enable'):
                raise Exception('Failed to enable %s on server' % wa.packbund())
            wa.startup().stop()
            self.complete()
        except Exception as e:
            self.abend(e, take_log=True, take_screenshot=True)
            self.post_error()


class CABST_Disable_App_On_Device(TestBase):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Disable ??? to start on device'
        self._myapp = None

    def run(self):
        global device_id
        try:
            self.start()

            wa = self._myapp()
            wa.stop()
            if not connection.set_app_on_device(device_id, wa.packbund(), 'disable'):
                raise Exception('Failed to disable %s on server' % wa.packbund())
            wa.initiate().login()
            time.sleep(0.5)
            if not wa.match_image_template('CHECK_%s.screen_1.png' % self._id, 'administrative_block'):
                logger.info(' > NOTICE: Could not observe the block message on screen.')
            time.sleep(2)
            if wa.is_app_foreground():
                raise Exception('Disabled App could start up')
            log_file = self.get_log_file()
            if not connection.set_app_on_device(device_id, wa.packbund(), 'enable'):
                raise Exception('Failed to enable %s on server' % wa.packbund())
            wa.startup_once()
            if not wa.is_app_foreground():
                raise Exception('Failed to launch enabled App')

            self.complete()
        except Exception as e:
            self.abend(e, take_log=True, take_screenshot=True)
            self.post_error()
        self._myapp().stop()


class CABST_Wipe_App_On_Device(TestBase):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Wipe ??? on device'
        self._myapp = None

    def run(self):
        global device_id
        try:
            self.start()

            wa = self._myapp()
            wa.stop()
            if not connection.set_app_on_device(device_id, wa.packbund(), 'wipe'):
                raise Exception('Failed to wipe %s on server' % wa.packbund())
            wa.initiate().login()
            time.sleep(0.5)
            if not wa.match_image_template('CHECK_%s.screen_1.png' % self._id, 'administrative_block'):
                logger.info(' > NOTICE: Could not observe the block message on screen (at initial wipe).')
            time.sleep(2)
            if wa.is_app_foreground():
                raise Exception('Wiped App could start up')
            log_file = self.get_log_file()
            if not connection.set_app_on_device(device_id, wa.packbund(), 'enable'):
                raise Exception('Failed to enable %s on server' % wa.packbund())
            wa.initiate()
            time.sleep(0.5)
            if not wa.match_image_template('CHECK_%s.screen_2.png' % self._id, 'administrative_block'):
                logger.info(' > NOTICE: Could not observe the block message on screen (after re-enabling app).')
            time.sleep(2)
            if wa.is_app_foreground():
                raise Exception('Wiped App could start up after enabling on server')

            self.complete()
        except Exception as e:
            self.abend(e, take_log=True, take_screenshot=True)
            self.post_error()
        self._myapp().stop().prep(reinstall=True)
        connection.set_app_on_device(device_id, self._myapp().packbund(), 'enable')


class CABST_Wipe_Sealed_On_Device(TestBase):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Wipe ??? Sealed App on device'
        self._myapp = None

    def run(self):
        global device_id
        try:
            self.start()

            wa = self._myapp()
            wa.stop()
            if not connection.set_app_on_device(device_id, wa.packbund(), 'wipe'):
                raise Exception('Failed to wipe %s on server' % wa.packbund())
            # first try -- app should terminate
            logger.debug('%s: launching app after wipe... (1st try)' % self._id)
            wa.initiate().login()
            time.sleep(1)
            self.get_screenshot(prefix='CHECK_')
            time.sleep(2)
            if wa.is_app_foreground():
                raise Exception('Wiped App could start up (1)')
            logger.debug('%s: app terminated after login (1)' % self._id)
            wa.stop()
            # second try -- workspace join should be banned
            logger.debug('%s: launching app after wipe... (2nd try)' % self._id)
            wa.initiate()
            if wa.is_app_foreground():
                wa.join_workspace(banned=True)
                if wa.is_app_foreground():
                    raise Exception('Wiped App could start up (2)')
            else:
                logger.debug('%s: app terminated without message (2)' % self._id)
            # then enable the app
            if not connection.set_app_on_device(device_id, wa.packbund(), 'enable'):
                raise Exception('Failed to enable %s on server' % wa.packbund())
            wa.stop()
            logger.debug('%s: launching app after re-enable...' % self._id)
            wa.startup_once()
            if not wa.is_app_foreground():
                raise Exception('Sealed App cannot start up after enabling on server')

            self.complete()
        except Exception as e:
            self.abend(e, take_log=True, take_screenshot=True)
            self.post_error()
        self._myapp().stop()
        connection.set_app_on_device(device_id, self._myapp().packbund(), 'enable')


class C0000_Enable_WorkWeb_On_Device(CABST_Enable_App_On_Device):
    def __init__(self):
        CABST_Enable_App_On_Device.__init__(self)
        self._desc = 'Enable Work Web for preparation on device'
        self._myapp = WorkWeb


class C0001_Enable_SWA_On_Device(CABST_Enable_App_On_Device):
    def __init__(self):
        CABST_Enable_App_On_Device.__init__(self)
        self._desc = 'Enable SWA for preparation on device'
        self._myapp = TWText


class C0002_Enable_WrappedApp_On_Device(CABST_Enable_App_On_Device):
    def __init__(self):
        CABST_Enable_App_On_Device.__init__(self)
        self._desc = 'Enable Wrapped App for preparation on device'
        self._myapp = TAoneApp


class C0010_Disable_WorkWeb_On_Device(CABST_Disable_App_On_Device):
    def __init__(self):
        CABST_Disable_App_On_Device.__init__(self)
        self._desc = 'Disable Work Web to start on device'
        self._dependencies.append('T101.C0000_Enable_WorkWeb_On_Device')
        self._myapp = WorkWeb


class C0011_Disable_SWA_On_Device(CABST_Disable_App_On_Device):
    def __init__(self):
        CABST_Disable_App_On_Device.__init__(self)
        self._desc = 'Disable SWA to start on device'
        self._dependencies.append('T101.C0001_Enable_SWA_On_Device')
        self._myapp = TWText


class C0012_Disable_WrappedApp_On_Device(CABST_Disable_App_On_Device):
    def __init__(self):
        CABST_Disable_App_On_Device.__init__(self)
        self._desc = 'Disable Wrapped App to start on device'
        self._dependencies.append('T101.C0002_Enable_WrappedApp_On_Device')
        self._myapp = TAoneApp


class C0020_Wipe_WorkWeb_On_Device(CABST_Wipe_Sealed_On_Device):
    def __init__(self):
        CABST_Wipe_Sealed_On_Device.__init__(self)
        self._desc = 'Wipe Work Web on device'
        self._dependencies.append('T101.C0000_Enable_WorkWeb_On_Device')
        self._myapp = WorkWeb


class C0021_Wipe_SWA_On_Device(CABST_Wipe_App_On_Device):
    def __init__(self):
        CABST_Wipe_App_On_Device.__init__(self)
        self._desc = 'Wipe SWA on device'
        self._dependencies.append('T101.C0001_Enable_SWA_On_Device')
        self._myapp = TWText


class C0022_Wipe_WrappedApp_On_Device(CABST_Wipe_App_On_Device):
    def __init__(self):
        CABST_Wipe_App_On_Device.__init__(self)
        self._desc = 'Wipe Wrapped App on device'
        self._dependencies.append('T101.C0002_Enable_WrappedApp_On_Device')
        self._myapp = TAoneApp
