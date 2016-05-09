import time
from datetime import datetime

from helper import connection, logger
from helper.android import android_device
from apps.android.workhub import WorkHub
from apps.android.workweb import WorkWeb
from apps.android.swa import TWText, TWEdit
from apps.android.taoneapp import TAoneApp, TAoneUtil
from testbase import TestBase


def generate_copytext():
    return 'COPYTEXT%s' % datetime.today().strftime('%H%M%S')

_copytext = ''


def test_copy_text(app, block=False):
    global _copytext
    _copytext = generate_copytext()
    logger.info('Copying text "%s"...' % _copytext)
    app.startup(param=dict(extras=dict(do='copytext2')))
    app.copy_text(text=_copytext, block=block)


def test_paste_text(app, clipboard, block=False):
    global _copytext
    app.startup(param=dict(extras=dict(do='pastetext2')))
    app.paste_text(clipboard=clipboard, verify=_copytext, block=block)


class CABST_Copy_App(TestBase):
    def __init__(self, app, policy, block=False):
        TestBase.__init__(self)
        self._desc = 'Copy text on ???? (clipboard_sharing=????)'
        self._app = app
        self._policy = policy
        self._block = block

    def run(self):
        status = True
        try:
            self.start()
            test_copy_text(self._app().prep(self._policy), self._block)
            self.complete()
        except Exception as e:
            self.abend(e, take_log=True, take_screenshot=True)
            self.post_error()
            status = False
        self._app().stop()
        return status


class CABST_Paste_App_From(TestBase):
    def __init__(self, app, policy, clipboard, block=False):
        TestBase.__init__(self)
        self._desc = 'Paste text on ????? (clipboard_sharing=?????) from ????? clipboard - copied on ?????'
        self._app = app
        self._policy = policy
        self._clipboard = clipboard
        self._block = block

    def run(self):
        global _copytext
        try:
            self.start()
            test_paste_text(self._app().prep(self._policy), self._clipboard, block=self._block)
            self.complete()
        except Exception as e:
            self.abend(e, take_log=True, take_screenshot=True)
            self.post_error()
        self._app().stop()


class C0001_Copy_WorkWeb_All(CABST_Copy_App):
    def __init__(self):
        CABST_Copy_App.__init__(self, WorkWeb, 'xTA - default')
        self._desc = 'Copy text on Work Web (clipboard_sharing=allow)'


class C0001s01_Paste_WorkWeb_All_From_WorkWeb_All(CABST_Paste_App_From):
    def __init__(self):
        CABST_Paste_App_From.__init__(self, WorkWeb, 'xTA - default', 'system')
        self._desc = 'Paste text on Work Web (clipboard_sharing=allow) from system clipboard - copied on Work Web'
        self._dependencies.append('T032.C0001_Copy_WorkWeb_All')


class C0001s02_Paste_SWA_All_From_WorkWeb_All(CABST_Paste_App_From):
    def __init__(self):
        CABST_Paste_App_From.__init__(self, TWEdit, 'xTA - default', 'system')
        self._desc = 'Paste text on Secure Web App (clipboard_sharing=allow) from system clipboard - copied on Work Web'
        self._dependencies.append('T032.C0001_Copy_WorkWeb_All')


class C0001s03_Paste_WrappedApp_All_From_WorkWeb_All(CABST_Paste_App_From):
    def __init__(self):
        CABST_Paste_App_From.__init__(self, TAoneApp, 'xTA - default', 'system')
        self._desc = 'Paste text on Wrapped Native App (clipboard_sharing=allow) ' + \
                     'from system clipboard - copied on Work Web'
        self._dependencies.append('T032.C0001_Copy_WorkWeb_All')


class C0001s09_Paste_Unwrapped_From_WorkWeb_All(CABST_Paste_App_From):
    def __init__(self):
        CABST_Paste_App_From.__init__(self, TAoneUtil, None, 'none')
        self._desc = 'Paste text on Unwrapped Native App from system clipboard - copied on Work Web'
        self._dependencies.append('T032.C0001_Copy_WorkWeb_All')


class C0001s11_Paste_WorkWeb_WS_From_WorkWeb_All(CABST_Paste_App_From):
    def __init__(self):
        CABST_Paste_App_From.__init__(self, WorkWeb, 'xTA - clipboard - workspace', 'system')
        self._desc = 'Paste text on WorkWeb (clipboard_sharing=workspace) from system clipboard - copied on Work Web'
        self._dependencies.append('T032.C0001_Copy_WorkWeb_All')


