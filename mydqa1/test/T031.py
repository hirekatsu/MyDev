# -*- coding: utf-8 -*-
from datetime import datetime

from apps.android.workweb import WorkWeb
from apps.android.workmail import WorkMail
from apps.android.swa import TWText
from apps.android.taoneapp import TAoneApp, TAoneBuddy, TAoneUtil
from helper import logger
from testbase import TestBase


def generate_sharetext():
    return 'SHARETEXT%s' % datetime.today().strftime('%H%M%S')


def test_share_document(source_app, target_app, workspace=False):
    logger.debug('test_share_document: source_app=%s, target_app=%s, workspace=%s'
                 % (type(source_app), type(target_app), workspace))

    # from 5.5 wrap UI for share has been changed
    # but Work Web 1.7.138 is still using old Wrap Kit
    source_version = 5.4 if source_app.packbund() == 'com.symantec.mobile.securebrowser' else 5.5

    sharetext = generate_sharetext()
    logger.debug('test_share_document: sharing text=%s' % sharetext)
    logger.debug('test_share_document: preparing apps...')

    source_app.startup(param=dict(extras=dict(do='sharetext2')))
    source_app.share_document(sharetext)
    if not workspace:
        usable = ['TAoneApp', 'TAoneBuddy', 'TAoneUtil', WorkMail.sharetag(False, source_version)]
        unusable = None
    else:
        usable = ['TAoneApp', 'TAoneBuddy', WorkMail.sharetag(True, source_version)]
        unusable = ['TAoneUtil']
    source_app.openable(workspace=workspace,
                        block=False,
                        usable=usable,
                        unusable=unusable)
    source_app.open_with(app=target_app.sharename(workspace, source_version), workspace=workspace)
    target_app.receive_document(sharetext)


def test_block_share_document(wa):
    logger.debug('test_block_share_document: app=%s' % type(wa))
    sharetext = generate_sharetext()
    logger.debug('test_block_share_document: sharing text=%s' % sharetext)
    wa.prep(policy='xTA - document - block').startup(param=dict(extras=dict(do='sharetext2')))
    wa.share_document(sharetext)
    wa.openable(workspace=True, block=True, usable=None, unusable=None)


class CABST_Share_App(TestBase):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Share text on ???? (document_sharing=????) with ???? (document_sharing=????)'
        self._s_app = None
        self._s_policy = ''
        self._s_workspace = False
        self._t_app = None
        self._t_policy = ''


    def run(self):
        try:
            self.start()
            test_share_document(self._s_app().prep(self._s_policy),
                                self._t_app().prep(self._t_policy), self._s_workspace)
            self.complete()
        except Exception as e:
            self.abend(e, take_log=True, take_screenshot=True)
            self.post_error()
        self._s_app().stop()
        self._t_app().stop()


class C0000_Receiver_Apps(TestBase):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Launch wrapped apps that can receive shared text to register in workspace'

    def run(self, skip=False):
        def startone(app):
            result = True
            try:
                app().prep().startup()
            except Exception as e:
                import sys, traceback
                exc_type, exc_value, exc_tb = sys.exc_info()
                logger.debug(traceback.format_exception(exc_type, exc_value, exc_tb))
                self.get_log_file()
                self.get_screenshot()
                result = False
            app().stop()
            return result

        status = {}
        self.start()
        logger.info('Launching receiver apps...')
        if startone(TAoneApp):
            status['TAoneApp'] = True
        if startone(TAoneBuddy):
            status['TAoneBuddy'] = True
        if startone(TAoneUtil):
            status['TAoneUtil'] = True
        if startone(WorkMail):
            status['WorkMail'] = True
        for v in status:
            self.set_named_result(v, True)
        if len(status) == 4:
            self.complete()
            status = True
        else:
            self.abend(Exception('Failed to prepare one of receiver apps: %s' % str(status)), take_log=True, take_screenshot=True)
            self.post_error()
            status = False
        return status


class C0001_Share_WorkWeb_All_With_Wrapped_All(CABST_Share_App):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Share text on Work Web (document_sharing=all) with Wrapped Native App (document_sharing=all)'
        self._dependencies.append('T031.C0000_Receiver_Apps')
        self._s_app = WorkWeb
        self._s_policy = 'xTA - default'
        self._s_workspace = False
        self._t_app = TAoneApp
        self._t_policy = 'xTA - default'


