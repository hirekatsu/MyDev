import argparse


def init_parser():
    parser = argparse.ArgumentParser(description='Device certification automated test')
    parser.add_argument('-s', '--serial-number', action='store', nargs='?', const=None, default=None, type=str,
                        choices=None, help='Serial number of the Android device to test.', metavar=None)
    parser.add_argument('-u', '--udid', action='store', nargs='?', const=None, default=None, type=str,
                        choices=None, help='UUID of the iOS device to test.', metavar=None)
    parser.add_argument('-c', '--config-file', action='store', nargs='?', const=None, default=None, type=str,
                        choices=None, help='Configuration file for non-default settings.', metavar=None)
    parser.add_argument('--nolog',  action='store_true', default=False,
                        help='No logs generated if this flag is set (default: False)')
    parser.add_argument('--command',  action='store', nargs='?', const=None, default=None, type=str,
                        choices=None, help='One-shot command.', metavar=None)
    parser.add_argument('--debug',  action='store_true', default=False,
                        help='Debug mode if this flag is set (default: False)')
    parser.add_argument('--device-log',  action='store_true', default=False,
                        help='Always keep device log (default: False)')
    return parser
