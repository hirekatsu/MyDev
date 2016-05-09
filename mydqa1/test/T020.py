# -*- coding: utf-8 -*-
from datetime import datetime

from apps.android.taoneapp import TAoneApp
from helper import logger
from helper.android import android_device
from testbase import TestBase


def generate_filetext():
    return 'FILETEXT%s' % datetime.today().strftime('%H%M%S')


def generate_filename():
    return 'FILE%s' % datetime.today().strftime('%H%M%S')


class CABST_Storage_With_Allowed_No_Encryption(TestBase):
    def __init__(self, policy, mode, file_prefix, file_directory, clear_on_close):
        TestBase.__init__(self)
        self._desc = 'Write/read file on ??? storage (??? storage allowed, no encryption)'
        self._policy = policy
        self._mode = mode
        self._file_prefix = file_prefix
        self._file_directory = file_directory
        self._clear_on_close = clear_on_close

    def run(self):
        try:
            self.start()
            filename = generate_filename()
            filetext = generate_filetext()
            logger.debug('filename=%s, filetext=%s' % (filename, filetext))
            logger.debug('preparing and launching app...')
            ta = TAoneApp()
            runas = ta.packbund() if self._mode == 'appdata' else None
            ta.prep(policy=self._policy, reinstall='on_policy_changed')
            ta.startup(param=dict(extras=dict(do='storage')))
            #
            if self._mode == 'xstorage':
                logger.debug('getting external dirs...')
                app_external_dirs = ta.get_external_dir()
                adb_external_dir = android_device.get_external_storage()
                app_sub_dir = app_external_dirs['filesDir'][len(app_external_dirs['storageDir']):]
                self._file_directory = adb_external_dir + app_sub_dir
                # self._file_directory = ta.get_external_dir()['filesDir']
                logger.debug('external files dir=%s' % self._file_directory)
            #
            physical_path = '%s/%s' % (self._file_directory, filename)
            android_device.file_delete(path=physical_path, runas=runas)
            logger.debug('writing file to app data storage...')
            ta.write_storage(mode=self._mode, path=self._file_prefix + filename, content=filetext, block=False)
            logger.debug('verifying file exists...')
            if not android_device.file_exist(path=physical_path, runas=runas):
                raise Exception('Written file does not exist: %s' % physical_path)
            content = android_device.file_cat(path=physical_path, runas=runas)
            if content != filetext:
                raise Exception('Written file content does not match: expected=%s, actual=%s' % (filetext, content))
            logger.debug('reading file on app data storage...')
            # should be successful
            ta.read_storage(verify=filetext, block=False)

            # re-launch app and verify file still remains
            ta.stop()
            ta.startup(param=dict(extras=dict(do='storage')))
            if not self._clear_on_close:
                if not android_device.file_exist(path=physical_path, runas=runas):
                    raise Exception('Written file does not exist after restarting app: %s' % physical_path)
                logger.debug('deleting file on app data storage...')
                ta.delete_storage(mode=self._mode, path=self._file_prefix + filename, block=False)
                logger.debug('verifying file deleted...')
                if android_device.file_exist(path=physical_path, runas=runas):
                    raise Exception('Written file has not been deleted: %s' % physical_path)
            else:
                if android_device.file_exist(path=physical_path, runas=runas):
                    raise Exception('Written file still exists after restarting app: %s' % physical_path)
            self.complete()
        except Exception as e:
            self.abend(e, take_log=True, take_screenshot=True)
            self.post_error()
        TAoneApp().stop()


