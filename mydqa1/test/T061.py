# -*- coding: utf-8 -*-
from helper import logger
from testbase import TestBase
from apps.android.workweb import WorkWeb, WorkWebNavigationException
from apps.android.swa import TWText, TWTextByIPAddr, TWBasicAuth, TWDigestAuth
from apps.android.swa import SymantecSWA, GoogleSWA, LinkedinSWA, YahooSWA
from apps.website import sites as website


class CABST_Default_WorkWeb(TestBase):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Verify Web site access status on Work Web with default NAC policy'
        self._site = None
        self._templates = []

    def run(self):
        try:
            self.start()
            ww = WorkWeb().prep('xTA - default').startup()
            try:
                ww.navigate(website[self._site])
            except WorkWebNavigationException:
                ww.startup().navigate(website[self._site])
            if ww.is_error_page() or not ww.is_page_up(*self._templates):
                raise Exception('Failed to access Web site: %s' % website[self._site])
            self.complete()
        except Exception as e:
            self.abend(e, take_log=True, take_screenshot=True)
            self.post_error()
        WorkWeb().stop()


class CABST_Default_WorkWeb_Auth(TestBase):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Verify Web site access status on Work Web with default NAC policy'
        self._url = None

    def run(self):
        try:
            self.start()
            ww = WorkWeb().prep('xTA - default').startup()
            try:
                ww.navigate(self._url)
            except WorkWebNavigationException:
                ww.startup().navigate(self._url)
            if not ww.is_web_auth_prompted() and not ww.refresh().is_web_auth_prompted():
                raise Exception('Failed to access Web site: %s' % self._url)
            self.complete()
        except Exception as e:
            self.abend(e, take_log=True, take_screenshot=True)
            self.post_error()
        WorkWeb().stop()


class CABST_Default_SWA(TestBase):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Verify Web site access status on Secure Web App with default NAC policy'
        self._app = None
        self._templates = []

    def run(self):
        try:
            self.start()
            if not self._app().prep('xTA - default').startup().refresh().is_page_up(*self._templates):
                raise Exception('Failed to access Web site on SWA: %s' % self._app)
            self.complete()
        except Exception as e:
            self.abend(e, take_log=True, take_screenshot=True)
            self.post_error()
        self._app().stop()


class CABST_Default_SWA_Auth(TestBase):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Verify Web site access status on Secure Web App with default NAC policy'
        self._app = None
        self._templates = []

    def run(self):
        try:
            self.start()
            if self._app().prep('xTA - default').startup().refresh().is_page_up(*self._templates):
                raise Exception('Failed to access Web site on SWA: %s' % self._app)
            self.complete()
        except Exception as e:
            self.abend(e, take_log=True, take_screenshot=True)
            self.post_error()
        self._app().stop()


class CABST_Allow_WorkWeb(TestBase):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Allow access to ??? on Work Web with ??? NAC policy'
        self._policy = None
        self._url = None
        self._templates = []

    def run(self):
        try:
            self.start()
            ww = WorkWeb().prep(self._policy).startup().navigate(self._url).refresh()
            if ww.is_error_page() or not ww.is_page_up(*self._templates):
                raise Exception('Failed to access "%s" with policy "%s" on Work Web' % (self._url, self._policy))
            self.complete()
        except Exception as e:
            self.abend(e, take_log=True, take_screenshot=True)
            self.post_error()
        WorkWeb().stop()


class CABST_Block_WorkWeb(TestBase):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Block access to ??? on Work Web with ??? NAC policy'
        self._policy = None
        self._url = None
        self._templates = []

    def run(self):
        try:
            self.start()
            ww = WorkWeb().prep(self._policy).startup().navigate(self._url)
            if not ww.is_error_page() or ww.is_page_up(*self._templates):
                ww.refresh()
                if not ww.is_error_page() or ww.is_page_up(*self._templates):
                    raise Exception('Failed to block "%s" with policy "%s" on Work Web' % (self._url, self._policy))
            self.complete()
        except Exception as e:
            self.abend(e, take_log=True, take_screenshot=True)
            self.post_error()
        WorkWeb().stop()