class C0002_Share_WorkWeb_All_With_WorkMail_All(CABST_Share_App):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Share text on Work Web (document_sharing=all) with Work Mail (document_sharing=all)'
        self._dependencies.append('T031.C0000_Receiver_Apps')
        self._s_app = WorkWeb
        self._s_policy = 'xTA - default'
        self._s_workspace = False
        self._t_app = WorkMail
        self._t_policy = 'xTA - default'


class C0011_Share_WorkWeb_All_With_Wrapped_WS(CABST_Share_App):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Share text on Work Web (document_sharing=all) ' + \
                     'with Wrapped Native App (document_sharing=workspace)'
        self._dependencies.append('T031.C0000_Receiver_Apps')
        self._s_app = WorkWeb
        self._s_policy = 'xTA - default'
        self._s_workspace = False
        self._t_app = TAoneApp
        self._t_policy = 'xTA - document - workspace'


class C0012_Share_WorkWeb_All_With_WorkMail_WS(CABST_Share_App):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Share text on Work Web (document_sharing=all) with Work Mail (document_sharing=workspace)'
        self._dependencies.append('T031.C0000_Receiver_Apps')
        self._s_app = WorkWeb
        self._s_policy = 'xTA - default'
        self._s_workspace = False
        self._t_app = WorkMail
        self._t_policy = 'xTA - document - workspace'


class C0021_Share_WorkWeb_All_With_Wrapped_Block(CABST_Share_App):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Share text on Work Web (document_sharing=all) ' + \
                     'with Wrapped Native App (document_sharing=block)'
        self._dependencies.append('T031.C0000_Receiver_Apps')
        self._s_app = WorkWeb
        self._s_policy = 'xTA - default'
        self._s_workspace = False
        self._t_app = TAoneApp
        self._t_policy = 'xTA - document - block'


class C0022_Share_WorkWeb_All_With_WorkMail_Block(CABST_Share_App):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Share text on Work Web (document_sharing=all) with Work Mail (document_sharing=block)'
        self._dependencies.append('T031.C0000_Receiver_Apps')
        self._s_app = WorkWeb
        self._s_policy = 'xTA - default'
        self._s_workspace = False
        self._t_app = WorkMail
        self._t_policy = 'xTA - document - block'


class C0101_Share_SWA_All_With_Wrapped_All(CABST_Share_App):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Share text on Secure Web App (document_sharing=all) ' + \
                     'with Wrapped Native App (document_sharing=all)'
        self._dependencies.append('T031.C0000_Receiver_Apps')
        self._s_app = TWText
        self._s_policy = 'xTA - default'
        self._s_workspace = False
        self._t_app = TAoneApp
        self._t_policy = 'xTA - default'


class C0102_Share_SWA_All_With_WorkMail_All(CABST_Share_App):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Share text on Secure Web App (document_sharing=all) with Work Mail (document_sharing=all)'
        self._dependencies.append('T031.C0000_Receiver_Apps')
        self._s_app = TWText
        self._s_policy = 'xTA - default'
        self._s_workspace = False
        self._t_app = WorkMail
        self._t_policy = 'xTA - default'


class C0111_Share_SWA_All_With_Wrapped_WS(CABST_Share_App):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Share text on Secure Web App (document_sharing=all) ' + \
                     'with Wrapped Native App (document_sharing=workspace)'
        self._dependencies.append('T031.C0000_Receiver_Apps')
        self._s_app = TWText
        self._s_policy = 'xTA - default'
        self._s_workspace = False
        self._t_app = TAoneApp
        self._t_policy = 'xTA - document - workspace'


class C0112_Share_SWA_All_With_WorkMail_WS(CABST_Share_App):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Share text on Secure Web App (document_sharing=all) with Work Mail (document_sharing=workspace)'
        self._dependencies.append('T031.C0000_Receiver_Apps')
        self._s_app = TWText
        self._s_policy = 'xTA - default'
        self._s_workspace = False
        self._t_app = WorkMail
        self._t_policy = 'xTA - document - workspace'


class C0121_Share_SWA_All_With_Wrapped_Block(CABST_Share_App):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Share text on Secure Web App (document_sharing=all) ' + \
                     'with Wrapped Native App (document_sharing=block)'
        self._dependencies.append('T031.C0000_Receiver_Apps')
        self._s_app = TWText
        self._s_policy = 'xTA - default'
        self._s_workspace = False
        self._t_app = TAoneApp
        self._t_policy = 'xTA - document - block'