class C0001s12_Paste_SWA_WS_From_WorkWeb_All(CABST_Paste_App_From):
    def __init__(self):
        CABST_Paste_App_From.__init__(self, TWEdit, 'xTA - clipboard - workspace', 'system')
        self._desc = 'Paste text on Secure Web App (clipboard_sharing=workspace) ' + \
                     'from system clipboard - copied on Work Web'
        self._dependencies.append('T032.C0001_Copy_WorkWeb_All')


class C0001s13_Paste_WrappedApp_WS_From_WorkWeb_All(CABST_Paste_App_From):
    def __init__(self):
        CABST_Paste_App_From.__init__(self, TAoneApp, 'xTA - clipboard - workspace', 'system')
        self._desc = 'Paste text on Wrapped Native App (clipboard_sharing=workspace) ' + \
                     'from system clipboard - copied on Work Web'
        self._dependencies.append('T032.C0001_Copy_WorkWeb_All')


class C0001s21_Paste_WorkWeb_Block_From_WorkWeb_All(CABST_Paste_App_From):
    def __init__(self):
        CABST_Paste_App_From.__init__(self, WorkWeb, 'xTA - clipboard - block', 'system')
        self._desc = 'Paste text on WorkWeb (clipboard_sharing=block) from system clipboard - copied on Work Web'
        self._dependencies.append('T032.C0001_Copy_WorkWeb_All')


class C0001s22_Paste_SWA_Block_From_WorkWeb_All(CABST_Paste_App_From):
    def __init__(self):
        CABST_Paste_App_From.__init__(self, TWEdit, 'xTA - clipboard - block', 'system')
        self._desc = 'Paste text on Secure Web App (clipboard_sharing=block) ' + \
                     'from system clipboard - copied on Work Web'
        self._dependencies.append('T032.C0001_Copy_WorkWeb_All')


class C0001s23_Paste_WrappedApp_Block_From_WorkWeb_All(CABST_Paste_App_From):
    def __init__(self):
        CABST_Paste_App_From.__init__(self, TAoneApp, 'xTA - clipboard - block', 'system')
        self._desc = 'Paste text on Wrapped Native App (clipboard_sharing=block) ' + \
                     'from system clipboard - copied on Work Web'
        self._dependencies.append('T032.C0001_Copy_WorkWeb_All')


class C0002_Copy_SWA_All(CABST_Copy_App):
    def __init__(self):
        CABST_Copy_App.__init__(self, TWEdit, 'xTA - default')
        self._desc = 'Copy text on Secure Web App (clipboard_sharing=allow)'


class C0002s01_Paste_WorkWeb_All_From_SWA_All(CABST_Paste_App_From):
    def __init__(self):
        CABST_Paste_App_From.__init__(self, WorkWeb, 'xTA - default', 'system')
        self._desc = 'Paste text on Work Web (clipboard_sharing=allow) ' + \
                     'from system clipboard - copied on Secure Web App'
        self._dependencies.append('T032.C0002_Copy_SWA_All')


class C0002s02_Paste_SWA_All_From_SWA_All(CABST_Paste_App_From):
    def __init__(self):
        CABST_Paste_App_From.__init__(self, TWEdit, 'xTA - default', 'system')
        self._desc = 'Paste text on Secure Web App (clipboard_sharing=allow) ' + \
                     'from system clipboard - copied on Secure Web App'
        self._dependencies.append('T032.C0002_Copy_SWA_All')


class C0002s03_Paste_WrappedApp_All_From_SWA_All(CABST_Paste_App_From):
    def __init__(self):
        CABST_Paste_App_From.__init__(self, TAoneApp, 'xTA - default', 'system')
        self._desc = 'Paste text on Wrapped Native App (clipboard_sharing=allow) ' + \
                     'from system clipboard - copied on Secure Web App'
        self._dependencies.append('T032.C0002_Copy_SWA_All')


class C0002s09_Paste_Unwrapped_From_SWA_All(CABST_Paste_App_From):
    def __init__(self):
        CABST_Paste_App_From.__init__(self, TAoneUtil, None, 'none')
        self._desc = 'Paste text on Unwrapped Native App from system clipboard - copied on Secure Web App'
        self._dependencies.append('T032.C0002_Copy_SWA_All')


class C0002s11_Paste_WorkWeb_WS_From_SWA_All(CABST_Paste_App_From):
    def __init__(self):
        CABST_Paste_App_From.__init__(self, WorkWeb, 'xTA - clipboard - workspace', 'system')
        self._desc = 'Paste text on Work Web (clipboard_sharing=workspace) ' + \
                     'from system clipboard - copied on Secure Web App'
        self._dependencies.append('T032.C0002_Copy_SWA_All')