class CABST_Storage_With_Blocked_No_Encryption(TestBase):
    def __init__(self, policy, mode, file_prefix, file_directory):
        TestBase.__init__(self)
        self._desc = 'Block from writing file on ??? storage (??? storage not allowed, no encryption)'
        self._policy = policy
        self._mode = mode
        self._file_prefix = file_prefix
        self._file_directory = file_directory

    def run(self):
        try:
            self.start()
            filename = generate_filename()
            filetext = generate_filetext()
            logger.debug('filename=%s, filetext=%s' % (filename, filetext))
            logger.debug('preparing and launching app...')
            ta = TAoneApp()
            runas = ta.packbund() if self._mode == 'appdata' else None
            ta.prep(policy=self._policy, reinstall='on_policy_changed')
            ta.startup(param=dict(extras=dict(do='storage')))
            #
            if self._mode == 'xstorage':
                logger.debug('getting external dirs...')
                app_external_dirs = ta.get_external_dir()
                adb_external_dir = android_device.get_external_storage()
                app_sub_dir = app_external_dirs['filesDir'][len(app_external_dirs['storageDir']):]
                self._file_directory = adb_external_dir + app_sub_dir
                # self._file_directory = ta.get_external_dir()['filesDir']
                logger.debug('external files dir=%s' % self._file_directory)
            #
            physical_path = '%s/%s' % (self._file_directory, filename)
            android_device.file_delete(path=physical_path, runas=runas)
            logger.debug('writing file to app data storage...')
            ta.write_storage(mode=self._mode, path=self._file_prefix + filename, content=filetext, block=True)
            logger.debug('verifying file exists...')
            if android_device.file_exist(path=physical_path, runas=runas):
                raise Exception('Written exist, not blocked: %s' % physical_path)
            self.complete()
        except Exception as e:
            self.abend(e, take_log=True, take_screenshot=True)
            self.post_error()
        TAoneApp().stop()


class CABST_Storage_With_Allowed_Encryption(TestBase):
    def __init__(self, policy, mode, file_prefix, file_directory, clear_on_close):
        TestBase.__init__(self)
        self._desc = 'Write/read file on ??? storage (??? storage allowed, encryption required)'
        self._policy = policy
        self._mode = mode
        self._file_prefix = file_prefix
        self._file_directory = file_directory
        self._clear_on_close = clear_on_close

    def run(self):
        try:
            self.start()
            filename = generate_filename()
            filetext = generate_filetext()
            logger.debug('filename=%s, filetext=%s' % (filename, filetext))
            logger.debug('preparing and launching app...')
            ta = TAoneApp()
            runas = ta.packbund() if self._mode == 'appdata' else None
            ta.prep(policy=self._policy, reinstall='on_policy_changed')
            ta.startup(param=dict(extras=dict(do='storage')))
            #
            if self._mode == 'xstorage':
                logger.debug('getting external files dir...')
                self._file_directory = ta.get_external_dir()['filesDir']
                logger.debug('external files dir=%s' % self._file_directory)
            #
            physical_path = '%s/%s' % (self._file_directory, filename)
            android_device.file_delete(path=physical_path, runas=runas)
            # prior to writing file, keep file list in the dir
            dirinfo = android_device.file_diff(self._file_directory, runas=runas)
            logger.debug('writing file to app data storage...')
            ta.write_storage(mode=self._mode, path=self._file_prefix + filename, content=filetext, block=False)
            if self._mode == 'xstorage':
                logger.debug('checking if external files dir is encrypted...')
                if android_device.file_exist(self._file_directory, runas=runas):
                   raise Exception('External files directory is not encrypted: path=%s' % self._file_directory)
                encrypted_physical_path = None
            else:
                logger.debug('verifying encrypted file exists...')
                if android_device.file_exist(path=physical_path, runas=runas):
                    raise Exception('Written file exists but is not encrypted: %s' % physical_path)
                dirdiff = android_device.file_diff(dirinfo, runas=runas)
                logger.debug('file_diff=%s' % dirdiff)
                if len(dirdiff) != 1:
                    logger.debug('original state of the dir:')
                    logger.debug(str(dirinfo))
                    logger.debug('current state of the dir:')
                    logger.debug(android_device.file_list(self._file_directory, runas=runas))
                    raise Exception('Unexpected result of file list difference in the directory')
                encrypted_physical_path = '%s/%s' % (self._file_directory, dirdiff.pop())
                content = android_device.file_cat(path=encrypted_physical_path, runas=runas)
                logger.debug('encrypted file content=%s' % content)
                if content == filetext:
                    raise Exception('Written file content is not encrypted: original=%s' % filetext)

            logger.debug('reading file on app data storage...')
            # should be successful
            ta.read_storage(verify=filetext, block=False)

            # re-launch app and verify file still remains
            ta.stop()
            ta.startup(param=dict(extras=dict(do='storage')))
            if not self._clear_on_close:
                if encrypted_physical_path:
                    if not android_device.file_exist(path=encrypted_physical_path, runas=runas):
                        raise Exception('Written file doesn\'t exist after restarting app: %s' % encrypted_physical_path)
                logger.debug('deleting file on app data storage...')
                ta.delete_storage(mode=self._mode, path=self._file_prefix + filename, block=False)
                logger.debug('verifying file deleted...')
                if encrypted_physical_path:
                    if android_device.file_exist(path=encrypted_physical_path, runas=runas):
                        raise Exception('Written file has not been deleted: %s' % encrypted_physical_path)
            else:
                if encrypted_physical_path:
                    if android_device.file_exist(path=encrypted_physical_path, runas=runas):
                        raise Exception('Written file still exists after restarting app: %s' % encrypted_physical_path)
            ta.read_storage(mode=self._mode, path=self._file_prefix + filename, verify=filetext, block=True)
            self.complete()
        except Exception as e:
            self.abend(e, take_log=True, take_screenshot=True)
            self.post_error()
        TAoneApp().stop()