class CABST_Allow_SWA(TestBase):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Allow access to ??? on Secure Web App with ??? NAC policy'
        self._app = None
        self._policy = None
        self._templates = []

    def run(self):
        try:
            self.start()
            wa = self._app().prep(self._policy).startup()
            try:
                wa.refresh()
            except Exception:
                wa.prep(policy=self._policy, reinstall=True).startup()
            if not wa.is_page_up(*self._templates):
                raise Exception('Failed to access "%s" with policy "%s" on Secure Web App' % (wa.appname(), self._policy))
            self.complete()
        except Exception as e:
            self.abend(e, take_log=True, take_screenshot=True)
            self.post_error()
        self._app().stop()


class CABST_Block_SWA(TestBase):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Block access to ??? on Secure Web App with ??? NAC policy'
        self._app = None
        self._policy = None
        self._templates = []

    def run(self):
        try:
            self.start()
            wa = self._app().prep(self._policy).startup()
            try:
                wa.refresh()
            except Exception:
                wa.prep(policy=self._policy, reinstall=True).startup()
            if wa.is_page_up(*self._templates):
                raise Exception('Failed to block "%s" with policy "%s" on Secure Web App' % (wa.appname(), self._policy))
            self.complete()
        except Exception as e:
            self.abend(e, take_log=True, take_screenshot=True)
            self.post_error()
        self._app().stop()


class C0000_Default_Access(TestBase):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Verify Web sites access status with default NAC policy'

    def run(self):
        try:
            self.start()
            ww = WorkWeb().prep('xTA - default').startup()
            ww.navigate(website['symantec'])
            if not ww.is_error_page() and ww.is_page_up('symantec_logo'):
                self.set_named_result('ww.symantec', True)
                logger.info('Work Web: %s = OK' % website['symantec'])
            ww.navigate(website['yahoo'])
            if not ww.is_error_page() and ww.is_page_up('yahoo_main', 'yahoo_main2', 'yahoo_main3'):
                self.set_named_result('ww.yahoo', True)
                logger.info('Work Web: %s = OK' % website['yahoo'])
            ww.navigate(website['google'])
            if not ww.is_error_page() and ww.is_page_up('google_main', 'google_main2'):
                self.set_named_result('ww.google', True)
                logger.info('Work Web: %s = OK' % website['google'])
            ww.navigate(website['linkedin'])
            if not ww.is_error_page() and ww.is_page_up('linkedin_logo_1', 'linkedin_logo_2'):
                self.set_named_result('ww.linkedin', True)
                logger.info('Work Web: %s = OK' % website['linkedin'])
            ww.navigate('http://testweb1.ac.symantec.com/basic')
            if ww.is_web_auth_prompted() or ww.refresh().is_web_auth_prompted():
                self.set_named_result('ww.basic_auth', True)
                logger.info('Work Web: Basic auth = OK')
            ww.navigate('http://testweb1.ac.symantec.com/digest')
            if ww.is_web_auth_prompted() or ww.refresh().is_web_auth_prompted():
                self.set_named_result('ww.digest_auth', True)
                logger.info('Work Web: Digest auth = OK')

            if SymantecSWA().prep('xTA - default').startup().refresh().is_page_up('symantec_logo'):
                self.set_named_result('swa.symantec', True)
                logger.info('SWA: %s = OK' % website['symantec'])
            if YahooSWA().prep('xTA - default').startup().refresh().is_page_up('yahoo_main', 'yahoo_main2', 'yahoo_main3'):
                self.set_named_result('swa.yahoo', True)
                logger.info('SWA: %s = OK' % website['yahoo'])
            if GoogleSWA().prep('xTA - default').startup().refresh().is_page_up('google_main', 'google_main2'):
                self.set_named_result('swa.google', True)
                logger.info('SWA: %s = OK' % website['google'])
            if LinkedinSWA().prep('xTA - default').startup().refresh().is_page_up('linkedin_logo_1', 'linkedin_logo_2'):
                self.set_named_result('swa.linkedin', True)
                logger.info('SWA: %s = OK' % website['linkedin'])
            if not TWBasicAuth().prep('xTA - default').startup().refresh().is_page_up('symc_logo'):
                self.set_named_result('swa.basic_auth', True)
                logger.info('SWA: Basic auth = OK')
            if not TWDigestAuth().prep('xTA - default').startup().refresh().is_page_up('symc_logo'):
                self.set_named_result('swa.digest_auth', True)
                logger.info('SWA: Digest auth = OK')
            self.complete()
        except Exception as e:
            self.abend(e, take_log=True, take_screenshot=True)
            self.post_error()
        WorkWeb().stop()
        SymantecSWA().stop()
        GoogleSWA().stop()
        LinkedinSWA().stop()
        YahooSWA().stop()
        TWBasicAuth().stop()
        TWDigestAuth().stop()