class C0122_Share_SWA_All_With_WorkMail_Block(CABST_Share_App):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Share text on Secure Web App (document_sharing=all) with Work Mail (document_sharing=block)'
        self._dependencies.append('T031.C0000_Receiver_Apps')
        self._s_app = TWText
        self._s_policy = 'xTA - default'
        self._s_workspace = False
        self._t_app = WorkMail
        self._t_policy = 'xTA - document - block'


class C0201_Share_WrappedApp_All_With_Wrapped_All(CABST_Share_App):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Share text on Wrapped Native App (document_sharing=all) ' + \
                     'with Wrapped Native App (document_sharing=all)'
        self._dependencies.append('T031.C0000_Receiver_Apps')
        self._s_app = TAoneApp
        self._s_policy = 'xTA - default'
        self._s_workspace = False
        self._t_app = TAoneBuddy
        self._t_policy = 'xTA - default'


class C0202_Share_WrappedApp_All_With_WorkMail_All(CABST_Share_App):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Share text on Wrapped Native App (document_sharing=all) with Work Mail (document_sharing=all)'
        self._dependencies.append('T031.C0000_Receiver_Apps')
        self._s_app = TAoneApp
        self._s_policy = 'xTA - default'
        self._s_workspace = False
        self._t_app = WorkMail
        self._t_policy = 'xTA - default'


class C0211_Share_WrappedApp_All_With_Wrapped_WS(CABST_Share_App):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Share text on Wrapped Native App (document_sharing=all) ' + \
                     'with Wrapped Native App (document_sharing=workspace)'
        self._dependencies.append('T031.C0000_Receiver_Apps')
        self._s_app = TAoneApp
        self._s_policy = 'xTA - default'
        self._s_workspace = False
        self._t_app = TAoneBuddy
        self._t_policy = 'xTA - document - workspace'


class C0212_Share_WrappedApp_All_With_WorkMail_WS(CABST_Share_App):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Share text on Wrapped Native App (document_sharing=all) ' + \
                     'with Work Mail (document_sharing=workspace)'
        self._dependencies.append('T031.C0000_Receiver_Apps')
        self._s_app = TAoneApp
        self._s_policy = 'xTA - default'
        self._s_workspace = False
        self._t_app = WorkMail
        self._t_policy = 'xTA - document - workspace'


class C0221_Share_WrappedApp_All_With_Wrapped_Block(CABST_Share_App):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Share text on Wrapped Native App (document_sharing=all) ' + \
                     'with Wrapped Native App (document_sharing=block)'
        self._dependencies.append('T031.C0000_Receiver_Apps')
        self._s_app = TAoneApp
        self._s_policy = 'xTA - default'
        self._s_workspace = False
        self._t_app = TAoneBuddy
        self._t_policy = 'xTA - document - block'


class C0222_Share_WrappedApp_All_With_WorkMail_Block(CABST_Share_App):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Share text on Wrapped Native App (document_sharing=all) ' + \
                     'with Work Mail (document_sharing=block)'
        self._dependencies.append('T031.C0000_Receiver_Apps')
        self._s_app = TAoneApp
        self._s_policy = 'xTA - default'
        self._s_workspace = False
        self._t_app = WorkMail
        self._t_policy = 'xTA - document - block'


class C1001_Share_WorkWeb_WS_With_Wrapped_All(CABST_Share_App):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Share text on Work Web (document_sharing=workspace) ' + \
                     'with Wrapped Native App (document_sharing=all)'
        self._dependencies.append('T031.C0000_Receiver_Apps')
        self._s_app = WorkWeb
        self._s_policy = 'xTA - document - workspace'
        self._s_workspace = True
        self._t_app = TAoneApp
        self._t_policy = 'xTA - default'


class C1002_Share_WorkWeb_WS_With_WorkMail_All(CABST_Share_App):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Share text on Work Web (document_sharing=workspace) with Work Mail (document_sharing=all)'
        self._dependencies.append('T031.C0000_Receiver_Apps')
        self._s_app = WorkWeb
        self._s_policy = 'xTA - document - workspace'
        self._s_workspace = True
        self._t_app = WorkMail
        self._t_policy = 'xTA - default'


