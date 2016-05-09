import os.path
import re
import urllib

from helper import logger
from helper.android import android_device

_jar_folder = None
_jar_name = None
_packbund = None
_lastout = ''


def initialize(jar_folder, jar_name, packbund):
    global _jar_folder, _jar_name, _packbund
    logger.debug('initialize: jar_folder=%s, jar_name=%s, packbund=%s' % (jar_folder, jar_name, packbund))
    _jar_folder = jar_folder
    _jar_name = jar_name
    _packbund = packbund
    sout, serr = android_device.run_adb('push "%s" /data/local/tmp' % os.path.join(jar_folder, jar_name))
    if not serr or not re.match('^\d+ KB/s', serr):
        raise Exception('Failed to install uiautomator jar', __name__)


def test(testname, param={}):
    global _jar_name, _packbund, _lastout
    logger.debug('test: testname=%s' % testname)
    logger.debug('test: param=%s' % str(param))
    if param is None:
        param = {}
    parr = []
    for key in param:
        parr.extend(('-e', key, urllib.quote(str(param[key]))))
    cmd = 'shell uiautomator runtest %s -c %s.%s %s' % (_jar_name, _packbund, testname, ' '.join(parr))
    _lastout, serr = android_device.run_adb(cmd)
    return re.search('^OK', _lastout, flags=re.MULTILINE) is not None


def lastout():
    global _lastout
    return _lastout


def lasterror():
    global _lastout
    match = re.search(r'^junit\.framework\.AssertionFailedError: (.*)', _lastout, flags=re.MULTILINE)
    if not match:
        return ''
    return match.group(1)

