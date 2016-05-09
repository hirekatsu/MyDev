class App:
    TIMEOUT_LAUNCH = 30
    TIMEOUT_AUTH = 5 * 60
    TIMEOUT_WEB_LOAD = 60
    TIMEOUT_LAUNCH_MS = TIMEOUT_LAUNCH * 1000
    TIMEOUT_AUTH_MS = TIMEOUT_AUTH * 1000
    TIMEOUT_WEB_LOAD_MS = TIMEOUT_WEB_LOAD * 1000

    def __init__(self, packbund):
        self._packbund = packbund
        self._key = packbund
        self._name = ''
        self._temp = None

    def packbund(self):
        return self._packbund

    def appkey(self):
        return self._key

    def appname(self, name=None):
        if not name:
            return self._name
        self._name = name
        return self

    def sharename(self, workspace=False, version=100):
        return self.appname()

