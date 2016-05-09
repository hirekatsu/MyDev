from config import settings
from helper import logger
import subprocess
import re


def run_command(cmd, args, stdout=None):
    if cmd in settings.command:
        cmd = settings.command[cmd]
    cmd = '"%s"' % cmd
    cmdtxt = ' '.join([cmd, args])
    logger.debug('run_command: command: %s' % cmdtxt)
    f = None
    try:
        if not stdout:
            soutdest = subprocess.PIPE
        else:
            f = open(stdout, 'w')
            soutdest = f
        p = subprocess.Popen(cmdtxt, shell=True, stdout=soutdest, stderr=subprocess.PIPE)
        sout, serr = p.communicate()
        if sout:
            sout = re.sub('\r+', '', sout)
        if serr:
            serr = re.sub('\r+', '', serr)
        logger.debug('run_command: stdout')
        logger.debug(sout)
        logger.debug('run_command: stderr')
        logger.debug(serr)
    except Exception as e:
        logger.debug('run_command: ERROR: exception: \n%s\ntype:%s\nargs:%s\nmessage:%s' % (str(e), type(e), e.args, e.message))
        sout = ''
        serr = ''
    if f:
        f.close()
    return sout, serr
