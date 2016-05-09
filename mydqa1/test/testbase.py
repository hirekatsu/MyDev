import importlib
import os.path
import sys
import traceback

from config import settings
from helper import logger
from helper.android import android_device
from apps.android.androidapp import AndroidApp
from test import results as testresults


class TestBase():
    def __init__(self):
        c1 = str(self.__class__).rsplit('.', 2)
        c2 = c1[2].split('_', 1)
        self._class = '.'.join((c1[1], c1[2]))
        self._id = '_'.join((c1[1], c2[0]))
        self._name = c2[1].replace('_', ' ')
        self._desc = '---TEST DESC GOES HERE---'
        self._dependencies = []
        self._no_workhub_dependency = False

    def get_named_result(self, name):
        if self._class not in testresults:
            return False
        if name not in testresults[self._class]:
            return False
        return testresults[self._class][name]

    def set_named_result(self, name, value):
        if self._class not in testresults:
            testresults[self._class] = {}
        testresults[self._class][name] = value

    def set_test_result(self, value):
        self.set_named_result('success', value)

    def check_dependencies(self):
        if not self._no_workhub_dependency:
            self._dependencies.insert(0, ['T000.C0000_Launch_WorkHub', 'launch'])
        logger.debug('%s::check_dependencies: %s' % (self.__class__, self._dependencies))
        for de in self._dependencies:
            if not isinstance(de, list):
                de = [de, 'success']
            if de[0] not in testresults:
                cc = de[0].split('.', 1)
                dm = importlib.import_module('test.%s' % cc[0])
                dc = getattr(dm, cc[1])
                dc().run()
            logger.debug(testresults)
            if de[0] not in testresults or de[1] not in testresults[de[0]] or not testresults[de[0]][de[1]]:
                raise Exception('Failed to run test due to incomplete dependency: %s %s' % (de[0], de[1]))

    def run(self):
        try:
            self.start()
            # do anything
            self.complete()
        except Exception as e:
            self.abend(e, take_log=True, take_screenshot=True)
            self.post_error()
        raise Exception('%s::run() not implemented' % self.__class__)

    def start(self):
        self.check_dependencies()
        logger.info('### TEST %s: %s' % (self._id, self._name))
        android_device.flash_log()
        android_device.meminfo()

    def complete(self):
        self.set_test_result(True)
        if settings.local.keep_device_log:
            self.get_log_file()
        logger.info(' > SUCCESS')

    def abend(self, ex, take_log=False, take_screenshot=False):
        self.set_test_result(False)
        logger.info('========================================')
        logger.info(' FAILURE: %s: %s' % (self._id, self._name))
        logger.info('   %s' % '\n'.join([str(arg) for arg in ex.args]))
        logger.info(' Description:')
        logger.info('   %s' % self._desc)
        logger.info('========================================')
        logger.info('')
        exc_type, exc_value, exc_tb = sys.exc_info()
        logger.debug(traceback.format_exception(exc_type, exc_value, exc_tb))
        if take_log:
            self.get_log_file()
        if take_screenshot:
            self.get_screenshot()

    def post_error(self):
        AndroidApp.hide_android_error()

    def get_log_file(self):
        log_file = os.path.join(settings.local.out_path, '%s.device.log' % self._id)
        android_device.get_log(log_file)
        return log_file

    def get_screenshot(self, prefix='', suffix=''):
        png_file = os.path.join(settings.local.out_path, '%s%s.screen%s.png' % (prefix, self._id, suffix))
        android_device.get_screenshot(png_file)
        return png_file


