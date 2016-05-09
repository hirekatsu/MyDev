# -*- coding: utf-8 -*-
import time
import ui
from uiobject import UiObj
from helper import connection, logger
from config import settings
from androidapp import AndroidApp
from wrapped import Wrapped
from sealed import Sealed
from workhub import WorkHub


class WorkMailCore(Sealed):
    def __init__(self, username=None, password=None, workspace=None, email_password=None):
        Sealed.__init__(self,
                        packbund='com.symantec.securemail',
                        activity='com.nitrodesk.nitroid.NitroidMain',
                        username=username,
                        password=password,
                        workspace=workspace)
        self._email_password = email_password

    @staticmethod
    def sharetag(workspace=False, version=1000):
        return 'Work Mail' if workspace and version < 5.5 else ui.WorkMail.get('Send Email')

    def sharename(self, workspace=False, version=1000):
        return WorkMail.sharetag(workspace, version)

    def startup_once(self, param=None):
        extras = param['extras'] if param and 'extras' in param else None
        restart = param['restart'] if param and 'restart' in param else None
        Wrapped.initiate(self, extras=extras, restart=restart)
        self.accept_eula()
        if UiObj('/TextView[@package=%s][@text=%s]' % (self._packbund, ui.WorkMail.get('Awaiting Symantec Configuration'))).exists():
            activator = AndroidApp('com.activator.workmail', activity='.MainActivity')
            activator.prep().initiate()
            if not UiObj('/Button[@package=%s][@text="Activate Sealed Work Mail"]' % activator.packbund()).click():
                raise Exception('Failed to activate Sealed Work Mail from activator')
            time.sleep(5)
            activator.stop()
        workspace = param['workspace'] if param and 'workspace' in param and param['workspace'] else self._workspace
        self.join_workspace(workspace['name'])
        WorkHub().allow_workspace_request()
        if param and 'login_required' in param and param['login_required'] == True:
            if not self.is_login_prompted():
                raise Exception('Login is not prompted')
        username = param['username'] if param and 'username' in param and param['username'] else self._username
        password = param['password'] if param and 'password' in param and param['password'] else self._password
        self.login(username, password)
        self.accept_eula()
        self.wait_for_complete()
        if UiObj('/TextView[@package=%s][@text=%s]' % (self._packbund, ui.WorkMail.get('Device Configuration Wizard'))).exists():
            if not UiObj('/TextView[@text=%s]' % ui.WorkMail.get('Password')).exists():
                raise Exception('Failed to configure Work Mail: No Password label')
            if self._email_password:
                if not UiObj('/EditText[@index=5]').set_text(self._email_password):
                    raise Exception('Failed to configure Work Mail: No Password edit box')
            else:
                logger.debug('WorkMail.startup: Assuming password is already set...')
            if not UiObj('/Button[@text=%s]' % ui.WorkMail.get('Next')).click():
                raise Exception('Failed to configure Work Mail: No Next button')
            if not self.wait_for_complete():
                raise Exception('Failed to configure Work Mail: Configuration timed out')
            if not UiObj('/TextView[@package=%s][contains(@text,%s)]' % (self._packbund, ui.WorkMail.get('Finished configuration'))).exists():
                raise Exception('Failed to configure Work Mail: Configuration failed due to any reason')
            if not UiObj('/Button[@text=%s]' % ui.WorkMail.get('Close')).click():
                raise Exception('Failed to configure Work Mail: No Close button')
            self.wait_for_complete()
        if self.is_android_error():
            raise Exception('Failed to configure Work Mail: Android error')
        if not self.is_main_page():
            raise Exception('Failed to start Work Mail: Main page is not on screen')
        return self

    def accept_eula(self):
        accept = UiObj('/Button[@package=%s][@text=%s]' % (self._packbund, ui.WorkMail.get('I Accept')))
        if UiObj('/TextView[@text=%s]' % ui.WorkMail.get('License Agreement')).exists() and accept.exists():
            accept.click()
            if not self.wait_for_complete():
                raise Exception('Failed to initiate Work Mail: License Agreement process timed out (1)')
            if UiObj('/TextView[@text=%s]' % ui.WorkMail.get('Confirm')).exists() and accept.exists():
                accept.click()
                if not self.wait_for_complete():
                    raise Exception('Failed to initiate Work Mail: License Agreement process timed out (2)')
        return True

    def is_main_page(self):
        if not UiObj('/TextView[@package=%s][matches(@resource,".*mainViewStatusLine1")]' % self._packbund).exists():
            return False
        if not UiObj('/ScrollView[@package=%s][matches(@resource,".*buttonScrollview")]' % self._packbund).exists():
            return False
        return True

    def switch_pane(self, pane):
        if self.is_main_page():
            pane_switch = {'email': 0, 'calendar': 1, 'contact': 2, 'contacts': 2, 'task': 3, 'tasks': 3, 'newemail': 4}
            if pane not in pane_switch:
                raise Exception('Failed to switch pane on Work Mail: Invalid pane name %s' % pane)
            if not UiObj('/ScrollView[@package=%s]' % self._packbund).exists():
                raise Exception('Failed to switch pane on Work Mail: No container view for buttons on main page')
            button = UiObj('/ImageButton[@index=%d]' % pane_switch[pane])
            if not button.exists():
                raise Exception('Failed to switch pane on Work Mail: No button for index %d' % pane_switch[pane])
            button.click()
        else:
            raise Exception('Failed to switch pane on Work Mail: Not implemented yet')
        return self

    def switch_tab(self, tab):
        container = UiObj('/TabWidget[@package=%s][@instance=0]' % self._packbund)
        if not container.exists():
            raise Exception('Failed to switch tab on Work Mail: No TabWidget')
        button = container.get_child('/TextView[@text=%s]' % tab)
        if not button.exists():
            raise Exception('Failed to switch tab on Work Mail: No tab button %s' % tab)
        button.click()

    def receive_document(self, verify):
        self.login()
        self.switch_tab(ui.WorkMail.get('Message'))
        body = UiObj('/ScrollView[@index=1]/LinearLayout[@index=0]/EditText[@index=1]')
        if not body.exists():
            raise Exception('Failed to receive text on Work Mail: Message body does not exist')
        current = body.get_text()
        if current == verify:
            logger.debug('WorkMail.receive_document: Received text is verified.')
        else:
            raise Exception('Failed to receive text on Work Mail: Message body text does not match the shared text')
        if self.is_android_error():
            raise Exception('Failed to receive text on Work Mail: Android error')
        if not self.is_app_foreground():
            raise Exception('Failed to receive text on Work Mail: Eventually app is not on screen')
        return self

    def browse_web(self, url):
        tasklist = UiObj('/ListView[matches(@resource,".*lstTasks")]')
        if not tasklist.exists():
            self.switch_pane('tasks')
            if not tasklist.exists():
                raise Exception('Failed to open Web page from Work Mail: Tasks list not found')
        item = tasklist.get_child('/TextView[@text=%s]' % url)
        if not item.exists():
            # if item does not exist, add it
            button = UiObj('/TableLayout[@index=1]/ImageButton[@index=4]')
            if not button.click():
                raise Exception('Failed to open Web page from Work Mail: No button to add a new task item')
            time.sleep(0.5)
            UiObj('/ScrollView[@index=1]/LinearLayout[@index=0]/EditText[@index=1]').set_text(url)
            UiObj('/TableLayout[@index=0]/ImageButton[matches(@resource,".*btnCreate")]').click()
            time.sleep(1)
            if not item.exists():
                raise Exception('Failed to open Web page from Work Mail: Cannot create a task of the URL %s' % url)
        item.click()
        time.sleep(1)
        link = UiObj('/TextView[@text=%s]' % url)
        if not link.exists():
            raise Exception('Failed to open Web page from Work Mail: No link of the URL')
        link.click()
        time.sleep(1)
        if self.is_android_error():
            raise Exception('Failed to open Web page from Work Mail: Android error')
        return self


class WorkMail(WorkMailCore):
    def __init__(self):
        WorkMailCore.__init__(self,
                              username=settings.server.username,
                              password=settings.server.password,
                              workspace=dict(packbund=connection.workhub_packbund(),
                                             name=settings.server.workhub),
                              email_password=settings.server.email_password)