class C0002s12_Paste_SWA_WS_From_SWA_All(CABST_Paste_App_From):
    def __init__(self):
        CABST_Paste_App_From.__init__(self, TWEdit, 'xTA - clipboard - workspace', 'system')
        self._desc = 'Paste text on Secure Web App (clipboard_sharing=workspace) ' + \
                     'from system clipboard - copied on Secure Web App'
        self._dependencies.append('T032.C0002_Copy_SWA_All')


class C0002s13_Paste_WrappedApp_WS_From_SWA_All(CABST_Paste_App_From):
    def __init__(self):
        CABST_Paste_App_From.__init__(self, TAoneApp, 'xTA - clipboard - workspace', 'system')
        self._desc = 'Paste text on Wrapped Native App (clipboard_sharing=workspace) ' + \
                     'from system clipboard - copied on Secure Web App'
        self._dependencies.append('T032.C0002_Copy_SWA_All')


class C0002s21_Paste_WorkWeb_Block_From_SWA_All(CABST_Paste_App_From):
    def __init__(self):
        CABST_Paste_App_From.__init__(self, WorkWeb, 'xTA - clipboard - block', 'system')
        self._desc = 'Paste text on Work Web (clipboard_sharing=block) ' + \
                     'from system clipboard - copied on Secure Web App'
        self._dependencies.append('T032.C0002_Copy_SWA_All')


class C0002s22_Paste_SWA_Block_From_SWA_All(CABST_Paste_App_From):
    def __init__(self):
        CABST_Paste_App_From.__init__(self, TWEdit, 'xTA - clipboard - block', 'system')
        self._desc = 'Paste text on Secure Web App (clipboard_sharing=block) ' + \
                     'from system clipboard - copied on Secure Web App'
        self._dependencies.append('T032.C0002_Copy_SWA_All')


class C0002s23_Paste_WrappedApp_Block_From_SWA_All(CABST_Paste_App_From):
    def __init__(self):
        CABST_Paste_App_From.__init__(self, TAoneApp, 'xTA - clipboard - block', 'system')
        self._desc = 'Paste text on Wrapped Native App (clipboard_sharing=block) ' + \
                     'from system clipboard - copied on Secure Web App'
        self._dependencies.append('T032.C0002_Copy_SWA_All')


class C0003_Copy_WrappedApp_All(CABST_Copy_App):
    def __init__(self):
        CABST_Copy_App.__init__(self, TAoneApp, 'xTA - default')
        self._desc = 'Copy text on Wrapped Native App (clipboard_sharing=allow)'


class C0003s01_Paste_WorkWeb_All_From_WrappedApp_All(CABST_Paste_App_From):
    def __init__(self):
        CABST_Paste_App_From.__init__(self, WorkWeb, 'xTA - default', 'system')
        self._desc = 'Paste text on Work Web (clipboard_sharing=allow) ' + \
                     'from system clipboard - copied on Wrapped Native App'
        self._dependencies.append('T032.C0003_Copy_WrappedApp_All')


class C0003s02_Paste_SWA_All_From_WrappedApp_All(CABST_Paste_App_From):
    def __init__(self):
        CABST_Paste_App_From.__init__(self, TWEdit, 'xTA - default', 'system')
        self._desc = 'Paste text on Secure Web App (clipboard_sharing=allow) ' + \
                     'from system clipboard - copied on Wrapped Native App'
        self._dependencies.append('T032.C0003_Copy_WrappedApp_All')


class C0003s03_Paste_WrappedApp_All_From_WrappedApp_All(CABST_Paste_App_From):
    def __init__(self):
        CABST_Paste_App_From.__init__(self, TAoneApp, 'xTA - default', 'system')
        self._desc = 'Paste text on Wrapped Native App (clipboard_sharing=allow) ' + \
                     'from system clipboard - copied on Wrapped Native App'
        self._dependencies.append('T032.C0003_Copy_WrappedApp_All')


class C0003s09_Paste_Unwrapped_From_WrappedApp_All(CABST_Paste_App_From):
    def __init__(self):
        CABST_Paste_App_From.__init__(self, TAoneUtil, None, 'none')
        self._desc = 'Paste text on Unwrapped Native App from system clipboard - copied on Wrapped Native App'
        self._dependencies.append('T032.C0003_Copy_WrappedApp_All')


class C0003s11_Paste_WorkWeb_WS_From_WrappedApp_All(CABST_Paste_App_From):
    def __init__(self):
        CABST_Paste_App_From.__init__(self, WorkWeb, 'xTA - clipboard - workspace', 'system')
        self._desc = 'Paste text on Work Web (clipboard_sharing=workspace) ' + \
                     'from system clipboard - copied on Wrapped Native App'
        self._dependencies.append('T032.C0003_Copy_WrappedApp_All')