class C0000s01_Default_WorkWeb_Symantec(CABST_Default_WorkWeb):
    def __init__(self):
        CABST_Default_WorkWeb.__init__(self)
        self._desc = 'Verify Web site access status on Work Web with default NAC policy'
        self._site = 'symantec'
        self._templates = ['symantec_logo']


class C0000s02_Default_WorkWeb_Yahoo(CABST_Default_WorkWeb):
    def __init__(self):
        CABST_Default_WorkWeb.__init__(self)
        self._desc = 'Verify Yahoo Web site access status on Work Web with default NAC policy'
        self._site = 'yahoo'
        self._templates = ['yahoo_main', 'yahoo_main2', 'yahoo_main3']


class C0000s03_Default_WorkWeb_Google(CABST_Default_WorkWeb):
    def __init__(self):
        CABST_Default_WorkWeb.__init__(self)
        self._desc = 'Verify Google Web site access status on Work Web with default NAC policy'
        self._site = 'google'
        self._templates = ['google_main', 'google_main2']


class C0000s04_Default_WorkWeb_LinkedIn(CABST_Default_WorkWeb):
    def __init__(self):
        CABST_Default_WorkWeb.__init__(self)
        self._desc = 'Verify LinkedIn Web site access status on Work Web with default NAC policy'
        self._site = 'linkedin'
        self._templates = ['linkedin_logo_1', 'linkedin_logo_2']


class C0000s05_Default_WorkWeb_Basic_Auth(CABST_Default_WorkWeb_Auth):
    def __init__(self):
        CABST_Default_WorkWeb_Auth.__init__(self)
        self._desc = 'Verify Basic Auth Web site access status on Work Web with default NAC policy'
        self._url = 'http://testweb1.ac.symantec.com/basic'


class C0000s06_Default_WorkWeb_Digest_Auth(CABST_Default_WorkWeb_Auth):
    def __init__(self):
        CABST_Default_WorkWeb_Auth.__init__(self)
        self._desc = 'Verify Digest Auth Web site access status on Work Web with default NAC policy'
        self._url = 'http://testweb1.ac.symantec.com/digest'


class C0000s11_Default_SWA_Symantec(CABST_Default_SWA):
    def __init__(self):
        CABST_Default_SWA.__init__(self)
        self._desc = 'Verify Symantec Web site access status on Secure Web App with default NAC policy'
        self._app = SymantecSWA
        self._templates = ['symantec_logo']


class C0000s12_Default_SWA_Yahoo(CABST_Default_SWA):
    def __init__(self):
        CABST_Default_SWA.__init__(self)
        self._desc = 'Verify Yahoo Web site access status on Secure Web App with default NAC policy'
        self._app = YahooSWA
        self._templates = ['yahoo_main', 'yahoo_main2', 'yahoo_main3']


class C0000s13_Default_SWA_Google(CABST_Default_SWA):
    def __init__(self):
        CABST_Default_SWA.__init__(self)
        self._desc = 'Verify Google Web site access status on Secure Web App with default NAC policy'
        self._app = GoogleSWA
        self._templates = ['google_main', 'google_main2']


class C0000s14_Default_SWA_LinkedIn(CABST_Default_SWA):
    def __init__(self):
        CABST_Default_SWA.__init__(self)
        self._desc = 'Verify LinkedIn Web site access status on Secure Web App with default NAC policy'
        self._app = LinkedinSWA
        self._templates = ['linkedin_logo_1', 'linkedin_logo_2']


class C0000s15_Default_SWA_Basic_Auth(CABST_Default_SWA_Auth):
    def __init__(self):
        CABST_Default_SWA_Auth.__init__(self)
        self._desc = 'Verify Basic Auth Web site access status on Secure Web App with default NAC policy'
        self._app = TWBasicAuth
        self._templates = ['symc_logo']


class C0000s16_Default_SWA_Digest_Auth(CABST_Default_SWA_Auth):
    def __init__(self):
        CABST_Default_SWA_Auth.__init__(self)
        self._desc = 'Verify Digest Auth Web site access status on Secure Web App with default NAC policy'
        self._app = TWDigestAuth
        self._templates = ['symc_logo']