class CABST_Storage_With_Blocked_Encryption(TestBase):
    def __init__(self, policy, mode, file_prefix, file_directory):
        TestBase.__init__(self)
        self._desc = 'Block from writing file on ??? storage (??? storage not allowed, encryption required)'
        self._policy = policy
        self._mode = mode
        self._file_prefix = file_prefix
        self._file_directory = file_directory

    def run(self):
        try:
            self.start()
            filename = generate_filename()
            filetext = generate_filetext()
            logger.debug('filename=%s, filetext=%s' % (filename, filetext))
            logger.debug('preparing and launching app...')
            ta = TAoneApp()
            ta.prep(policy=self._policy, reinstall='on_policy_changed')
            ta.startup(param=dict(extras=dict(do='storage')))
            #
            if self._mode == 'xstorage':
                logger.debug('getting external files dir...')
                self._file_directory = ta.get_external_dir()['filesDir']
                logger.debug('external files dir=%s' % self._file_directory)
            #
            physical_path = '%s/%s' % (self._file_directory, filename)
            android_device.file_delete(path=physical_path, runas=ta.packbund())
            # prior to writing file, keep file list in the dir
            dirinfo = android_device.file_diff(self._file_directory, runas=ta.packbund())
            logger.debug('writing file to app data storage...')
            ta.write_storage(mode=self._mode, path=self._file_prefix + filename, content=filetext, block=True)
            if self._mode != 'xstorage':
                logger.debug('verifying file exists...')
                dirdiff = android_device.file_diff(dirinfo, runas=ta.packbund())
                if len(dirdiff) != 0:
                    logger.debug('original state of the dir:')
                    logger.debug(str(dirinfo))
                    logger.debug('current state of the dir:')
                    logger.debug(android_device.file_list(self._file_directory, runas=ta.packbund()))
                    raise Exception('Unexpected result of file list difference in the directory --- file has been added')
            # should fail to read the file
            ta.read_storage(verify=filetext, block=True)
            self.complete()
        except Exception as e:
            self.abend(e, take_log=True, take_screenshot=True)
            self.post_error()
        TAoneApp().stop()


