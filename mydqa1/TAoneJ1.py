import sys
import traceback

import config
from config import argument

try:
    config.initiate_android(argument.init_parser().parse_args())

    if config._command:
        from helper import logger
        logger.set_file(None, None, True)
        if config._command == 'workhub':
            from apps.android.workhub import WorkHub
            WorkHub().prep(reinstall=True)
        elif config._command == 'workhub.reset':
            from apps.android.workhub import WorkHub
            WorkHub().reset(startup=False)
        elif config._command == 'apps':
            from apps.android import prep_wrapped_apps
            prep_wrapped_apps(install=False)
        elif config._command == 'apps.install':
            from apps.android import prep_wrapped_apps
            prep_wrapped_apps(install=True)
        elif config._command == 'rewrap':
            from apps.android import rewrap_apps
            rewrap_apps()
        elif config._command == 'policies':
            from apps.android import prep_policies
            prep_policies()
        import shutil
        shutil.rmtree(config.settings.local.out_path)
        sys.exit(0)

    ############################################
    # Work Hub and other Apps - installation and initial startup
    from test import T000
    T000.C0000_Launch_WorkHub().run()
    T000.C0011_Launch_WorkWeb().run()
    T000.C0012_Launch_WorkMail().run()
    T000.C0021_Launch_SWA().run()
    T000.C0022_Launch_SWA_Google().run()
    T000.C0031_Launch_WrappedApp().run()
    T000.C0040_Prep_Other_Apps().run()

    ############################################
    # App Policy - Authentication
    from test import T010
    T010.C0001_Auth_Required_WorkWeb().run()
    T010.C0002_Auth_Required_SWA().run()
    T010.C0003_Auth_Required_WrappedApp().run()
    T010.C0101_Auth_Timeout_One_Minute_WorkMail().run()
    T010.C0103_Auth_Timeout_One_Minute_WrappedApp().run()
    T010.C0111_Auth_Not_Timeout_WorkMail().run()
    T010.C0113_Auth_Not_Timeout_WrappedApp().run()
    T010.C9003_Auth_Attempt_With_Wrong_Password_Five_Times_WrappedApp().run()

    ############################################
    # App Policy - On-device storage
    from test import T020
    T020.C0010_AppData_With_All_Allowed_No_Encryption().run()
    T020.C0020_External_With_All_Allowed_No_Encryption().run()
    T020.C0031_SDcard1_With_All_Allowed_No_Encryption().run()
    T020.C0032_SDcard2_With_All_Allowed_No_Encryption().run()
    T020.C0033_SDcard3_With_All_Allowed_No_Encryption().run()
    T020.C0110_AppData_With_SDcard_Blocked_No_Encryption().run()
    T020.C0120_External_With_SDcard_Blocked_No_Encryption().run()
    T020.C0131_SDcard1_With_SDcard_Blocked_No_Encryption().run()
    T020.C0132_SDcard2_With_SDcard_Blocked_No_Encryption().run()
    T020.C0133_SDcard3_With_SDcard_Blocked_No_Encryption().run()

    # 'storage block' option is no longer available from 5.4
    # T020.C0210_AppData_With_All_Blocked_No_Encryption().run()
    # T020.C0220_External_With_All_Blocked_No_Encryption().run()
    # T020.C0231_SDcard1_With_All_Blocked_No_Encryption().run()
    # T020.C0232_SDcard2_With_All_Blocked_No_Encryption().run()
    # T020.C0233_SDcard3_With_All_Blocked_No_Encryption().run()

    T020.C1010_AppData_With_All_Allowed_Encryption().run()
    T020.C1020_External_With_All_Allowed_Encryption().run()
    T020.C1031_SDcard1_With_All_Allowed_Encryption().run()
    T020.C1032_SDcard2_With_All_Allowed_Encryption().run()
    T020.C1033_SDcard3_With_All_Allowed_Encryption().run()
    T020.C1110_AppData_With_SDcard_Blocked_Encryption().run()
    T020.C1120_External_With_SDcard_Blocked_Encryption().run()
    T020.C1131_SDcard1_With_SDcard_Blocked_Encryption().run()
    T020.C1132_SDcard2_With_SDcard_Blocked_Encryption().run()
    T020.C1133_SDcard3_With_SDcard_Blocked_Encryption().run()

    # 'storage block' option is no longer available from 5.4
    # T020.C1210_AppData_With_All_Blocked_Encryption().run()
    # T020.C1220_External_With_All_Blocked_Encryption().run()
    # T020.C1231_SDcard1_With_All_Blocked_Encryption().run()
    # T020.C1232_SDcard2_With_All_Blocked_Encryption().run()
    # T020.C1233_SDcard3_With_All_Blocked_Encryption().run()

    T020.C2010_AppData_With_Clear_On_Close().run()

    # No use of 'authentication not required' for SoftBank cases
    # Also, timing is unclear when the policy is applied to app on device...
    # T020.C2110_AppData_With_Clear_On_Close_Without_Auth().run()

    ###########################################
    # App Policy - Usage restrictions - Document sharing
    from test import T031
    T031.C0000_Receiver_Apps().run()
    T031.C0001_Share_WorkWeb_All_With_Wrapped_All().run()
    T031.C0002_Share_WorkWeb_All_With_WorkMail_All().run()
    T031.C0011_Share_WorkWeb_All_With_Wrapped_WS().run()
    T031.C0012_Share_WorkWeb_All_With_WorkMail_WS().run()
    T031.C0021_Share_WorkWeb_All_With_Wrapped_Block().run()
    T031.C0022_Share_WorkWeb_All_With_WorkMail_Block().run()
    T031.C0101_Share_SWA_All_With_Wrapped_All().run()
    T031.C0102_Share_SWA_All_With_WorkMail_All().run()
    T031.C0111_Share_SWA_All_With_Wrapped_WS().run()
    T031.C0112_Share_SWA_All_With_WorkMail_WS().run()
    T031.C0121_Share_SWA_All_With_Wrapped_Block().run()
    T031.C0122_Share_SWA_All_With_WorkMail_Block().run()
    T031.C0201_Share_WrappedApp_All_With_Wrapped_All().run()
    T031.C0202_Share_WrappedApp_All_With_WorkMail_All().run()
    T031.C0211_Share_WrappedApp_All_With_Wrapped_WS().run()
    T031.C0212_Share_WrappedApp_All_With_WorkMail_WS().run()
    T031.C0221_Share_WrappedApp_All_With_Wrapped_Block().run()
    T031.C0222_Share_WrappedApp_All_With_WorkMail_Block().run()
    T031.C1001_Share_WorkWeb_WS_With_Wrapped_All().run()
    T031.C1002_Share_WorkWeb_WS_With_WorkMail_All().run()
    T031.C1003_Share_WorkWeb_WS_No_Encrypt_With_Wrapped_All().run()
    T031.C1004_Share_WorkWeb_WS_No_Encrypt_With_WorkMail_All().run()
    T031.C1011_Share_WorkWeb_WS_With_Wrapped_WS().run()
    T031.C1012_Share_WorkWeb_WS_With_WorkMail_WS().run()
    T031.C1021_Share_WorkWeb_WS_With_Wrapped_Block().run()
    T031.C1022_Share_WorkWeb_WS_With_WorkMail_Block().run()
    T031.C1101_Share_SWA_WS_With_Wrapped_All().run()
    T031.C1102_Share_SWA_WS_With_WorkMail_All().run()
    T031.C1103_Share_SWA_WS_No_Encrypt_With_Wrapped_All().run()
    T031.C1104_Share_SWA_WS_No_Encrypt_With_WorkMail_All().run()
    T031.C1111_Share_SWA_WS_With_Wrapped_WS().run()
    T031.C1112_Share_SWA_WS_With_WorkMail_WS().run()
    T031.C1121_Share_SWA_WS_With_Wrapped_Block().run()
    T031.C1122_Share_SWA_WS_With_WorkMail_Block().run()
    T031.C1201_Share_WrappedApp_WS_With_Wrapped_All().run()
    T031.C1202_Share_WrappedApp_WS_With_WorkMail_All().run()
    T031.C1203_Share_WrappedApp_WS_No_Encrypt_With_Wrapped_All().run()
    T031.C1204_Share_WrappedApp_WS_No_Encrypt_With_WorkMail_All().run()
    T031.C1211_Share_WrappedApp_WS_With_Wrapped_WS().run()
    T031.C1212_Share_WrappedApp_WS_With_WorkMail_WS().run()
    T031.C1221_Share_WrappedApp_WS_With_Wrapped_Block().run()
    T031.C1222_Share_WrappedApp_WS_With_WorkMail_Block().run()
    T031.C2000_Share_WorkWeb_Block().run()
    T031.C2100_Share_SWA_Block().run()
    T031.C2200_Share_WrappedApp_Block().run()
    T031.C5001_Share_WorkWeb_All_Encrypt_With_Unwrapped().run()
    T031.C5002_Share_SWA_All_Encrypt_With_Unwrapped().run()
    T031.C5003_Share_WrappedApp_All_Encrypt_With_Unwrapped().run()

    # ###########################################
    # App Policy - Usage restrictions - Clipboard sharing
    from test import T032
    T032.C0001_Copy_WorkWeb_All().run()
    T032.C0001s01_Paste_WorkWeb_All_From_WorkWeb_All().run()
    T032.C0001s02_Paste_SWA_All_From_WorkWeb_All().run()
    T032.C0001s03_Paste_WrappedApp_All_From_WorkWeb_All().run()
    T032.C0001s09_Paste_Unwrapped_From_WorkWeb_All().run()
    T032.C0001s11_Paste_WorkWeb_WS_From_WorkWeb_All().run()
    T032.C0001s12_Paste_SWA_WS_From_WorkWeb_All().run()
    T032.C0001s13_Paste_WrappedApp_WS_From_WorkWeb_All().run()
    T032.C0001s21_Paste_WorkWeb_Block_From_WorkWeb_All().run()
    T032.C0001s22_Paste_SWA_Block_From_WorkWeb_All().run()
    T032.C0001s23_Paste_WrappedApp_Block_From_WorkWeb_All().run()
    T032.C0002_Copy_SWA_All().run()
    T032.C0002s01_Paste_WorkWeb_All_From_SWA_All().run()
    T032.C0002s02_Paste_SWA_All_From_SWA_All().run()
    T032.C0002s03_Paste_WrappedApp_All_From_SWA_All().run()
    T032.C0002s09_Paste_Unwrapped_From_SWA_All().run()
    T032.C0002s11_Paste_WorkWeb_WS_From_SWA_All().run()
    T032.C0002s12_Paste_SWA_WS_From_SWA_All().run()
    T032.C0002s13_Paste_WrappedApp_WS_From_SWA_All().run()
    T032.C0002s21_Paste_WorkWeb_Block_From_SWA_All().run()
    T032.C0002s22_Paste_SWA_Block_From_SWA_All().run()
    T032.C0002s23_Paste_WrappedApp_Block_From_SWA_All().run()
    T032.C0003_Copy_WrappedApp_All().run()
    T032.C0003s01_Paste_WorkWeb_All_From_WrappedApp_All().run()
    T032.C0003s02_Paste_SWA_All_From_WrappedApp_All().run()
    T032.C0003s03_Paste_WrappedApp_All_From_WrappedApp_All().run()
    T032.C0003s09_Paste_Unwrapped_From_WrappedApp_All().run()
    T032.C0003s11_Paste_WorkWeb_WS_From_WrappedApp_All().run()
    T032.C0003s12_Paste_SWA_WS_From_WrappedApp_All().run()
    T032.C0003s13_Paste_WrappedApp_WS_From_WrappedApp_All().run()
    T032.C0003s21_Paste_WorkWeb_Block_From_WrappedApp_All().run()
    T032.C0003s22_Paste_SWA_Block_From_WrappedApp_All().run()
    T032.C0003s23_Paste_WrappedApp_Block_From_WrappedApp_All().run()
    T032.C0011_Copy_WorkWeb_WS().run()
    T032.C0011s01_Paste_WorkWeb_All_From_WorkWeb_WS().run()
    T032.C0011s02_Paste_SWA_All_From_WorkWeb_WS().run()
    T032.C0011s03_Paste_WrappedApp_All_From_WorkWeb_WS().run()
    T032.C0011s09_Paste_Unwrapped_From_WorkWeb_WS().run()
    T032.C0011s11_Paste_WorkWeb_WS_From_WorkWeb_WS().run()
    T032.C0011s12_Paste_SWA_WS_From_WorkWeb_WS().run()
    T032.C0011s13_Paste_WrappedApp_WS_From_WorkWeb_WS().run()
    T032.C0011s21_Paste_WorkWeb_Block_From_WorkWeb_WS().run()
    T032.C0011s22_Paste_SWA_Block_From_WorkWeb_WS().run()
    T032.C0011s23_Paste_WrappedApp_Block_From_WorkWeb_WS().run()
    T032.C0012_Copy_SWA_WS().run()
    T032.C0012s01_Paste_WorkWeb_All_From_SWA_WS().run()
    T032.C0012s02_Paste_SWA_All_From_SWA_WS().run()
    T032.C0012s03_Paste_WrappedApp_All_From_SWA_WS().run()
    T032.C0012s09_Paste_Unwrapped_From_SWA_WS().run()
    T032.C0012s11_Paste_WorkWeb_WS_From_SWA_WS().run()
    T032.C0012s12_Paste_SWA_WS_From_SWA_WS().run()
    T032.C0012s13_Paste_WrappedApp_WS_From_SWA_WS().run()
    T032.C0012s21_Paste_WorkWeb_Block_From_SWA_WS().run()
    T032.C0012s22_Paste_SWA_Block_From_SWA_WS().run()
    T032.C0012s23_Paste_WrappedApp_Block_From_SWA_WS().run()
    T032.C0013_Copy_WrappedApp_WS().run()
    T032.C0013s01_Paste_WorkWeb_All_From_WrappedApp_WS().run()
    T032.C0013s02_Paste_SWA_All_From_WrappedApp_WS().run()
    T032.C0013s03_Paste_WrappedApp_All_From_WrappedApp_WS().run()
    T032.C0013s09_Paste_Unwrapped_From_WrappedApp_WS().run()
    T032.C0013s11_Paste_WorkWeb_WS_From_WrappedApp_WS().run()
    T032.C0013s12_Paste_SWA_WS_From_WrappedApp_WS().run()
    T032.C0013s13_Paste_WrappedApp_WS_From_WrappedApp_WS().run()
    T032.C0013s21_Paste_WorkWeb_Block_From_WrappedApp_WS().run()
    T032.C0013s22_Paste_SWA_Block_From_WrappedApp_WS().run()
    T032.C0013s23_Paste_WrappedApp_Block_From_WrappedApp_WS().run()
    T032.C0021_Copy_WorkWeb_Block().run()
    T032.C0022_Copy_SWA_Block().run()
    T032.C0023_Copy_WrappedApp_Block().run()
    T032.C9002_Paste_WrappedApp_WS_And_Pause().run()
    T032.C9003_Copy_HTML_SWA_WS().run()
    T032.C9011_Paste_WrappedApp_WS_From_System_With_WS_Clipboard_Empty().run()
    T032.C9012_Copy_Paste_SWA_WS_Just_After_Installing_WorkHub().run()

    ############################################
    # App Policy - Usage restrictions - Browser preference
    from test import T033
    T033.C0000_Browser_Apps().run()
    T033.C0001_Browse_WorkMail_All_With_WorkWeb().run()
    T033.C0002_Browse_WorkMail_All_With_Unwrapped().run()
    T033.C0021_Browse_WrappedApp_All_With_WorkWeb().run()
    T033.C0022_Browse_WrappedApp_All_With_Unwrapped().run()
    T033.C0101_Browse_WorkMail_WS_With_WorkWeb().run()
    T033.C0121_Browse_WrappedApp_WS_With_WorkWeb().run()
    T033.C0201_Browse_WorkMail_WS_With_None().run()
    T033.C0221_Browse_WrappedApp_WS_With_None().run()

    ############################################
    # App Policy - NAC
    from test import T061
    T061.C0000s01_Default_WorkWeb_Symantec().run()
    T061.C0000s02_Default_WorkWeb_Yahoo().run()
    T061.C0000s03_Default_WorkWeb_Google().run()
    T061.C0000s04_Default_WorkWeb_LinkedIn().run()
    T061.C0000s05_Default_WorkWeb_Basic_Auth().run()
    T061.C0000s06_Default_WorkWeb_Digest_Auth().run()
    T061.C0000s11_Default_SWA_Symantec().run()
    T061.C0000s12_Default_SWA_Yahoo().run()
    T061.C0000s13_Default_SWA_Google().run()
    T061.C0000s14_Default_SWA_LinkedIn().run()
    T061.C0000s15_Default_SWA_Basic_Auth().run()
    T061.C0000s16_Default_SWA_Digest_Auth().run()
    T061.C0001_Block_WorkWeb_By_Whitelist().run()
    T061.C0002_Allow_WorkWeb_By_Whitelist().run()
    T061.C0011_Block_SWA_By_Whitelist().run()
    T061.C0012_Allow_SWA_By_Whitelist().run()
    T061.C0101_Block_WorkWeb_By_IP_Wildcard().run()
    T061.C0102_Allow_WorkWeb_By_IP_Wildcard().run()
    T061.C0111_Block_SWA_By_IP_Wildcard().run()
    T061.C0112_Allow_SWA_By_IP_Wildcard().run()
    T061.C0201_Block_WorkWeb_By_URL_With_Port().run()
    T061.C0202_Allow_WorkWeb_By_URL_With_Port().run()
    T061.C0211_Block_SWA_By_URL_With_Port().run()
    T061.C0212_Allow_SWA_By_URL_With_Port().run()
    T061.C0301_Block_WorkWeb_By_Port().run()
    T061.C0302_Allow_WorkWeb_By_Port_Range().run()
    T061.C0303_Block_WorkWeb_By_Wrong_Port().run()
    T061.C0311_Block_SWA_By_Port().run()
    T061.C0312_Allow_SWA_By_Port_Range().run()
    T061.C0313_Block_SWA_By_Wrong_Port().run()
    T061.C0401_Block_WorkWeb_By_Require_SSL().run()
    T061.C0402_Allow_WorkWeb_By_Require_SSL().run()
    T061.C0411_Block_SWA_By_Require_SSL().run()
    T061.C0412_Allow_SWA_By_Require_SSL().run()
    T061.C0501_Certificate_Injection_WorkWeb().run()
    T061.C0511_Certificate_Injection_SWA().run()

    ############################################
    # Device Management
    from test import T101
    T101.C0000_Enable_WorkWeb_On_Device().run()
    T101.C0001_Enable_SWA_On_Device().run()
    T101.C0002_Enable_WrappedApp_On_Device().run()
    T101.C0010_Disable_WorkWeb_On_Device().run()
    T101.C0011_Disable_SWA_On_Device().run()
    T101.C0012_Disable_WrappedApp_On_Device().run()
    T101.C0020_Wipe_WorkWeb_On_Device().run()
    T101.C0021_Wipe_SWA_On_Device().run()
    T101.C0022_Wipe_WrappedApp_On_Device().run()

    # ###########################################
    # Mobile Security
    from test import T201
    T201.C0000_Mobile_Security().run()

except Exception as e:
    exc_type, exc_value, exc_tb = sys.exc_info()
    print traceback.format_exception(exc_type, exc_value, exc_tb)

