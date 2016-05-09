settings = dict(
    server=dict(
        host='SERVERNAME.com',
        api_key='APIKEY0000=',
        ios_packbund='com.PACKAGE',
        ios_codesign='./CODESIGN.p12',
        ios_codesign_passphrase='passphrase',
        workhub='WORKHUB NAME',
        username='TEST USER NAME',
        password='TEST USER PASSWORD',
        email_password='TEST EMAIL PASSWORD'
    ),
    device=dict(
        android_serial=None,
        ios_version='',
        ios_device_name='',
        ios_udid=None
    ),
    local=dict(
        out_folder='./',
        log_file_name='TAoneJ1.log',
        debug_file_name='TAoneJ1.debug.log',
        appium_log_file_name='TAoneJ1.appium.log',
        UiA_JAR_name='TAoneJ1.jar',
        UiA_JAR_folder='./bin/',
        UiA_packbund='com.UIAUTOMATOR_PACKAGE',
        ss_folder='./bin/ss/',
        apk_folder='./apk/',
        apk_files={
            'com.symantec.mobile.securebrowser': 'com.symantec.mobile.securebrowser.20151106.apk',
            'com.symantec.securemail': 'com.symantec.securemail.20160118.apk',
            'com.symantec.jdc.taoneapp': 'com.symantec.jdc.taoneapp.base.apk',
            'com.symantec.jdc.taonebuddy': 'com.symantec.jdc.taonebuddy.base.apk',
            'com.symantec.jdc.taoneutil': 'com.symantec.jdc.taoneutil.base.apk',
            'com.activator.workmail': 'com.activator.workmail.apk'
        },
        Appium_workhub_port=4723,
        Appium_app_ports=[4724, 4725, 4726],
        ipa_folder='./ipa/',
        testweb_url='http://TESTWEB.com',
        testweb_ip_addr='10.10.10.10'
    ),
    command=dict(
        adb='~/Library/Android/sdk/platform-tools/adb',
        curl='/usr/bin/curl',
        appium='/usr/local/bin/appium'
    ),
    info=dict(
        groups={},
        app_policies={
            'xTA - default': dict(
                param=dict(
                    policy_name='xTA - default',
                    auth_required=True,
                    auth_timeout_enabled=False,
                    allow_interapp_sso=False,
                    storage_allowed=True,
                    encryption_required=True,
                    allow_sdcard_storage=True,
                    clear_data_on_close=False,
                    document_sharing='allow',
                    clipboard_sharing='allow',
                    browser_preference='system'),
                data=None),
            'xTA - reauth - one minute': dict(
                param=dict(
                    policy_name='xTA - reauth - one minute',
                    auth_timeout_enabled=True,
                    auth_timeout=1),
                data=None),
            'xTA - clipboard - workspace': dict(
                param=dict(
                    policy_name='xTA - clipboard - workspace',
                    clipboard_sharing='workspace'
                    ),
                data=None),
            'xTA - clipboard - block': dict(
                param=dict(
                    policy_name='xTA - clipboard - block',
                    clipboard_sharing='block'),
                data=None),
            'xTA - document - workspace': dict(
                param=dict(
                    policy_name='xTA - document - workspace',
                    document_sharing='workspace'),
                data=None),
            'xTA - document - workspace - no encrypt': dict(
                param=dict(
                    policy_name='xTA - document - workspace - no encrypt',
                    encryption_required=False,
                    document_sharing='workspace'),
                data=None),
            'xTA - document - block': dict(
                param=dict(
                    policy_name='xTA - document - block',
                    document_sharing='block'),
                data=None),
            'xTA - browser - workspace': dict(
                param=dict(
                    policy_name='xTA - browser - workspace',
                    browser_preference='workspace'),
                data=None),
            'xTA - storage sdcard block': dict(
                param=dict(
                    policy_name='xTA - storage sdcard block',
                    allow_sdcard_storage=False),
                data=None),
            'xTA - storage block': dict(
                param=dict(
                    policy_name='xTA - storage block',
                    storage_allowed=False),
                data=None),
            'xTA - storage allow - no encrypt': dict(
                param=dict(
                    policy_name='xTA - storage allow - no encrypt',
                    encryption_required=False),
                data=None),
            'xTA - storage sdcard block - no encrypt': dict(
                param=dict(
                    policy_name='xTA - storage sdcard block - no encrypt',
                    encryption_required=False,
                    allow_sdcard_storage=False),
                data=None),
            'xTA - storage block - no encrypt': dict(
                param=dict(
                    policy_name='xTA - storage block - no encrypt',
                    encryption_required=False,
                    storage_allowed=False),
                data=None),
            'xTA - storage allow - no encrypt - clear on close': dict(
                param=dict(
                    policy_name='xTA - storage allow - no encrypt - clear on close',
                    encryption_required=False,
                    clear_data_on_close=True),
                data=None),
            'xTA - storage allow - no encrypt - clear on close - no auth': dict(
                param=dict(
                    policy_name='xTA - storage allow - no encrypt - clear on close - no auth',
                    auth_required=False,
                    encryption_required=False,
                    clear_data_on_close=True),
                data=None),
            'xTA - nac - whitelist': dict(
                param=dict(
                    policy_name='xTA - nac - whitelist',
                    network_access_control=[
                        dict(protocols=1,
                             host='*.google.com'),
                        dict(protocols=1,
                             host='*.google.co.jp')
                    ]),
                data=None),
            'xTA - nac - whitelist with port': dict(
                param=dict(
                    policy_name='xTA - nac - whitelist with port',
                    network_access_control=[
                        dict(protocols=1,
                             host='*.google.com',
                             port='80,443'),
                        dict(protocols=1,
                             host='*.google.co.jp',
                             port='80,443')
                    ]),
                data=None),
            'xTA - nac - whitelist - clear on close': dict(
                param=dict(
                    policy_name='xTA - nac - whitelist - clear on close',
                    network_access_control=[
                        dict(protocols=1,
                             host='*.google.com'),
                        dict(protocols=1,
                             host='*.google.co.jp')
                    ],
                    clear_data_on_close=True),
                data=None),
            'xTA - nac - whitelist - ip wildcard': dict(
                param=dict(
                    policy_name='xTA - nac - whitelist - ip wildcard',
                    network_access_control=[
                        dict(protocols=1,
                             host='10.159.0.0/16')
                    ]),
                data=None),
            'xTA - nac - whitelist - port 80': dict(
                param=dict(
                    policy_name='xTA - nac - whitelist - port 80',
                    network_access_control=[
                        dict(protocols=1,
                             host='*',
                             port='80')
                    ]),
                data=None),
            'xTA - nac - whitelist - port range': dict(
                param=dict(
                    policy_name='xTA - nac - whitelist - port range',
                    network_access_control=[
                        dict(protocols=1,
                             host='*',
                             port='1-1024')
                    ]),
                data=None),
            'xTA - nac - whitelist - port wrong': dict(
                param=dict(
                    policy_name='xTA - nac - whitelist - port wrong',
                    network_access_control=[
                        dict(protocols=1,
                             host='*',
                             port='88,555')
                    ]),
                data=None),
            'xTA - nac - ssl required': dict(
                param=dict(
                    policy_name='xTA - nac - ssl required',
                    network_access_control=[
                        dict(require_ssl=True)
                    ]),
                data=None),
            'xTA - nac - credential injection': dict(
                param=dict(
                    policy_name='xTA - nac - credential injection',
                    network_access_control=[
                        dict(injection_type=1)
                    ]),
                data=None)
        },
        default_policy='xTA - default',
        apps={
            'com.symantec.mobile.securebrowser': dict(
                type='sealed',
                name='Symantec Work Web',
                metadata=None,
                policy_changed=False),
            'com.symantec.securemail': dict(
                type='sealed',
                name='Symantec Work Mail',
                metadata=None,
                policy_changed=False),
            'com.symantec.jdc.taoneapp': dict(
                type='native',
                name='TAoneApp',
                metadata=None,
                policy_changed=False),
            'com.symantec.jdc.taonebuddy': dict(
                type='native',
                name='TAoneBuddy',
                metadata=None,
                policy_changed=False),
            # 'swa:edit': dict(
            #     type='swa',
            #     name='SWA edit',
            #     metadata=None,
            #     policy_changed=False),
            'swa:text': dict(
                type='swa',
                name='SWA text',
                metadata=None,
                policy_changed=False),
            'swa:ipaddr': dict(
                type='swa',
                name='SWA IP addr',
                metadata=None,
                policy_changed=False),
            'swa:popup': dict(
                type='swa',
                name='SWA popup',
                metadata=None,
                policy_changed=False),
            'swa:basic': dict(
                type='swa',
                name='SWA basic auth',
                metadata=None,
                policy_changed=False),
            'swa:digest': dict(
                type='swa',
                name='SWA digest auth',
                metadata=None,
                policy_changed=False),
            'swa:symantec': dict(
                type='swa',
                name='SWA Symantec',
                metadata=None,
                policy_changed=False),
            'swa:google': dict(
                type='swa',
                name='SWA Google',
                metadata=None,
                policy_changed=False),
            'swa:linkedin': dict(
                type='swa',
                name='SWA Linkedin',
                metadata=None,
                policy_changed=False),
            'swa:yahoo': dict(
                type='swa',
                name='SWA Yahoo',
                metadata=None,
                policy_changed=False)
        }
    )
)
