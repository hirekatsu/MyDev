import os

from helper import logger, connection
from config import settings
from workhub import WorkHub


class MyWorkHub(WorkHub):
    def __init__(self):
        WorkHub.__init__(self,
                         packbund=settings.server.ios_packbund,
                         path=settings.local.ios_workhub_path,
                         username=settings.server.username,
                         password=settings.server.password)

    def ipapath(self):
        logger.debug('MyWorkHub.ipapath')
        if not os.path.exists(self._path):
            logger.debug('MyWorkHub.prep: workhub has not been downloaded yet')
            if not connection.download_workhub('ios', self._path):
                raise Exception('Failed to download workhub')
        return self._path

    def prep(self, reinstall=False):
        logger.debug('MyWorkHub.prep: reinstall=%s' % reinstall)
        return self

    def initiate(self):
        logger.debug('MyWorkHub.initiate: port is %s' % settings.local.Appium_workhub_port)
        return WorkHub.initiate(self, settings.local.Appium_workhub_port)