class C1003_Share_WorkWeb_WS_No_Encrypt_With_Wrapped_All(CABST_Share_App):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Share text on Work Web (document_sharing=workspace, encryption_required=false) ' + \
                     'with Wrapped Native App (document_sharing=all)'
        self._dependencies.append('T031.C0000_Receiver_Apps')
        self._s_app = WorkWeb
        self._s_policy = 'xTA - document - workspace - no encrypt'
        self._s_workspace = True
        self._t_app = TAoneApp
        self._t_policy = 'xTA - default'


class C1004_Share_WorkWeb_WS_No_Encrypt_With_WorkMail_All(CABST_Share_App):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Share text on Work Web (document_sharing=workspace, encryption_required=false) ' + \
                     'with Work Mail (document_sharing=all)'
        self._dependencies.append('T031.C0000_Receiver_Apps')
        self._s_app = WorkWeb
        self._s_policy = 'xTA - document - workspace - no encrypt'
        self._s_workspace = True
        self._t_app = WorkMail
        self._t_policy = 'xTA - default'


class C1011_Share_WorkWeb_WS_With_Wrapped_WS(CABST_Share_App):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Share text on Work Web (document_sharing=workspace) ' + \
                     'with Wrapped Native App (document_sharing=workspace)'
        self._dependencies.append('T031.C0000_Receiver_Apps')
        self._s_app = WorkWeb
        self._s_policy = 'xTA - document - workspace'
        self._s_workspace = True
        self._t_app = TAoneApp
        self._t_policy = 'xTA - document - workspace'


class C1012_Share_WorkWeb_WS_With_WorkMail_WS(CABST_Share_App):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Share text on Work Web (document_sharing=workspace) with Work Mail (document_sharing=workspace)'
        self._dependencies.append('T031.C0000_Receiver_Apps')
        self._s_app = WorkWeb
        self._s_policy = 'xTA - document - workspace'
        self._s_workspace = True
        self._t_app = WorkMail
        self._t_policy = 'xTA - document - workspace'


class C1021_Share_WorkWeb_WS_With_Wrapped_Block(CABST_Share_App):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Share text on Work Web (document_sharing=workspace) ' + \
                     'with Wrapped Native App (document_sharing=block)'
        self._dependencies.append('T031.C0000_Receiver_Apps')
        self._s_app = WorkWeb
        self._s_policy = 'xTA - document - workspace'
        self._s_workspace = True
        self._t_app = TAoneApp
        self._t_policy = 'xTA - document - block'


class C1022_Share_WorkWeb_WS_With_WorkMail_Block(CABST_Share_App):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Share text on Work Web (document_sharing=workspace) with Work Mail (document_sharing=block)'
        self._dependencies.append('T031.C0000_Receiver_Apps')
        self._s_app = WorkWeb
        self._s_policy = 'xTA - document - workspace'
        self._s_workspace = True
        self._t_app = WorkMail
        self._t_policy = 'xTA - document - block'


class C1101_Share_SWA_WS_With_Wrapped_All(CABST_Share_App):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Share text on Secure Web App (document_sharing=workspace) ' + \
                     'with Wrapped Native App (document_sharing=all)'
        self._dependencies.append('T031.C0000_Receiver_Apps')
        self._s_app = TWText
        self._s_policy = 'xTA - document - workspace'
        self._s_workspace = True
        self._t_app = TAoneApp
        self._t_policy = 'xTA - default'


class C1102_Share_SWA_WS_With_WorkMail_All(CABST_Share_App):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Share text on Secure Web App (document_sharing=workspace) ' + \
                     'with Work Mail (document_sharing=all)'
        self._dependencies.append('T031.C0000_Receiver_Apps')
        self._s_app = TWText
        self._s_policy = 'xTA - document - workspace'
        self._s_workspace = True
        self._t_app = WorkMail
        self._t_policy = 'xTA - default'


class C1103_Share_SWA_WS_No_Encrypt_With_Wrapped_All(CABST_Share_App):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Share text on Secure Web App (document_sharing=workspace, encryption_required=false) ' + \
                     'with Wrapped Native App (document_sharing=all)'
        self._dependencies.append('T031.C0000_Receiver_Apps')
        self._s_app = TWText
        self._s_policy = 'xTA - document - workspace - no encrypt'
        self._s_workspace = True
        self._t_app = TAoneApp
        self._t_policy = 'xTA - default'