class C0001_Block_WorkWeb_By_Whitelist(CABST_Block_WorkWeb):
    def __init__(self):
        CABST_Block_WorkWeb.__init__(self)
        self._desc = 'Block access to Symantec Web site on Work Web with Google whitelist NAC policy'
        self._dependencies.append('T061.C0000s01_Default_WorkWeb_Symantec')
        self._policy = 'xTA - nac - whitelist'
        self._url = website['symantec']
        self._templates = ['symantec_logo']


class C0002_Allow_WorkWeb_By_Whitelist(CABST_Allow_WorkWeb):
    def __init__(self):
        CABST_Allow_WorkWeb.__init__(self)
        self._desc = 'Allow access to Google Web site on Work Web with Google whitelist NAC policy'
        self._dependencies.append('T061.C0000s03_Default_WorkWeb_Google')
        self._policy = 'xTA - nac - whitelist'
        self._url = website['google']
        self._templates = ['google_main', 'google_main2']


class C0011_Block_SWA_By_Whitelist(CABST_Block_SWA):
    def __init__(self):
        CABST_Block_SWA.__init__(self)
        self._desc = 'Block access to Yahoo Web site on Secure Web App with Google whitelist NAC policy'
        self._dependencies.append('T061.C0000s12_Default_SWA_Yahoo')
        self._app = YahooSWA
        self._policy = 'xTA - nac - whitelist'
        self._templates = ['yahoo_main', 'yahoo_main2', 'yahoo_main3']


class C0012_Allow_SWA_By_Whitelist(CABST_Allow_SWA):
    def __init__(self):
        CABST_Allow_SWA.__init__(self)
        self._desc = 'Allow access to Google Web site on Secure Web App with Google whitelist NAC policy'
        self._dependencies.append('T061.C0000s13_Default_SWA_Google')
        self._app = GoogleSWA
        self._policy = 'xTA - nac - whitelist'
        self._templates = ['google_main', 'google_main2']


class C0101_Block_WorkWeb_By_IP_Wildcard(CABST_Block_WorkWeb):
    def __init__(self):
        CABST_Block_WorkWeb.__init__(self)
        self._desc = 'Block access to Test Web site by URL on Work Web, with IP wildcard NAC policy'
        self._policy = 'xTA - nac - whitelist - ip wildcard'
        self._url = website['text']
        self._templates = ['symc_logo']


class C0102_Allow_WorkWeb_By_IP_Wildcard(CABST_Allow_WorkWeb):
    def __init__(self):
        CABST_Allow_WorkWeb.__init__(self)
        self._desc = 'Allow access to Test Web site by IP address on Work Web, with IP wildcard NAC policy'
        self._policy = 'xTA - nac - whitelist - ip wildcard'
        self._url = website['ipaddr']
        self._templates = ['symc_logo']


class C0111_Block_SWA_By_IP_Wildcard(CABST_Block_SWA):
    def __init__(self):
        CABST_Block_SWA.__init__(self)
        self._desc = 'Block access to Test Web site by URL on Secure Web App, with IP wildcard NAC policy'
        self._app = TWText
        self._policy = 'xTA - nac - whitelist - ip wildcard'
        self._templates = ['symc_logo']


class C0112_Allow_SWA_By_IP_Wildcard(CABST_Allow_SWA):
    def __init__(self):
        CABST_Allow_SWA.__init__(self)
        self._desc = 'Allow access to Test Web site by IP address on Secure Web App, with IP wildcard NAC policy'
        self._app = TWTextByIPAddr
        self._policy = 'xTA - nac - whitelist - ip wildcard'
        self._templates = ['symc_logo']


class C0201_Block_WorkWeb_By_URL_With_Port(CABST_Block_WorkWeb):
    def __init__(self):
        CABST_Block_WorkWeb.__init__(self)
        self._desc = 'Block access to Yahoo Web site on Work Web with URL + port NAC policy'
        self._dependencies.append('T061.C0000s02_Default_WorkWeb_Yahoo')
        self._policy = 'xTA - nac - whitelist with port'
        self._url = website['yahoo']
        self._templates = ['yahoo_main', 'yahoo_main2', 'yahoo_main3']


