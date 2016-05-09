import codecs
import os.path


class SettingsContainer(object):
    def absorb(self, setting):
        for key, val in setting.iteritems():
            setattr(self, key, val)

    def __repr__(self):
        # l = []
        # for k in dir(self):
        #     if not k.startswith('__'):
        #         l.append('%s: %s' % (k, str(getattr(self, k))))
        # return '\n'.join(l)
        return str(dir(self))


server = SettingsContainer()
device = SettingsContainer()
local = SettingsContainer()
command = {}
info = SettingsContainer()


def take(s):
    global server, local, command, info
    if 'server' in s:
        server.absorb(s['server'])
    if 'device' in s:
        device.absorb(s['device'])
    if 'local' in s:
        local.absorb(s['local'])
    if 'command' in s:
        command.update(s['command'])
    if 'info' in s:
        info.absorb(s['info'])

    # app policy initialization
    policies = info.app_policies
    default_param = policies['xTA - default']['param']
    for pname in policies:
        if not pname == 'xTA - default':
            pdata = dict(default_param)
            pdata.update(policies[pname]['param'])
            policies[pname]['param'] = pdata


def import_from(filepath):
    with codecs.open(filepath, encoding='utf-8') as fo:
        take(eval(fo.read()))


def tempfile(basename):
    global local
    return os.path.join(local.out_path, basename)