class C0010_AppData_With_All_Allowed_No_Encryption(CABST_Storage_With_Allowed_No_Encryption):
    def __init__(self):
        CABST_Storage_With_Allowed_No_Encryption.__init__(self,
                                                          policy='xTA - storage allow - no encrypt',
                                                          mode='appdata', file_prefix='', file_directory='files',
                                                          clear_on_close=False)
        self._desc = 'Write/read file on App data storage (all storage allowed, no encryption)'


class C0020_External_With_All_Allowed_No_Encryption(CABST_Storage_With_Allowed_No_Encryption):
    def __init__(self):
        CABST_Storage_With_Allowed_No_Encryption.__init__(self,
                                                          policy='xTA - storage allow - no encrypt',
                                                          mode='xstorage', file_prefix='', file_directory=None,
                                                          clear_on_close=False)
        self._desc = 'Write/read file on external storage (all storage allowed, no encryption)'


class C0031_SDcard1_With_All_Allowed_No_Encryption(CABST_Storage_With_Allowed_No_Encryption):
    def __init__(self):
        CABST_Storage_With_Allowed_No_Encryption.__init__(self,
                                                          policy='xTA - storage allow - no encrypt',
                                                          mode='fullpath',
                                                          file_prefix='/sdcard/',
                                                          file_directory='/sdcard',
                                                          clear_on_close=False)
        self._desc = 'Write/read file on SD card storage /sdcard (all storage allowed, no encryption)'


class C0032_SDcard2_With_All_Allowed_No_Encryption(CABST_Storage_With_Allowed_No_Encryption):
    def __init__(self):
        CABST_Storage_With_Allowed_No_Encryption.__init__(self,
                                                          policy='xTA - storage allow - no encrypt',
                                                          mode='fullpath',
                                                          file_prefix='/storage/sdcard0/',
                                                          file_directory='/storage/sdcard0',
                                                          clear_on_close=False)
        self._desc = 'Write/read file on SD card storage /storage/sdcard0 (all storage allowed, no encryption)'


class C0033_SDcard3_With_All_Allowed_No_Encryption(CABST_Storage_With_Allowed_No_Encryption):
    def __init__(self):
        CABST_Storage_With_Allowed_No_Encryption.__init__(self,
                                                          policy='xTA - storage allow - no encrypt',
                                                          mode='fullpath',
                                                          file_prefix='/storage/emulated/legacy/',
                                                          file_directory='/storage/emulated/legacy',
                                                          clear_on_close=False)
        self._desc = 'Write/read file on SD card storage /storage/emulated/legacy (all storage allowed, no encryption)'


class C0110_AppData_With_SDcard_Blocked_No_Encryption(CABST_Storage_With_Allowed_No_Encryption):
    def __init__(self):
        CABST_Storage_With_Allowed_No_Encryption.__init__(self,
                                                          policy='xTA - storage sdcard block - no encrypt',
                                                          mode='appdata', file_prefix='', file_directory='files',
                                                          clear_on_close=False)
        self._desc = 'Write/read file on App data storage (sdcard storage not allowed, no encryption)'


class C0120_External_With_SDcard_Blocked_No_Encryption(CABST_Storage_With_Blocked_No_Encryption):
    def __init__(self):
        CABST_Storage_With_Blocked_No_Encryption.__init__(self,
                                                          policy='xTA - storage sdcard block - no encrypt',
                                                          mode='xstorage', file_prefix='', file_directory=None)
        self._desc = 'Block from writing file on external storage (sdcard storage not allowed, no encryption)'


class C0131_SDcard1_With_SDcard_Blocked_No_Encryption(CABST_Storage_With_Blocked_No_Encryption):
    def __init__(self):
        CABST_Storage_With_Blocked_No_Encryption.__init__(self,
                                                          policy='xTA - storage sdcard block - no encrypt',
                                                          mode='fullpath',
                                                          file_prefix='/sdcard/',
                                                          file_directory='/sdcard')
        self._desc = 'Block from writing file on SD card storage /sdcard (sdcard storage not allowed, no encryption)'