class C0202_Allow_WorkWeb_By_URL_With_Port(CABST_Allow_WorkWeb):
    def __init__(self):
        CABST_Allow_WorkWeb.__init__(self)
        self._desc = 'Allow access to Google Web site on Work Web with URL + port NAC policy'
        self._dependencies.append('T061.C0000s03_Default_WorkWeb_Google')
        self._policy = 'xTA - nac - whitelist with port'
        self._url = website['google']
        self._templates = ['google_main', 'google_main2']


class C0211_Block_SWA_By_URL_With_Port(CABST_Block_SWA):
    def __init__(self):
        CABST_Block_SWA.__init__(self)
        self._desc = 'Block access to Yahoo Web site on Secure Web App with URL + port NAC policy'
        self._dependencies.append('T061.C0000s12_Default_SWA_Yahoo')
        self._app = YahooSWA
        self._policy = 'xTA - nac - whitelist with port'
        self._templates = ['yahoo_main', 'yahoo_main2', 'yahoo_main3']


class C0212_Allow_SWA_By_URL_With_Port(CABST_Allow_SWA):
    def __init__(self):
        CABST_Allow_SWA.__init__(self)
        self._desc = 'Allow access to Google Web site on Secure Web App with URL + port NAC policy'
        self._dependencies.append('T061.C0000s13_Default_SWA_Google')
        self._app = GoogleSWA
        self._policy = 'xTA - nac - whitelist with port'
        self._templates = ['google_main', 'google_main2']


class C0301_Block_WorkWeb_By_Port(CABST_Block_WorkWeb):
    def __init__(self):
        CABST_Block_WorkWeb.__init__(self)
        self._desc = 'Block access to Linkedin Web site on Work Web with port 80 NAC policy'
        self._dependencies.append('T061.C0000s04_Default_WorkWeb_LinkedIn')
        self._policy = 'xTA - nac - whitelist - port 80'
        self._url = website['linkedin']
        self._templates = ['linkedin_logo_1', 'linkedin_logo_2']


class C0302_Allow_WorkWeb_By_Port_Range(CABST_Allow_WorkWeb):
    def __init__(self):
        CABST_Allow_WorkWeb.__init__(self)
        self._desc = 'Allow access to Linkedin Web site on Work Web with port 1-1024 NAC policy'
        self._dependencies.append('T061.C0000s04_Default_WorkWeb_LinkedIn')
        self._policy = 'xTA - nac - whitelist - port range'
        self._url = website['linkedin']
        self._templates = ['linkedin_logo_1', 'linkedin_logo_2']


class C0303_Block_WorkWeb_By_Wrong_Port(CABST_Block_WorkWeb):
    def __init__(self):
        CABST_Block_WorkWeb.__init__(self)
        self._desc = 'Block access to Yahoo Web site on Work Web with wrong port NAC policy'
        self._dependencies.append('T061.C0000s02_Default_WorkWeb_Yahoo')
        self._policy = 'xTA - nac - whitelist - port wrong'
        self._url = website['yahoo']
        self._templates = ['yahoo_main', 'yahoo_main2', 'yahoo_main3']


class C0311_Block_SWA_By_Port(CABST_Block_SWA):
    def __init__(self):
        CABST_Block_SWA.__init__(self)
        self._desc = 'Block access to Linkedin Web site on Secure Web App with port 80 NAC policy'
        self._dependencies.append('T061.C0000s14_Default_SWA_LinkedIn')
        self._app = LinkedinSWA
        self._policy = 'xTA - nac - whitelist - port 80'
        self._templates = ['linkedin_logo_1', 'linkedin_logo_2']


class C0312_Allow_SWA_By_Port_Range(CABST_Allow_SWA):
    def __init__(self):
        CABST_Allow_SWA.__init__(self)
        self._desc = 'Allow access to Linkedin Web site on Secure Web App with port 1-1024 NAC policy'
        self._dependencies.append('T061.C0000s14_Default_SWA_LinkedIn')
        self._app = LinkedinSWA
        self._policy = 'xTA - nac - whitelist - port range'
        self._templates = ['linkedin_logo_1', 'linkedin_logo_2']


class C0313_Block_SWA_By_Wrong_Port(CABST_Block_SWA):
    def __init__(self):
        CABST_Block_SWA.__init__(self)
        self._desc = 'Block access to Yahoo Web site on Secure Web App with wrong port NAC policy'
        self._dependencies.append('T061.C0000s12_Default_SWA_Yahoo')
        self._app = YahooSWA
        self._policy = 'xTA - nac - whitelist - port wrong'
        self._templates = ['yahoo_main', 'yahoo_main2', 'yahoo_main3']


