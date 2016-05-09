# -*- coding: utf-8 -*-
from datetime import datetime
import os
import os.path
import codecs

_log_file = None
_debug_file = None
_debug_print = False


def set_file(log_file, debug_file, debug_print):
    global _log_file, _debug_file, _debug_print
    try:
        if log_file:
            if not os.path.isdir(os.path.dirname(log_file)):
                os.makedirs(os.path.dirname(log_file))
            with open(log_file, 'w') as fo:
                fo.write('')
        _log_file = log_file
        if debug_file:
            if not os.path.isdir(os.path.dirname(debug_file)):
                os.makedirs(os.path.dirname(debug_file))
            with open(debug_file, 'w') as fo:
                fo.write('')
        _debug_file = debug_file
    except Exception as e:
        print 'Logger error: %s' % e
    _debug_print = debug_print


def writefile(dest, text):
    # with codecs.open(dest, 'a', 'utf-8') as fo:
    with open(dest, 'a') as fo:
        fo.write(text)
        fo.write('\n')


def debug(text):
    global _debug_file, _debug_print
    text = '[%s] %s' % (datetime.today().strftime('%H:%M:%S.%f'), text)
    if _debug_file:
        writefile(_debug_file, text)
        if _debug_print:
            print text
    else:
        print text


def info(text):
    global _log_file
    if _log_file:
        writefile(_log_file, text)
    print text
    debug(text)