class C1104_Share_SWA_WS_No_Encrypt_With_WorkMail_All(CABST_Share_App):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Share text on Secure Web App (document_sharing=workspace, encryption_required=false) ' + \
                     'with Work Mail (document_sharing=all)'
        self._dependencies.append('T031.C0000_Receiver_Apps')
        self._s_app = TWText
        self._s_policy = 'xTA - document - workspace - no encrypt'
        self._s_workspace = True
        self._t_app = WorkMail
        self._t_policy = 'xTA - default'


class C1111_Share_SWA_WS_With_Wrapped_WS(CABST_Share_App):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Share text on Secure Web App (document_sharing=workspace) ' + \
                     'with Wrapped Native App (document_sharing=workspace)'
        self._dependencies.append('T031.C0000_Receiver_Apps')
        self._s_app = TWText
        self._s_policy = 'xTA - document - workspace'
        self._s_workspace = True
        self._t_app = TAoneApp
        self._t_policy = 'xTA - document - workspace'


class C1112_Share_SWA_WS_With_WorkMail_WS(CABST_Share_App):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Share text on Secure Web App (document_sharing=workspace) ' + \
                     'with Work Mail (document_sharing=workspace)'
        self._dependencies.append('T031.C0000_Receiver_Apps')
        self._s_app = TWText
        self._s_policy = 'xTA - document - workspace'
        self._s_workspace = True
        self._t_app = WorkMail
        self._t_policy = 'xTA - document - workspace'


class C1121_Share_SWA_WS_With_Wrapped_Block(CABST_Share_App):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Share text on Secure Web App (document_sharing=workspace) ' + \
                     'with Wrapped Native App (document_sharing=block)'
        self._dependencies.append('T031.C0000_Receiver_Apps')
        self._s_app = TWText
        self._s_policy = 'xTA - document - workspace'
        self._s_workspace = True
        self._t_app = TAoneApp
        self._t_policy = 'xTA - document - block'


class C1122_Share_SWA_WS_With_WorkMail_Block(CABST_Share_App):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Share text on Secure Web App (document_sharing=workspace) with Work Mail (document_sharing=block)'
        self._dependencies.append('T031.C0000_Receiver_Apps')
        self._s_app = TWText
        self._s_policy = 'xTA - document - workspace'
        self._s_workspace = True
        self._t_app = WorkMail
        self._t_policy = 'xTA - document - block'


class C1201_Share_WrappedApp_WS_With_Wrapped_All(CABST_Share_App):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Share text on Wrapped Native App (document_sharing=workspace) ' + \
                     'with Wrapped Native App (document_sharing=all)'
        self._dependencies.append('T031.C0000_Receiver_Apps')
        self._s_app = TAoneApp
        self._s_policy = 'xTA - document - workspace'
        self._s_workspace = True
        self._t_app = TAoneBuddy
        self._t_policy = 'xTA - default'


class C1202_Share_WrappedApp_WS_With_WorkMail_All(CABST_Share_App):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Share text on Wrapped Native App (document_sharing=workspace) ' + \
                     'with Work Mail (document_sharing=all)'
        self._dependencies.append('T031.C0000_Receiver_Apps')
        self._s_app = TAoneApp
        self._s_policy = 'xTA - document - workspace'
        self._s_workspace = True
        self._t_app = WorkMail
        self._t_policy = 'xTA - default'


class C1203_Share_WrappedApp_WS_No_Encrypt_With_Wrapped_All(CABST_Share_App):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Share text on Wrapped Native App (document_sharing=workspace, encryption_required=false) ' + \
                     'with Wrapped Native App (document_sharing=all)'
        self._dependencies.append('T031.C0000_Receiver_Apps')
        self._s_app = TAoneApp
        self._s_policy = 'xTA - document - workspace - no encrypt'
        self._s_workspace = True
        self._t_app = TAoneBuddy
        self._t_policy = 'xTA - default'


class C1204_Share_WrappedApp_WS_No_Encrypt_With_WorkMail_All(CABST_Share_App):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Share text on Wrapped Native App (document_sharing=workspace, encryption_required=false) ' + \
                     'with Work Mail (document_sharing=all)'
        self._dependencies.append('T031.C0000_Receiver_Apps')
        self._s_app = TAoneApp
        self._s_policy = 'xTA - document - workspace - no encrypt'
        self._s_workspace = True
        self._t_app = WorkMail
        self._t_policy = 'xTA - default'


