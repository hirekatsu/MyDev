# -*- coding: utf-8 -*-
from wrapped import Wrapped
from workhub import WorkHub
from uiobject import UiObj
import ui
import time


class Sealed(Wrapped):
    def __init__(self, packbund, activity=None, username=None, password=None, workspace=None):
        Wrapped.__init__(self, packbund=packbund, activity=activity, username=username, password=password)
        self._workspace = workspace

    # def is_workspace_prompted(self):
    #     print '$$$$$ TODO $$$$$ %s' % str(self)

    def join_workspace(self, workspace=None, banned=False):
        if not workspace:
            workspace = self._workspace['name']
        title = UiObj('/TextView[@package=%s][contains(@text,%s)]' % (self._packbund, ui.WrapLib.get('Do you want this app to join a WorkSpace')))
        ok = UiObj('/Button[@text=%s]' % ui.WrapLib.get('OK'))
        if title.exists() and ok.exists() and UiObj('/Button[@text=%s]' % ui.WrapLib.get('NO')).exists():
            ok.click()
            if not self.wait_for_complete():
                raise Exception('Failed to join Workspace: Timeout after clicking OK')
            join = UiObj('/Button[@package=%s][@text=%s]' % (self._packbund, ui.WrapLib.get('Join')))
            if join.exists():
                checked = UiObj('/CheckedTextView[@text=%s]' % workspace)
                if not checked.exists():
                    raise Exception('Failed to join Workspace: Specified Workspace %s does not exist' % workspace)
                checked.click()
                join.click()
                if not self.wait_for_complete():
                    raise Exception('Failed to join Workspace: Timeout after selecting Workspace')
                time.sleep(0.5)
        errmsg = UiObj('/TextView[@package=%s][contains(@text,%s)]' % (self._packbund, ui.WrapLib.get('is not allowed to join the')))
        if errmsg.exists():
            if not banned:
                raise Exception('Failed to join Workspace: Not allowed to join Workspace')
            UiObj('/Button[@text=%s]' % ui.WrapLib.get('OK')).click()
        else:
            if banned:
                raise Exception('Failed to block the app from joining Workspace')
        return self

    def startup_once(self, param=None):
        activity = param['activity'] if param and 'activity'in param else None
        extras = param['extras'] if param and 'extras' in param else None
        restart = param['restart'] if param and 'restart' in param else None
        Wrapped.initiate(self, activity=activity, extras=extras, restart=restart)
        workspace = param['workspace'] if param and 'workspace' in param and param['workspace'] else self._workspace
        self.join_workspace(workspace['name'])
        WorkHub().allow_workspace_request()
        if param and 'login_required' in param and param['login_required'] == True:
            if not self.is_login_prompted():
                raise Exception('Login is not prompted')
        username = param['username'] if param and 'username' in param and param['username'] else self._username
        password = param['password'] if param and 'password' in param and param['password'] else self._password
        self.login(username, password)
        return self