class C0003s12_Paste_SWA_WS_From_WrappedApp_All(CABST_Paste_App_From):
    def __init__(self):
        CABST_Paste_App_From.__init__(self, TWEdit, 'xTA - clipboard - workspace', 'system')
        self._desc = 'Paste text on Secure Web App (clipboard_sharing=workspace) ' + \
                     'from system clipboard - copied on Wrapped Native App'
        self._dependencies.append('T032.C0003_Copy_WrappedApp_All')


class C0003s13_Paste_WrappedApp_WS_From_WrappedApp_All(CABST_Paste_App_From):
    def __init__(self):
        CABST_Paste_App_From.__init__(self, TAoneApp, 'xTA - clipboard - workspace', 'system')
        self._desc = 'Paste text on Wrapped Native App (clipboard_sharing=workspace) ' + \
                     'from system clipboard - copied on Wrapped Native App'
        self._dependencies.append('T032.C0003_Copy_WrappedApp_All')


class C0003s21_Paste_WorkWeb_Block_From_WrappedApp_All(CABST_Paste_App_From):
    def __init__(self):
        CABST_Paste_App_From.__init__(self, WorkWeb, 'xTA - clipboard - block', 'system')
        self._desc = 'Paste text on Work Web (clipboard_sharing=block) ' + \
                     'from system clipboard - copied on Wrapped Native App'


class C0003s22_Paste_SWA_Block_From_WrappedApp_All(CABST_Paste_App_From):
    def __init__(self):
        CABST_Paste_App_From.__init__(self, TWEdit, 'xTA - clipboard - block', 'system')
        self._desc = 'Paste text on Secure Web App (clipboard_sharing=block) ' + \
                     'from system clipboard - copied on Wrapped Native App'
        self._dependencies.append('T032.C0003_Copy_WrappedApp_All')


class C0003s23_Paste_WrappedApp_Block_From_WrappedApp_All(CABST_Paste_App_From):
    def __init__(self):
        CABST_Paste_App_From.__init__(self, TAoneApp, 'xTA - clipboard - block', 'system')
        self._desc = 'Paste text on Wrapped Native App (clipboard_sharing=block) ' + \
                     'from system clipboard - copied on Wrapped Native App'


class C0011_Copy_WorkWeb_WS(CABST_Copy_App):
    def __init__(self):
        CABST_Copy_App.__init__(self, WorkWeb, 'xTA - clipboard - workspace')
        self._desc = 'Copy text on Work Web (clipboard_sharing=workspace)'


class C0011s01_Paste_WorkWeb_All_From_WorkWeb_WS(CABST_Paste_App_From):
    def __init__(self):
        CABST_Paste_App_From.__init__(self, WorkWeb, 'xTA - default', 'workspace')
        self._desc = 'Paste on Work Web (clipboard_sharing=allow) from workspace clipboard - copied on Work Web'
        self._dependencies.append('T032.C0011_Copy_WorkWeb_WS')


class C0011s02_Paste_SWA_All_From_WorkWeb_WS(CABST_Paste_App_From):
    def __init__(self):
        CABST_Paste_App_From.__init__(self, TWEdit, 'xTA - default', 'workspace')
        self._desc = 'Paste text on Secure Web App (clipboard_sharing=allow) ' + \
                     'from workspace clipboard - copied on Work Web'
        self._dependencies.append('T032.C0011_Copy_WorkWeb_WS')


class C0011s03_Paste_WrappedApp_All_From_WorkWeb_WS(CABST_Paste_App_From):
    def __init__(self):
        CABST_Paste_App_From.__init__(self, TAoneApp, 'xTA - default', 'workspace')
        self._desc = 'Paste text on Wrapped Native App (clipboard_sharing=allow) ' + \
                     'from workspace clipboard - copied on Work Web'
        self._dependencies.append('T032.C0011_Copy_WorkWeb_WS')


class C0011s09_Paste_Unwrapped_From_WorkWeb_WS(CABST_Paste_App_From):
    def __init__(self):
        CABST_Paste_App_From.__init__(self, TAoneUtil, None, 'none', True)
        self._desc = 'Cannot paste text on Unwrapped Native App from workspace clipboard - copied on Work Web'
        self._dependencies.append('T032.C0011_Copy_WorkWeb_WS')


class C0011s11_Paste_WorkWeb_WS_From_WorkWeb_WS(CABST_Paste_App_From):
    def __init__(self):
        CABST_Paste_App_From.__init__(self, WorkWeb, 'xTA - clipboard - workspace', 'workspace')
        self._desc = 'Paste text on Work Web (clipboard_sharing=workspace) ' + \
                     'from workspace clipboard - copied on Work Web'
        self._dependencies.append('T032.C0011_Copy_WorkWeb_WS')