class C1211_Share_WrappedApp_WS_With_Wrapped_WS(CABST_Share_App):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Share text on Wrapped Native App (document_sharing=workspace) ' + \
                     'with Wrapped Native App (document_sharing=workspace)'
        self._dependencies.append('T031.C0000_Receiver_Apps')
        self._s_app = TAoneApp
        self._s_policy = 'xTA - document - workspace'
        self._s_workspace = True
        self._t_app = TAoneBuddy
        self._t_policy = 'xTA - document - workspace'


class C1212_Share_WrappedApp_WS_With_WorkMail_WS(CABST_Share_App):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Share text on Wrapped Native App (document_sharing=workspace) ' + \
                     'with Work Mail (document_sharing=workspace)'
        self._dependencies.append('T031.C0000_Receiver_Apps')
        self._s_app = TAoneApp
        self._s_policy = 'xTA - document - workspace'
        self._s_workspace = True
        self._t_app = WorkMail
        self._t_policy = 'xTA - document - workspace'


class C1221_Share_WrappedApp_WS_With_Wrapped_Block(CABST_Share_App):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Share text on Wrapped Native App (document_sharing=workspace) ' + \
                     'with Wrapped Native App (document_sharing=block)'
        self._dependencies.append('T031.C0000_Receiver_Apps')
        self._s_app = TAoneApp
        self._s_policy = 'xTA - document - workspace'
        self._s_workspace = True
        self._t_app = TAoneBuddy
        self._t_policy = 'xTA - document - block'


class C1222_Share_WrappedApp_WS_With_WorkMail_Block(CABST_Share_App):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Share text on Wrapped Native App (document_sharing=workspace) ' + \
                     'with Work Mail (document_sharing=block)'
        self._dependencies.append('T031.C0000_Receiver_Apps')
        self._s_app = TAoneApp
        self._s_policy = 'xTA - document - workspace'
        self._s_workspace = True
        self._t_app = WorkMail
        self._t_policy = 'xTA - document - block'


class C2000_Share_WorkWeb_Block(TestBase):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Cannot share text on Work Web (document_sharing=block)'

    def run(self):
        try:
            self.start()
            test_block_share_document(WorkWeb())
            self.complete()
        except Exception as e:
            self.abend(e, take_log=True, take_screenshot=True)
            self.post_error()
        WorkWeb().stop()


class C2100_Share_SWA_Block(TestBase):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Cannot share text on Secure Web App (document_sharing=block)'

    def run(self):
        try:
            self.start()
            test_block_share_document(TWText())
            self.complete()
        except Exception as e:
            self.abend(e, take_log=True, take_screenshot=True)
            self.post_error()
        TWText().stop()


class C2200_Share_WrappedApp_Block(TestBase):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Cannot share text on Wrapped Native App (document_sharing=block)'

    def run(self):
        try:
            self.start()
            test_block_share_document(TAoneApp())
            self.complete()
        except Exception as e:
            self.abend(e, take_log=True, take_screenshot=True)
            self.post_error()
        TAoneApp().stop()


class C5001_Share_WorkWeb_All_Encrypt_With_Unwrapped(CABST_Share_App):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Share text on Work Web (document_sharing=all, encryption required) with Unwrapped App'
        self._dependencies.append('T031.C0000_Receiver_Apps')
        self._s_app = WorkWeb
        self._s_policy = 'xTA - default'
        self._s_workspace = False
        self._t_app = TAoneUtil
        self._t_policy = ''


class C5002_Share_SWA_All_Encrypt_With_Unwrapped(CABST_Share_App):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Share text on Secure Web App (document_sharing=all, encryption required) ' + \
                     'with Unwrapped App'
        self._dependencies.append('T031.C0000_Receiver_Apps')
        self._s_app = TWText
        self._s_policy = 'xTA - default'
        self._s_workspace = False
        self._t_app = TAoneUtil
        self._t_policy = ''


class C5003_Share_WrappedApp_All_Encrypt_With_Unwrapped(CABST_Share_App):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Share text on Wrapped Native App (document_sharing=all, encryption required) ' + \
                     'with Unwrapped App'
        self._dependencies.append('T031.C0000_Receiver_Apps')
        self._s_app = TAoneApp
        self._s_policy = 'xTA - default'
        self._s_workspace = False
        self._t_app = TAoneUtil
        self._t_policy = ''
