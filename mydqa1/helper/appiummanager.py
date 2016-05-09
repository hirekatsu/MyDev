import os
import re
from appium import webdriver
from config import settings
from helper import logger

_desired_capacities = {
    'appium-version': '1.0',
    'platformName': '',
    'deviceName': ''
}
# app
# bundleId

_ports = {}
_log_file = ''


def initialize(device_info, ports, log_file):
    global _desired_capacities, _ports, _log_file
    logger.debug('initializing appium')
    _desired_capacities['platformName'] = 'iOS'
    _desired_capacities['deviceName'] = device_info['name']
    _ports = {p: None for p in ports}
    _log_file = log_file
    command = '%s --udid %s --device-name "%s" --platform-name iOS --platform-version %s --log %s --log-timestamp --local-timezone --log-no-colors --log-level info &' % (settings.command['appium'],
                 device_info['udid'],
                 device_info['name'],
                 device_info['os_version'],
                 _log_file)
    logger.debug(command)
    os.system(command)


def finalize():
    os.system('killall -9 node')


def is_launch_failure(packbund):
    global _log_file
    with open(_log_file, 'r') as f:
        rx = re.compile('Failed to launch process with bundle identifier \'%s\'' % re.escape(packbund))
        for line in f:
            if rx.search(line):
                return True
    return False


def start_driver(packbund, path=None, port=None):
    global _desired_capacities, _ports
    logger.debug('start_driver: packbund=%s, path=%s, port=%s' % (packbund, path, port))
    wd = None
    dc = {'bundleId': packbund}
    if path:
        dc['app'] = path
    dc.update(_desired_capacities)
    logger.debug('start_driver: desired_capabilities=%s' % dc)
    if port is None:
        logger.debug('start_driver: finding available port in list=%s' % _ports)
        for p, d in _ports.iteritems():
            if d is None:
                port = p
                break
        if port is None:
            raise Exception('start_driver: no available port')
        logger.debug('start_driver: port %s selected' % port)
    try:
        logger.debug('start_driver: starting driver with port %s' % port)
        wd = webdriver.Remote('http://0.0.0.0:%s/wd/hub' % port, dc)
        logger.debug('start_driver: driver started, then wait for 60 sec.')
        wd.implicitly_wait(60)
        logger.debug('start_driver: 60 sec. elapsed')
        if port in _ports:
            _ports[port] = wd
    except Exception as e:
        logger.debug('start_driver: failed to start driver')
        if wd:
            wd.quit()
        raise e
    return wd


def stop_driver(wd):
    global _ports
    logger.debug('quit_driver: wd=%s' % wd)
    for p, d in _ports.iteritems():
        if d == wd:
            _ports[p] = None
            break
    wd.quit()