class C0011s12_Paste_SWA_WS_From_WorkWeb_WS(CABST_Paste_App_From):
    def __init__(self):
        CABST_Paste_App_From.__init__(self, TWEdit, 'xTA - clipboard - workspace', 'workspace')
        self._desc = 'Paste text on Secure Web App (clipboard_sharing=workspace) ' + \
                     'from workspace clipboard - copied on Work Web'
        self._dependencies.append('T032.C0011_Copy_WorkWeb_WS')


class C0011s13_Paste_WrappedApp_WS_From_WorkWeb_WS(CABST_Paste_App_From):
    def __init__(self):
        CABST_Paste_App_From.__init__(self, TAoneApp, 'xTA - clipboard - workspace', 'workspace')
        self._desc = 'Paste text on Wrapped Native App (clipboard_sharing=workspace) ' + \
                     'from workspace clipboard - copied on Work Web'
        self._dependencies.append('T032.C0011_Copy_WorkWeb_WS')


class C0011s21_Paste_WorkWeb_Block_From_WorkWeb_WS(CABST_Paste_App_From):
    def __init__(self):
        CABST_Paste_App_From.__init__(self, WorkWeb, 'xTA - clipboard - block', 'workspace')
        self._desc = 'Paste text on Work Web (clipboard_sharing=block) ' + \
                     'from workspace clipboard - copied on Work Web'
        self._dependencies.append('T032.C0011_Copy_WorkWeb_WS')


class C0011s22_Paste_SWA_Block_From_WorkWeb_WS(CABST_Paste_App_From):
    def __init__(self):
        CABST_Paste_App_From.__init__(self, TWEdit, 'xTA - clipboard - block', 'workspace')
        self._desc = 'Paste text on Secure Web App (clipboard_sharing=block) ' + \
                     'from workspace clipboard - copied on Work Web'
        self._dependencies.append('T032.C0011_Copy_WorkWeb_WS')


class C0011s23_Paste_WrappedApp_Block_From_WorkWeb_WS(CABST_Paste_App_From):
    def __init__(self):
        CABST_Paste_App_From.__init__(self, TAoneApp, 'xTA - clipboard - block', 'workspace')
        self._desc = 'Paste text on Wrapped Native App (clipboard_sharing=block) ' + \
                     'from workspace clipboard - copied on Work Web'
        self._dependencies.append('T032.C0011_Copy_WorkWeb_WS')


class C0012_Copy_SWA_WS(CABST_Copy_App):
    def __init__(self):
        CABST_Copy_App.__init__(self, TWEdit, 'xTA - clipboard - workspace')
        self._desc = 'Copy text on Secure Web App (clipboard_sharing=workspace)'


class C0012s01_Paste_WorkWeb_All_From_SWA_WS(CABST_Paste_App_From):
    def __init__(self):
        CABST_Paste_App_From.__init__(self, WorkWeb, 'xTA - default', 'workspace')
        self._desc = 'Paste text on Work Web (clipboard_sharing=allow) ' + \
                     'from workspace clipboard - copied on Secure Web App'
        self._dependencies.append('T032.C0012_Copy_SWA_WS')


class C0012s02_Paste_SWA_All_From_SWA_WS(CABST_Paste_App_From):
    def __init__(self):
        CABST_Paste_App_From.__init__(self, TWEdit, 'xTA - default', 'workspace')
        self._desc = 'Paste text on Secure Web App (clipboard_sharing=allow) ' + \
                     'from workspace clipboard - copied on Secure Web App'
        self._dependencies.append('T032.C0012_Copy_SWA_WS')


class C0012s03_Paste_WrappedApp_All_From_SWA_WS(CABST_Paste_App_From):
    def __init__(self):
        CABST_Paste_App_From.__init__(self, TAoneApp, 'xTA - default', 'workspace')
        self._desc = 'Paste text on Wrapped Native App (clipboard_sharing=allow) ' + \
                     'from workspace clipboard - copied on Secure Web App'
        self._dependencies.append('T032.C0012_Copy_SWA_WS')


class C0012s09_Paste_Unwrapped_From_SWA_WS(CABST_Paste_App_From):
    def __init__(self):
        CABST_Paste_App_From.__init__(self, TAoneUtil, None, 'none', True)
        self._desc = 'Cannot paste text on Unwrapped Native App from workspace clipboard - copied on Secure Web App'
        self._dependencies.append('T032.C0012_Copy_SWA_WS')


class C0012s11_Paste_WorkWeb_WS_From_SWA_WS(CABST_Paste_App_From):
    def __init__(self):
        CABST_Paste_App_From.__init__(self, WorkWeb, 'xTA - clipboard - workspace', 'workspace')
        self._desc = 'Paste text on Work Web (clipboard_sharing=workspace) ' + \
                     'from workspace clipboard - copied on Secure Web App'
        self._dependencies.append('T032.C0012_Copy_SWA_WS')


