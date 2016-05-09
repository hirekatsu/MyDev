import os
from datetime import datetime

import default_settings
import settings
from apps.android import ui
from helper import logger, connection, uiautomator
from helper.android import android_device

_args = None
_taid = 'TA' + datetime.today().strftime('%y%m%d_%H%M%S')
_command = None
settings.take(default_settings.settings)


def initiate(a):
    global _args, _taid, _command
    _args = a
    if _args.config_file:
        settings.import_from(_args.config_file)
    sl = settings.local
    setattr(sl, 'out_path', os.path.join(sl.out_folder, _taid + '.out'))
    setattr(sl, 'log_path', os.path.join(sl.out_path, sl.log_file_name))
    setattr(sl, 'debug_path', os.path.join(sl.out_path, sl.debug_file_name))
    setattr(sl, 'appium_log_path', os.path.join(sl.out_path, sl.appium_log_file_name))
    setattr(sl, 'temp_path', os.path.join(sl.out_path, 'TA.tmp'))
    setattr(sl, 'android_workhub_path', os.path.join(sl.out_path, 'workhub.apk'))
    setattr(sl, 'ios_workhub_path', os.path.join(sl.out_path, 'workhub.ipa'))
    setattr(sl, 'nms_path', os.path.join(sl.out_path, 'nms.apk'))

    setattr(sl, 'keep_device_log', _args.device_log)

    _command = _args.command

    if not _args.nolog:
        logger.set_file(settings.local.log_path, settings.local.debug_path, _args.debug)
    logger.debug('settings.server: ' + str(settings.server))
    logger.debug('settings.local: ' + str(settings.local))
    logger.debug('settings.command: ' + str(settings.command))
    logger.debug('settings.info: ' + str(settings.info))

    connection.collect_server_info()


def initiate_android(a):
    global _args
    initiate(a)

    serial_number = settings.device.android_serial
    if _args.serial_number:
        serial_number = _args.serial_number
    android_device.attach(serial_number)
    logger.info('DEVICE=%s' % android_device.get_serial())
    ui.initialize(android_device.get_language())
    uiautomator.initialize(settings.local.UiA_JAR_folder,
                           settings.local.UiA_JAR_name,
                           settings.local.UiA_packbund)


def initiate_ios(a):
    global _args
    initiate(a)

    from helper import appiummanager
    udid = settings.device.ios_udid
    if _args.udid:
        udid = _args.udid
    appiummanager.initialize(dict(os_version=settings.device.ios_version,
                                  name=settings.device.ios_device_name,
                                  udid=udid),
                             settings.local.Appium_app_ports,
                             settings.local.appium_log_path)


def terminate_ios():
    from helper import appiummanager
    appiummanager.finalize()