class C0132_SDcard2_With_SDcard_Blocked_No_Encryption(CABST_Storage_With_Blocked_No_Encryption):
    def __init__(self):
        CABST_Storage_With_Blocked_No_Encryption.__init__(self,
                                                          policy='xTA - storage sdcard block - no encrypt',
                                                          mode='fullpath',
                                                          file_prefix='/storage/sdcard0/',
                                                          file_directory='/storage/sdcard0')
        self._desc = 'Block from writing file on SD card storage /storage/sdcard0 (sdcard storage allowed, no encryption)'


class C0133_SDcard3_With_SDcard_Blocked_No_Encryption(CABST_Storage_With_Blocked_No_Encryption):
    def __init__(self):
        CABST_Storage_With_Blocked_No_Encryption.__init__(self,
                                                          policy='xTA - storage sdcard block - no encrypt',
                                                          mode='fullpath',
                                                          file_prefix='/storage/emulated/legacy/',
                                                          file_directory='/storage/emulated/legacy')
        self._desc = 'Block from writing file on SD card storage /storage/emulated/legacy (sdcard storage allowed, no encryption)'


class C0210_AppData_With_All_Blocked_No_Encryption(CABST_Storage_With_Blocked_No_Encryption):
    def __init__(self):
        CABST_Storage_With_Blocked_No_Encryption.__init__(self,
                                                          policy='xTA - storage block - no encrypt',
                                                          mode='appdata', file_prefix='', file_directory='files')
        self._desc = 'Block from writing file on App data storage (all storage not allowed, no encryption)'


class C0220_External_With_All_Blocked_No_Encryption(CABST_Storage_With_Blocked_No_Encryption):
    def __init__(self):
        CABST_Storage_With_Blocked_No_Encryption.__init__(self,
                                                          policy='xTA - storage block - no encrypt',
                                                          mode='xstorage', file_prefix='', file_directory=None)
        self._desc = 'Block from writing file on external storage (all storage not allowed, no encryption)'


class C0231_SDcard1_With_All_Blocked_No_Encryption(CABST_Storage_With_Blocked_No_Encryption):
    def __init__(self):
        CABST_Storage_With_Blocked_No_Encryption.__init__(self,
                                                          policy='xTA - storage block - no encrypt',
                                                          mode='fullpath',
                                                          file_prefix='/sdcard/',
                                                          file_directory='/sdcard')
        self._desc = 'Block from writing file on SD card storage /sdcard (all storage not allowed, no encryption)'


class C0232_SDcard2_With_All_Blocked_No_Encryption(CABST_Storage_With_Blocked_No_Encryption):
    def __init__(self):
        CABST_Storage_With_Blocked_No_Encryption.__init__(self,
                                                          policy='xTA - storage block - no encrypt',
                                                          mode='fullpath',
                                                          file_prefix='/storage/sdcard0/',
                                                          file_directory='/storage/sdcard0')
        self._desc = 'Block from writing file on SD card storage /storage/sdcard0 (all storage allowed, no encryption)'


class C0233_SDcard3_With_All_Blocked_No_Encryption(CABST_Storage_With_Blocked_No_Encryption):
    def __init__(self):
        CABST_Storage_With_Blocked_No_Encryption.__init__(self,
                                                          policy='xTA - storage block - no encrypt',
                                                          mode='fullpath',
                                                          file_prefix='/storage/emulated/legacy/',
                                                          file_directory='/storage/emulated/legacy')
        self._desc = 'Block from writing file on SD card storage /storage/emulated/legacy (all storage allowed, no encryption)'


class C1010_AppData_With_All_Allowed_Encryption(CABST_Storage_With_Allowed_Encryption):
    def __init__(self):
        CABST_Storage_With_Allowed_Encryption.__init__(self,
                                                       policy='xTA - default',
                                                       mode='appdata', file_prefix='', file_directory='files',
                                                       clear_on_close=False)
        self._desc = 'Write/read file on App data storage (all storage allowed, encryption required)'


