from helper import logger
import helper
import re
import os.path

_serial = None
_lang = 'en'
_ops = []


##################
#
#########
def get_serial():
    global _serial
    return _serial


##################
#
#########
def get_language():
    global _lang
    return _lang


##################
#
#########
def attach(s):
    global _serial, _ops, _lang
    logger.debug('%s: serial=%s' % (__name__, s))
    devarr = get_list()
    if len(devarr) == 0:
        raise Exception("No device attached", __name__)
    elif s is None:
        if len(devarr) == 1:
            _serial = devarr[0]
        else:
            raise Exception('Two or more devices attached: %s' % ' '.join(devarr), __name__)
    else:
        if s in devarr:
            _serial = s
        else:
            raise Exception('Specified device is not attached: %s NOT in (%s)' % (s, ' '.join(devarr)), __name__)
    _ops.extend(['-s', _serial])
    _lang = get_os_language()
    logger.debug('%s: lang=%s' % (__name__, _lang))


##################
#
#########
def run_adb(cmd, stdout=None):
    global _ops
    logger.debug('run_adb: _ops=%s, cmd=%s' % (str(_ops), cmd))
    sout, serr = helper.run_command('adb', '%s %s' % (' '.join(_ops), cmd), stdout=stdout)
    return sout, serr


##################
#
#########
def get_list():
    devarr = []
    sout, serr = run_adb('devices')
    sout = sout.splitlines()
    if len(sout) > 0 and sout[0].startswith('* daemon not running. starting it now on port'):
        sout.pop(0)
    if len(sout) > 0 and sout[0].startswith('* daemon started successfully *'):
        sout.pop(0)
    if len(sout) > 0 and sout[0].startswith('List of devices attached'):
        sout.pop(0)
        for line in sout:
            m = re.search('^([^\s]*)\s+device', line)
            if m is not None:
                devarr.append(m.group(1))
    logger.debug('%s: devices: %s' % (__name__, ' '.join(devarr)))
    return devarr


##################
#
#########
def meminfo():
    run_adb('shell dumpsys meminfo')


##################
#
#########
def get_os_language():
    sout, serr = run_adb('shell getprop persist.sys.language')
    return re.sub('[\r\n]', '', sout)


##################
#
#########
def is_app_installed(packbund):
    # sout, serr = run_adb('shell pm list package "|" grep %s' % packbund)
    sout, serr = run_adb('shell pm list package')
    return re.search('package:%s' % packbund, sout) is not None


##################
#
#########
def uninstall_app(packbund):
    logger.debug('uninstall_app: packbund=%s' % packbund)
    sout, serr = run_adb('uninstall %s' % packbund)
    return re.search('Success', sout) is not None


##################
#
#########
def install_app(packbund, filepath, reinstall=False):
    logger.debug('install_app: packbund=%s, filepath=%s, reinstall=%s' % (packbund, filepath, reinstall))
    if is_app_installed(packbund):
        if reinstall:
            if not uninstall_app(packbund):
                logger.debug('install_app: uninstalling failed')
                return False
        else:
            logger.debug('install_app: app is already installed')
            return True
    logger.debug('install_app: starting installation')
    sout, serr = run_adb('install %s' % filepath)
    if not re.search('Success', sout):
        logger.debug('install_app: failed adb installation')
        return False
    logger.debug('install_app: finishing installation')
    if not is_app_installed(packbund):
        logger.debug('install_app: app is not in package list')
        return False
    return True


##################
#
#########
def stop_app(packbund):
    logger.debug('stop_app: packbund=%s' % packbund)
    run_adb('shell am force-stop %s' % packbund)


##################
#
#########
def file_delete(path, runas=''):
    runas_op = ''
    if runas:
        runas_op = 'run-as %s' % runas
    sout, serr = run_adb('shell %s rm %s' % (runas_op, path))
    return 'No such file or directory' not in sout


##################
#
#########
def file_list(path, recursive=False, runas=''):
    runas_op = ''
    if runas:
        runas_op = 'run-as %s' % runas
    ls_op = '-R' if recursive else ''
    if not path.endswith('/'):
        path += '/'
    sout, serr = run_adb('shell %s ls %s %s' % (runas_op, ls_op, path))
    return set(sout.splitlines())


##################
#
#########
def file_exist(path, runas=''):
    runas_op = ''
    if runas:
        runas_op = 'run-as %s' % runas
    sout, serr = run_adb('shell %s ls -d %s' % (runas_op, path))
    return 'No such file or directory' not in sout


##################
#
#########
def file_cat(path, runas=''):
    runas_op = ''
    if runas:
        runas_op = 'run-as %s' % runas
    sout, serr = run_adb('shell %s cat %s' % (runas_op, path))
    return sout


##################
#
#########
def file_diff(arg, recursive=False, runas=''):
    if isinstance(arg, str):
        return dict(path=arg, recursive=recursive, list=file_list(arg, recursive=recursive, runas=runas))
    elif isinstance(arg, dict):
        logger.debug('file_diff: previous:\n%s' % arg['list'])
        current = file_list(arg['path'], recursive=arg['recursive'], runas=runas)
        logger.debug('file_diff: current:\n%s' % current)
        diff = current - arg['list']
        logger.debug('file_diff: diff:\n%s' % diff)
        return diff
    return None


def get_external_storage():
    sout, serr = run_adb('shell echo $EXTERNAL_STORAGE')
    return re.sub('[\r\n]', '', sout)


##################
#
#########
def flash_log():
    run_adb('logcat -c')


##################
#
#########
def get_log(filepath):
    logger.debug('get_log: getting device log to %s' % filepath)
    run_adb('logcat -d -v threadtime', stdout=filepath)


##################
#
#########
def get_screenshot(filepath):
    logger.debug('get_screenshot: getting device screenshot to %s' % filepath)
    basename = os.path.basename(filepath)
    dirname = os.path.dirname(filepath)
    run_adb('shell screencap -p /data/local/tmp/%s' % basename)
    logger.debug('get_screenshot: screenshot taken')
    run_adb('pull /data/local/tmp/%s %s' % (basename, dirname))
    logger.debug('get_screenshot: screenshot file pulled')
    run_adb('shell rm /data/local/tmp/%s' % basename)
    logger.debug('get_screenshot: screenshot retrieved successfully')


##################
#
#########
KEY_HOME = 3
KEY_TAB = 61
KEY_ENTER = 66
KEY_DEL = 67
KEY_MENU = 82
KEY_ESCAPE = 111


def send_key(key):
    logger.debug('send_key: key=%d' % key)
    run_adb('shell input keyevent %d' % key)

def input_text(text):
    logger.debug('input_text: text=%s' % text)
    run_adb('shell input text %s' % text)