class C0012s12_Paste_SWA_WS_From_SWA_WS(CABST_Paste_App_From):
    def __init__(self):
        CABST_Paste_App_From.__init__(self, TWEdit, 'xTA - clipboard - workspace', 'workspace')
        self._desc = 'Paste text on Secure Web App (clipboard_sharing=workspace) ' + \
                     'from workspace clipboard - copied on Secure Web App'
        self._dependencies.append('T032.C0012_Copy_SWA_WS')


class C0012s13_Paste_WrappedApp_WS_From_SWA_WS(CABST_Paste_App_From):
    def __init__(self):
        CABST_Paste_App_From.__init__(self, TAoneApp, 'xTA - clipboard - workspace', 'workspace')
        self._desc = 'Paste text on Wrapped Native App (clipboard_sharing=workspace) ' + \
                     'from workspace clipboard - copied on Secure Web App'
        self._dependencies.append('T032.C0012_Copy_SWA_WS')


class C0012s21_Paste_WorkWeb_Block_From_SWA_WS(CABST_Paste_App_From):
    def __init__(self):
        CABST_Paste_App_From.__init__(self, WorkWeb, 'xTA - clipboard - block', 'workspace')
        self._desc = 'Paste text on Work Web (clipboard_sharing=block) ' + \
                     'from workspace clipboard - copied on Secure Web App'
        self._dependencies.append('T032.C0012_Copy_SWA_WS')


class C0012s22_Paste_SWA_Block_From_SWA_WS(CABST_Paste_App_From):
    def __init__(self):
        CABST_Paste_App_From.__init__(self, TWEdit, 'xTA - clipboard - block', 'workspace')
        self._desc = 'Paste text on Secure Web App (clipboard_sharing=block) ' + \
                     'from workspace clipboard - copied on Secure Web App'
        self._dependencies.append('T032.C0012_Copy_SWA_WS')


class C0012s23_Paste_WrappedApp_Block_From_SWA_WS(CABST_Paste_App_From):
    def __init__(self):
        CABST_Paste_App_From.__init__(self, TAoneApp, 'xTA - clipboard - block', 'workspace')
        self._desc = 'Paste text on Wrapped Native App (clipboard_sharing=block) ' + \
                     'from workspace clipboard - copied on Secure Web App'
        self._dependencies.append('T032.C0012_Copy_SWA_WS')


class C0013_Copy_WrappedApp_WS(CABST_Copy_App):
    def __init__(self):
        CABST_Copy_App.__init__(self, TAoneApp, 'xTA - clipboard - workspace')
        self._desc = 'Copy text on Wrapped Native App (clipboard_sharing=workspace)'


class C0013s01_Paste_WorkWeb_All_From_WrappedApp_WS(CABST_Paste_App_From):
    def __init__(self):
        CABST_Paste_App_From.__init__(self, WorkWeb, 'xTA - default', 'workspace')
        self._desc = 'Paste text on Work Web (clipboard_sharing=allow) ' + \
                     'from workspace clipboard - copied on Wrapped Native App'
        self._dependencies.append('T032.C0013_Copy_WrappedApp_WS')


class C0013s02_Paste_SWA_All_From_WrappedApp_WS(CABST_Paste_App_From):
    def __init__(self):
        CABST_Paste_App_From.__init__(self, TWEdit, 'xTA - default', 'workspace')
        self._desc = 'Paste text on Secure Web App (clipboard_sharing=allow) ' + \
                     'from workspace clipboard - copied on Wrapped Native App'
        self._dependencies.append('T032.C0013_Copy_WrappedApp_WS')


class C0013s03_Paste_WrappedApp_All_From_WrappedApp_WS(CABST_Paste_App_From):
    def __init__(self):
        CABST_Paste_App_From.__init__(self, TAoneApp, 'xTA - default', 'workspace')
        self._desc = 'Paste text on Wrapped Native App (clipboard_sharing=allow) ' + \
                     'from workspace clipboard - copied on Wrapped Native App'
        self._dependencies.append('T032.C0013_Copy_WrappedApp_WS')


class C0013s09_Paste_Unwrapped_From_WrappedApp_WS(CABST_Paste_App_From):
    def __init__(self):
        CABST_Paste_App_From.__init__(self, TAoneUtil, None, 'none', True)
        self._desc = 'Cannot paste text on Unwrapped Native App from workspace clipboard - copied on Wrapped Native App'
        self._dependencies.append('T032.C0013_Copy_WrappedApp_WS')