class C1020_External_With_All_Allowed_Encryption(CABST_Storage_With_Allowed_Encryption):
    def __init__(self):
        CABST_Storage_With_Allowed_Encryption.__init__(self,
                                                       policy='xTA - default',
                                                       mode='xstorage', file_prefix='', file_directory=None,
                                                       clear_on_close=False)
        self._desc = 'Write/read file on external storage (all storage allowed, encryption required)'


class C1031_SDcard1_With_All_Allowed_Encryption(CABST_Storage_With_Allowed_Encryption):
    def __init__(self):
        CABST_Storage_With_Allowed_Encryption.__init__(self,
                                                       policy='xTA - default',
                                                       mode='fullpath',
                                                       file_prefix='/sdcard/',
                                                       file_directory='/sdcard',
                                                       clear_on_close=False)
        self._desc = 'Write/read file on SD card storage /sdcard (all storage allowed, encryption required)'


class C1032_SDcard2_With_All_Allowed_Encryption(CABST_Storage_With_Allowed_Encryption):
    def __init__(self):
        CABST_Storage_With_Allowed_Encryption.__init__(self,
                                                       policy='xTA - default',
                                                       mode='fullpath',
                                                       file_prefix='/storage/sdcard0/',
                                                       file_directory='/storage/sdcard0',
                                                       clear_on_close=False)
        self._desc = 'Write/read file on SD card storage /storage/sdcard0 (all storage allowed, encryption required)'


class C1033_SDcard3_With_All_Allowed_Encryption(CABST_Storage_With_Allowed_Encryption):
    def __init__(self):
        CABST_Storage_With_Allowed_Encryption.__init__(self,
                                                       policy='xTA - default',
                                                       mode='fullpath',
                                                       file_prefix='/storage/emulated/legacy/',
                                                       file_directory='/storage/emulated/legacy',
                                                       clear_on_close=False)
        self._desc = 'Write/read file on SD card storage /storage/emulated/legacy (all storage allowed, encryption required)'


class C1110_AppData_With_SDcard_Blocked_Encryption(CABST_Storage_With_Allowed_Encryption):
    def __init__(self):
        CABST_Storage_With_Allowed_Encryption.__init__(self,
                                                       policy='xTA - storage sdcard block',
                                                       mode='appdata', file_prefix='', file_directory='files',
                                                       clear_on_close=False)
        self._desc = 'Write/read file on App data storage (sdcard storage not allowed, encryption required)'


class C1120_External_With_SDcard_Blocked_Encryption(CABST_Storage_With_Blocked_Encryption):
    def __init__(self):
        CABST_Storage_With_Blocked_Encryption.__init__(self,
                                                       policy='xTA - storage sdcard block',
                                                       mode='xstorage', file_prefix='', file_directory=None)
        self._desc = 'Block from writing file on external storage (sdcard storage not allowed, encryption required)'


class C1131_SDcard1_With_SDcard_Blocked_Encryption(CABST_Storage_With_Blocked_Encryption):
    def __init__(self):
        CABST_Storage_With_Blocked_Encryption.__init__(self,
                                                       policy='xTA - storage sdcard block',
                                                       mode='fullpath',
                                                       file_prefix='/sdcard/',
                                                       file_directory='/sdcard')
        self._desc = 'Block from writing file on SD card storage /sdcard (sdcard storage not allowed, encryption required)'


class C1132_SDcard2_With_SDcard_Blocked_Encryption(CABST_Storage_With_Blocked_Encryption):
    def __init__(self):
        CABST_Storage_With_Blocked_Encryption.__init__(self,
                                                       policy='xTA - storage sdcard block',
                                                       mode='fullpath',
                                                       file_prefix='/storage/sdcard0/',
                                                       file_directory='/storage/sdcard0')
        self._desc = 'Block from writing file on SD card storage /storage/sdcard0 (sdcard storage not allowed, encryption required)'