class C0401_Block_WorkWeb_By_Require_SSL(CABST_Block_WorkWeb):
    def __init__(self):
        CABST_Block_WorkWeb.__init__(self)
        self._desc = 'Block access to Yahoo Web site on Work Web with Require SSL NAC policy'
        self._dependencies.append('T061.C0000s02_Default_WorkWeb_Yahoo')
        self._policy = 'xTA - nac - ssl required'
        self._url = website['yahoo']
        self._templates = ['yahoo_main', 'yahoo_main2', 'yahoo_main3']


class C0402_Allow_WorkWeb_By_Require_SSL(CABST_Allow_WorkWeb):
    def __init__(self):
        CABST_Allow_WorkWeb.__init__(self)
        self._desc = 'Allow access to Google Web site on Work Web with Require SSL NAC policy'
        self._dependencies.append('T061.C0000s03_Default_WorkWeb_Google')
        self._policy = 'xTA - nac - ssl required'
        self._url = website['google']
        self._templates = ['google_main', 'google_main2']


class C0411_Block_SWA_By_Require_SSL(CABST_Block_SWA):
    def __init__(self):
        CABST_Block_SWA.__init__(self)
        self._desc = 'Block access to Yahoo Web site on Secure Web App with Require SSL NAC policy'
        self._dependencies.append('T061.C0000s12_Default_SWA_Yahoo')
        self._app = YahooSWA
        self._policy = 'xTA - nac - ssl required'
        self._templates = ['yahoo_main', 'yahoo_main2', 'yahoo_main3']


class C0412_Allow_SWA_By_Require_SSL(CABST_Allow_SWA):
    def __init__(self):
        CABST_Allow_SWA.__init__(self)
        self._desc = 'Allow access to Google Web site on Secure Web App with Require SSL NAC policy'
        self._dependencies.append('T061.C0000s13_Default_SWA_Google')
        self._app = GoogleSWA
        self._policy = 'xTA - nac - ssl required'
        self._templates = ['google_main', 'google_main2']


class C0501_Certificate_Injection_WorkWeb(TestBase):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Certificate injection (basic/digest) on Work Web'
        self._dependencies.append('T061.C0000s05_Default_WorkWeb_Basic_Auth')
        self._dependencies.append('T061.C0000s06_Default_WorkWeb_Digest_Auth')

    def run(self):
        try:
            self.start()
            ww = WorkWeb()
            ww.prep('xTA - nac - credential injection').startup(param=dict(to_bookmarks=True))
            if ww.navigate('http://testweb1.ac.symantec.com/basic').is_web_auth_prompted():
                if ww.refresh().is_web_auth_prompted():
                    raise Exception('Certificate injection does not work for basic auth')
            if ww.navigate('http://testweb1.ac.symantec.com/digest').is_web_auth_prompted():
                if ww.refresh().is_web_auth_prompted():
                    raise Exception('Certificate injection does not work for digest auth')
            self.complete()
        except Exception as e:
            self.abend(e, take_log=True, take_screenshot=True)
            self.post_error()
        WorkWeb().stop()


class C0511_Certificate_Injection_SWA(TestBase):
    def __init__(self):
        TestBase.__init__(self)
        self._desc = 'Certificate injection (basic/digest) on Secure Web App'
        self._dependencies.append('T061.C0000s15_Default_SWA_Basic_Auth')
        self._dependencies.append('T061.C0000s16_Default_SWA_Digest_Auth')

    def run(self):
        try:
            self.start()
            wa = TWBasicAuth()
            if not wa.prep('xTA - nac - credential injection').startup().refresh().is_page_up('symc_logo'):
                raise Exception('Certificate injection does not work for basic auth')
            wa.stop()

            wa = TWDigestAuth()
            if not wa.prep('xTA - nac - credential injection').startup().refresh().is_page_up('symc_logo'):
                raise Exception('Certificate injection does not work for digest auth')
            wa.stop()
            self.complete()
        except Exception as e:
            self.abend(e, take_log=True, take_screenshot=True)
            self.post_error()
        TWBasicAuth().stop()
        TWDigestAuth().stop()