class C0013s11_Paste_WorkWeb_WS_From_WrappedApp_WS(CABST_Paste_App_From):
    def __init__(self):
        CABST_Paste_App_From.__init__(self, WorkWeb, 'xTA - clipboard - workspace', 'workspace')
        self._desc = 'Paste text on Work Web (clipboard_sharing=workspace) ' + \
                     'from workspace clipboard - copied on Wrapped Native App'
        self._dependencies.append('T032.C0013_Copy_WrappedApp_WS')


class C0013s12_Paste_SWA_WS_From_WrappedApp_WS(CABST_Paste_App_From):
    def __init__(self):
        CABST_Paste_App_From.__init__(self, TWEdit, 'xTA - clipboard - workspace', 'workspace')
        self._desc = 'Paste text on Secure Web App (clipboard_sharing=workspace) ' + \
                     'from workspace clipboard - copied on Wrapped Native App'
        self._dependencies.append('T032.C0013_Copy_WrappedApp_WS')


class C0013s13_Paste_WrappedApp_WS_From_WrappedApp_WS(CABST_Paste_App_From):
    def __init__(self):
        CABST_Paste_App_From.__init__(self, TAoneApp, 'xTA - clipboard - workspace', 'workspace')
        self._desc = 'Paste text on Wrapped Native App (clipboard_sharing=workspace) ' + \
                     'from system clipboard - copied on Wrapped Native App'
        self._dependencies.append('T032.C0013_Copy_WrappedApp_WS')


class C0013s21_Paste_WorkWeb_Block_From_WrappedApp_WS(CABST_Paste_App_From):
    def __init__(self):
        CABST_Paste_App_From.__init__(self, WorkWeb, 'xTA - clipboard - block', 'workspace')
        self._desc = 'Paste text on Work Web (clipboard_sharing=block) ' + \
                     'from workspace clipboard - copied on Wrapped Native App'
        self._dependencies.append('T032.C0013_Copy_WrappedApp_WS')


class C0013s22_Paste_SWA_Block_From_WrappedApp_WS(CABST_Paste_App_From):
    def __init__(self):
        CABST_Paste_App_From.__init__(self, TWEdit, 'xTA - clipboard - block', 'workspace')
        self._desc = 'Paste text on Secure Web App (clipboard_sharing=block) ' + \
                     'from workspace clipboard - copied on Wrapped Native App'
        self._dependencies.append('T032.C0013_Copy_WrappedApp_WS')


class C0013s23_Paste_WrappedApp_Block_From_WrappedApp_WS(CABST_Paste_App_From):
    def __init__(self):
        CABST_Paste_App_From.__init__(self, TAoneApp, 'xTA - clipboard - block', 'workspace')
        self._desc = 'Paste text on Wrapped Native App (clipboard_sharing=block) ' + \
                     'from workspace clipboard - copied on Wrapped Native App'
        self._dependencies.append('T032.C0013_Copy_WrappedApp_WS')


class C0021_Copy_WorkWeb_Block(TestBase):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Cannot copy text on Work Web (clipboard_sharing=block)'

    def run(self):
        global _copytext
        status = True
        try:
            self.start()
            ww = WorkWeb().prep('xTA - clipboard - block')
            test_copy_text(ww, block=True)
            # verifying copy is blocked
            ww.paste_text(clipboard='system', verify=_copytext, block=True)
            ww.paste_text(clipboard='workspace', verify=_copytext, block=True)
            self.complete()
        except Exception as e:
            self.abend(e, take_log=True, take_screenshot=True)
            self.post_error()
            status = False
        WorkWeb().stop()
        return status


class C0022_Copy_SWA_Block(TestBase):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Cannot copy text on Secure Web App (clipboard_sharing=block)'

    def run(self):
        global _copytext
        status = True
        try:
            self.start()
            wa = TWEdit().prep('xTA - clipboard - block')
            test_copy_text(wa, block=True)
            # verifying copy is blocked
            wa.paste_text(clipboard='none', verify=_copytext, block=True)
            self.complete()
        except Exception as e:
            self.abend(e, take_log=True, take_screenshot=True)
            self.post_error()
            status = False
        TWEdit().stop()
        return status


class C0023_Copy_WrappedApp_Block(TestBase):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Cannot copy text on Wrapped Native App (clipboard_sharing=block)'

    def run(self):
        status = True
        try:
            self.start()
            wa = TAoneApp().prep('xTA - clipboard - block')
            test_copy_text(wa, block=True)
            # verifying copy is blocked
            wa.startup(param=dict(extras=dict(do='pastetext2')))
            wa.paste_text(clipboard='system', verify=_copytext, block=True)
            wa.paste_text(clipboard='workspace', verify=_copytext, block=True)
            self.complete()
        except Exception as e:
            self.abend(e, take_log=True, take_screenshot=True)
            self.post_error()
            status = False
        TAoneApp().stop()
        return status