class C1133_SDcard3_With_SDcard_Blocked_Encryption(CABST_Storage_With_Blocked_Encryption):
    def __init__(self):
        CABST_Storage_With_Blocked_Encryption.__init__(self,
                                                       policy='xTA - storage sdcard block',
                                                       mode='fullpath',
                                                       file_prefix='/storage/emulated/legacy/',
                                                       file_directory='/storage/emulated/legacy')
        self._desc = 'Block from writing file on SD card storage /storage/emulated/legacy (sdcard storage not allowed, encryption required)'


class C1210_AppData_With_All_Blocked_Encryption(CABST_Storage_With_Blocked_Encryption):
    def __init__(self):
        CABST_Storage_With_Blocked_Encryption.__init__(self,
                                                       policy='xTA - storage block',
                                                       mode='appdata', file_prefix='', file_directory='files')
        self._desc = 'Block from writing file on App data storage (all storage not allowed, encryption required)'


class C1220_External_With_All_Blocked_Encryption(CABST_Storage_With_Blocked_Encryption):
    def __init__(self):
        CABST_Storage_With_Blocked_Encryption.__init__(self,
                                                       policy='xTA - storage block',
                                                       mode='xstorage', file_prefix='', file_directory=None)
        self._desc = 'Block from writing file on external storage (all storage not allowed, encryption required)'


class C1231_SDcard1_With_All_Blocked_Encryption(CABST_Storage_With_Blocked_Encryption):
    def __init__(self):
        CABST_Storage_With_Blocked_Encryption.__init__(self,
                                                       policy='xTA - storage block',
                                                       mode='fullpath',
                                                       file_prefix='/sdcard/',
                                                       file_directory='/sdcard')
        self._desc = 'Block from writing file on SD card storage /sdcard (all storage not allowed, encryption required)'


class C1232_SDcard2_With_All_Blocked_Encryption(CABST_Storage_With_Blocked_Encryption):
    def __init__(self):
        CABST_Storage_With_Blocked_Encryption.__init__(self,
                                                       policy='xTA - storage block',
                                                       mode='fullpath',
                                                       file_prefix='/storage/sdcard0/',
                                                       file_directory='/storage/sdcard0')
        self._desc = 'Block from writing file on SD card storage /storage/sdcard0 (all storage allowed, encryption required)'


class C1233_SDcard3_With_All_Blocked_Encryption(CABST_Storage_With_Blocked_Encryption):
    def __init__(self):
        CABST_Storage_With_Blocked_Encryption.__init__(self,
                                                       policy='xTA - storage block',
                                                       mode='fullpath',
                                                       file_prefix='/storage/emulated/legacy/',
                                                       file_directory='/storage/emulated/legacy')
        self._desc = 'Block from writing file on SD card storage /storage/emulated/legacy (all storage allowed, encryption required)'


class C2010_AppData_With_Clear_On_Close(CABST_Storage_With_Allowed_No_Encryption):
    def __init__(self):
        CABST_Storage_With_Allowed_No_Encryption.__init__(self,
                                                          policy='xTA - storage allow - no encrypt - clear on close',
                                                          mode='appdata', file_prefix='', file_directory='files',
                                                          clear_on_close=True)
        self._desc = 'Write/read file on App data storage (all storage allowed, no encryption, clear on close)'


class C2110_AppData_With_Clear_On_Close_Without_Auth(CABST_Storage_With_Allowed_No_Encryption):
    def __init__(self):
        CABST_Storage_With_Allowed_No_Encryption.__init__(self,
                                                          policy='xTA - storage allow - no encrypt - clear on close - no auth',
                                                          mode='appdata', file_prefix='', file_directory='files',
                                                          clear_on_close=True)
        self._desc = 'Write/read file on App data storage (all storage allowed, no encryption, clear on close, auth NOT required)'

    def run(self):
        CABST_Storage_With_Allowed_No_Encryption.run(self)
        from apps.android.workhub import WorkHub
        WorkHub().stop()

