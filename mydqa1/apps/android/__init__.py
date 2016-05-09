# -*- coding: utf-8 -*-
from config import settings
from helper import connection, logger
from helper.android import android_device as device


def uninstall_wrapped_apps():
    logger.debug('uninstall_wrapped_apps:')
    for key, data in settings.info.apps.iteritems():
        if data['metadata']:
            if 'bundle-identifier' in data['metadata']:
                logger.debug('uninstall_wrapped_apps: uninstalling %s...' % data['metadata']['bundle-identifier'])
                device.uninstall_app(data['metadata']['bundle-identifier'])
    logger.debug('uninstall_wrapped_apps: uninstalling workhub (%s)' % connection.workhub_packbund())
    device.uninstall_app(connection.workhub_packbund())


def prep_wrapped_apps(install=False):
    for key in settings.info.apps:
        logger.info(key)
        if not connection.assure_app(name=key, policy=None):
            logger.info('Failed to prep app %s on server' % key)
        elif install:
            packbund = settings.info.apps[key]['metadata']['bundle-identifier']
            apk_file = connection.download_app(key, settings.tempfile(packbund + '.apk'))
            if not apk_file:
                logger.info('Failed to download app "%s" from server' % key)
            else:
                if not device.install_app(packbund, apk_file, True):
                    logger.info('Failed to install app "%s" (%s) on device' % (key, packbund))


def rewrap_apps():
    connection.rebuild_workhub()
    for key in settings.info.apps:
        connection.rewrap_app(name=key)


def prep_policies():
    for key in settings.info.app_policies:
        connection.assure_app_policy(key)