class C9002_Paste_WrappedApp_WS_And_Pause(TestBase):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Paste on Wrapped Native App (clipboard_sharing=workspace) ' + \
                     'from clipboard but once pause and go back to HOME screen, and then re-launch the App.' + '''
Steps:
  1. Install a Wrapped Native App with clipboard_sharing=workspace policy.
  2. Launch the App and copy any text to workspace clipboard.
  3. Paste the text --- Paste From dialog should appear.
  4. Without choosing System/Workspace, go back to HOME screen.
  5. From HOME screen, re-launch the App.
Expectation:
  The App's screen comes back.
ET# 3818802'''

    def run(self):
        global _copytext
        status = True
        try:
            self.start()
            logger.info('Copying text to workspace clipboard...')
            wa = TAoneApp().prep('xTA - clipboard - workspace')
            test_copy_text(wa)
            wa.stop()
            logger.info('Trying to paste text and pause...')
            wa.startup(param=dict(extras=dict(do='pastetext2')))
            wa.paste_text_from_menu(clipboard='stop', verify=None, block=False)
            android_device.send_key(android_device.KEY_HOME)
            time.sleep(5)
            wa.startup(param=dict(restart=False))
            wa.select_paste_from(clipboard='workspace', verify=_copytext, block=False)
            self.complete()
        except Exception as e:
            self.abend(e, take_log=True, take_screenshot=True)
            self.post_error()
            status = False
        TAoneApp().stop()
        return status


class C9003_Copy_HTML_SWA_WS(CABST_Copy_App):
    def __init__(self):
        CABST_Copy_App.__init__(self, TWText, 'xTA - clipboard - workspace')
        self._desc = '''Copy HTML content text on Secure Web App (clipboard_sharing=workspace)
Steps:
  1. Install a Secure Web App with clipboard_sharing=workspace policy.
  2. Launch the App and copy any HTML content text.
Expectation:
  The text is copied to workspace clipboard. No Paste From dialog appears.
ET# 3817114'''


class C9011_Paste_WrappedApp_WS_From_System_With_WS_Clipboard_Empty(TestBase):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Paste on Wrapped Native App (clipboard_sharing=workspace) ' +  \
                     'from system clipboard with workspace clipboard empty' + '''
Steps:
  1. Re-install Work Hub. (to make sure workspace clipboard is empty)
  2. Install a wrapped app with clipboard_sharing=workspace policy.
  3. Launch an unwrapped app and copy any text to system clipboard.
  4. Launch the wrapped app and paste the text.
Expectation:
  The copied text is pasted without showing up Paste From dialog.
ET# 3802974'''

    def run(self):
        status = True
        try:
            self.start()
            logger.info('Re-installing Work Hub...')
            WorkHub().reset(startup=True)
            logger.info('Copying text on unwrapped App...')
            test_copy_text(TAoneUtil().prep())
            logger.info('Pasting text on Wrapped Native App...')
            test_paste_text(TAoneApp().prep('xTA - clipboard - workspace'), 'none')
            self.complete()
        except Exception as e:
            self.abend(e, take_log=True, take_screenshot=True)
            self.post_error()
            status = False
        TAoneUtil().stop()
        TAoneApp().stop()
        return status


class C9012_Copy_Paste_SWA_WS_Just_After_Installing_WorkHub(TestBase):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Just after installing Work Hub and apps, copy text on a Secure Web App ' + \
                     '(clipboard_sharing=workspace) and then paste it on another Secure Web App ' + \
                     '(clipboard_sharing=workspace)' + '''
Steps:
  1. Disassociate the device.
  2. Re-install and launch Work Hub.
  3. Install a Secure Web App with clipboard_sharing=workspace policy.
  4. Launch the app and copy any text to workspace clipboard.
  5. Install another Secure Web App with clipboard_sharing=workspace policy.
  6. Launch the second app and paste text.
Expectation:
  The copied text is pasted successfully.
ET# 3802957'''

    def run(self):
        status = True
        try:
            self.start()
            logger.info('Disassociating device...')
            if not connection.disassociate_device_by_serial(android_device.get_serial()):
                raise Exception('Device cannot get disassociated')
            logger.info('Re-installing Work Hub...')
            WorkHub().reset(startup=True)
            logger.info('Copying text on a Secure Web App...')
            test_copy_text(TWEdit().prep('xTA - clipboard - workspace'))
            logger.info('Pasting text on another Secure Web App...')
            test_paste_text(TWEdit().prep('xTA - clipboard - workspace'), 'workspace')
            self.complete()
        except Exception as e:
            self.abend(e, take_log=True, take_screenshot=True)
            self.post_error()
            status = False
        TWEdit().stop()
        return status
