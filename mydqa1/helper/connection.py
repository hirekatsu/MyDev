from config import settings
from helper import run_command
from helper import logger
import urllib
import re
import json
import time
import os.path


##################
#
#########
def workhub_packbund():
    cc = settings.server.host.split('.')
    return 'com.appcenterhq.%s.installer' % cc[0]


##################
#
#########
def check_response_head_default(res):
    match = re.search('< HTTP/1\.1 +(2\d+ +OK|100 +Continue).*', res)
    if not match:
        logger.debug('check_response_head_default: HTTP response is NOT OK/Continue')
        return False
    logger.debug('check_response_head_default: HTTP response: %s' % match.group(0))
    return True


##################
#
#########
def check_response_body_default(res):
    if not re.search('"status": *"okay"', res):
        logger.debug('check_response_body_default: status is not "okay"')
        return False
    logger.debug('check_response_body_default: success')
    return True


##################
#
#########
def call_api(param, check_response_head=check_response_head_default, check_response_body=check_response_body_default):
    p = ['-v', '--insecure', '--tlsv1', '--max-time', '300', '-X', param['method']]
    p.extend(('-H', '"X-Nukona-API-Key-v1:%s"' % settings.server.api_key))
    if 'conttype' in param:
        p.extend(('-H', '"Content-type:%s"' % param['conttype']))
    if 'form' in param:
        for item in param['form']:
            p.extend(('-F', '"%s"' % item.replace('"', '\\"')))
    if 'data' in param:
        p.extend(('-d', '"%s"' % param['data'].replace('"', '\\"')))
    url = 'https://%s%s?api_key=%s' % (settings.server.host, param['api'], urllib.quote(settings.server.api_key))
    p.append(url)
    stdout = param['download'] if 'download' in param else None
    sout, serr = run_command('curl', ' '.join(p), stdout)
    if not check_response_head(serr):
        return None
    if 'download' in param:
        sout = param['download']
    else:
        if not check_response_body(sout):
            return None
    return sout


##################
#
#########
def collect_server_info():
    # logger.debug('collect_server_info: collecting group info')
    # p = dict(api='/api1/groups',
    #          method='GET')
    # sout = call_api(p)
    # if not sout:
    #     raise Exception(__name__, 'failed to get group list from server')
    # groups = json.loads(sout)['groups']
    # settings.info['groups'] = {}
    # for group in groups:
    #     settings.info['groups'][group['name']] = group
    # if 'all' not in settings.info['groups']:
    #     raise Exception(__name__, '"all" key does not exist in group list')
    # logger.debug('collect_server_info: group "all" = %d' % settings.info['groups']['all']['id'])

    logger.debug('collect_server_info: collecting app policies')
    p = dict(api='/api1/app-policies',
             method='GET')
    sout = call_api(p)
    if not sout:
        raise Exception('Failed to get app policy list from server', __name__)
    policies = json.loads(sout)['policies']
    info_policies = settings.info.app_policies
    for policy in policies:
        pdata = policy['policy']
        pname = pdata['policy_name']
        if pname in info_policies:
            info_policies[pname]['data'] = pdata
    assure_app_policy(settings.info.default_policy)

    logger.debug('collect_server_info: collecting apps')
    p = dict(api='/api1/apps',
             method='GET')
    sout = call_api(p)
    if not sout:
        raise Exception('Failed to get app list from server', __name__)
    apps = json.loads(sout)['apps']
    info_apps = settings.info.apps
    for app in apps:
        for info_app_name in info_apps:
            if app['bundle-identifier'] == info_app_name or app['title'] == info_apps[info_app_name]['name']:
                info_apps[info_app_name]['metadata'] = get_app_metadata(app['bundle-identifier'])


##################
#
#########
def get_app_metadata(packbund):
    logger.debug('get_app_metadata: packbund=%s' % packbund)
    p = dict(api='/api1/apps/%s/metadata' % packbund,
             method='GET')
    sout = call_api(p)
    if not sout:
        logger.debug('get_app_metadata: failed to get app metadata')
        return None
    return json.loads(sout)['metadata']


##################
#
#########
def assure_app_policy(name):
    logger.debug('assure_app_policy: name=%s' % name)
    if name not in settings.info.app_policies:
        logger.debug('assure_app_policy: policy "%s" is not defined' % name)
        return False
    policies = settings.info.app_policies
    if policies[name]['data'] is None:
        logger.debug('assure_app_policy: NO policy "%s" on server - adding...' % name)
        p = dict(api='/api1/app-policies/add',
                 method='POST',
                 data='policy=' + urllib.quote(json.dumps(policies[name]['param'])))
        sout = call_api(p)
        if not sout:
            logger.debug('assure_app_policy: failed to add a new policy')
            return False
        policies[name]['data'] = json.loads(sout)['policy']
        set_loose_admin_password_policy()
    else:
        logger.debug('assure_app_policy: policy "%s" already exists - checking fields...' % name)
        pparam = policies[name]['param']
        pdata = dict(policies[name]['data'])
        pchange = False
        for fname in pparam:
            if fname in pdata and pparam[fname] != pdata[fname]:
                logger.debug('assure_app_policy: field=%s, old value=%s, new value=%s'
                             % (fname, str(pdata[fname]), str(pparam[fname])))
                pdata[fname] = pparam[fname]
                pchange = True
        if pchange:
            logger.debug('assure_app_policy: one or more fields do not match - changing...')
            p = dict(api='/api1/app-policies/%d' % pdata['id'],
                     method='POST',
                     data='policy=' + urllib.quote(json.dumps(pdata)))
            sout = call_api(p)
            if not sout:
                logger.debug('assure_app_policy: failed to update a policy "%s"' % name)
                return False
            policies[name]['data'] = pdata
            set_loose_admin_password_policy()
    return True


##################
#
#########
def set_loose_admin_password_policy():
    call_api(dict(api='/api1/settings/admin_password_policy',
                  method='POST',
                  data='&'.join(('max_pass_lifetime_enabled=false',
                                 'pass_history_depth_enabled=false',
                                 'prohibit_username_email=false',
                                 'require_uppercase=false',
                                 'require_lowercase=false',
                                 'require_numbers=false',
                                 'require_non_alpha=false',
                                 'first_three_unique=false'))))


##################
#
#########
def assure_app(name, policy='xTA - default'):
    def check_response_body1(res):
        return re.search('"status": *"(okay|ok)"', res) is not None

    def check_response_body_upload(res):
        if not check_response_body_default(res):
            if not re.search('"code": *254', res):
                logger.debug('check_response_body_upload: status code is NOT OK')
                return False
            logger.debug('check_response_body_upload: code is 254 = identical version already exists')
        return True

    logger.debug('assure_app: name=%s, policy=%s' % (name, str(policy)))
    if name not in settings.info.apps:
        logger.debug('assure_app: invalid app name')
        return False

    if policy:
        if not assure_app_policy(policy):
            return False
        pid = settings.info.app_policies[policy]['data']['id']
    else:
        pid = 0

    appdata = settings.info.apps[name]
    appdata['policy_changed'] = False
    if appdata['metadata'] is None:
        if appdata['type'] == 'sealed':
            logger.debug('assure_app: adding sealed app: %s' % name)
            p = dict(api='/api1/apps/sealedapps/add',
                     method='POST',
                     data='bundle-identifier=%s&platform=android' % name)
            sout = call_api(p, check_response_body=check_response_body1)
            if not sout:
                logger.debug('assure_app: failed to add sealed app')
                return False
            appid = name
        elif appdata['type'] == 'swa':
            from apps.website import sites as website
            logger.debug('assure_app: adding secure web app: %s' % name)
            if not re.match('^swa:', name):
                logger.debug('assure_app: invalid secure web app name')
                return False
            url = website[name[4:]]
            app_pid = pid if pid != 0 else settings.info.app_policies[settings.info.default_policy]['data']['id']
            metadata = dict(title=appdata['name'],
                            subtitle=url,
                            description='Secure Web App',
                            policy=app_pid,
                            android_keypair_create_new=True,
                            pointer='production',
                            entitlements=[{'groups': ['all'],
                                           'priority': 1}])
            p = dict(api='/api1/apps/create-webapp',
                     method='POST',
                     data='app_url=%s&platform=android&app_type=NATIVE_WEBAPP&metadata=%s' %
                          (url, urllib.quote(json.dumps(metadata))))
            sout = call_api(p)
            if not sout:
                logger.debug('assure_app: failed to add secure web app')
                return False
            appid = json.loads(sout)['app-uuid']
            if not wait_app_wrapping(uuid=appid):
                return False
            appdata['policy_changed'] = True
        elif appdata['type'] == 'native':
            logger.debug('assure_app: adding native app: %s' % name)
            if name not in settings.local.apk_files:
                logger.debug('assure_app: native app apk file is not defined')
                return False
            apk_file = os.path.join(settings.local.apk_folder, settings.local.apk_files[name])
            logger.debug('assure_app: native apk file path: %s' % apk_file)
            p = dict(api='/api1/apps/upload',
                     method='POST',
                     form=['bundle=@%s' % apk_file])
            sout = call_api(p,
                            check_response_body=check_response_body_upload)
            if not sout:
                logger.debug('assure_app: failed to upload apk file')
                return False
            logger.debug('assure_app: apk file uploaded')
            jout = json.loads(sout)
            if 'code' in jout and jout['code'] == 254:
                logger.debug('assure_app: %s' % jout['message'])

            else:
                vuuid = jout['version-uuid']
                p = dict(api='/api1/apps/%s/publish' % name,
                         method='POST',
                         data='version=%s&pointer=production' % vuuid)
                sout = call_api(p)
                if not sout:
                    logger.debug('assure_app: failed to publish app')
                    return False
                logger.debug('assure_app: app published successfully')
                app_pid = pid if pid != 0 else settings.info.app_policies[settings.info.default_policy]['data']['id']
                metadata = dict(title=appdata['name'],
                                subtitle=name,
                                description='Native App',
                                policy=app_pid,
                                android_keypair_create_new=True,
                                pointer='production',
                                entitlements=[dict(
                                    groups=['all'],
                                    priority=1)])
                p = dict(api='/api1/apps/%s/metadata' % name,
                         method='POST',
                         data='metadata=' + urllib.quote(json.dumps(metadata)))
                sout = call_api(p)
                if not sout:
                    logger.debug('assure_app: failed to update metadata')
                    return False
                if not wait_app_wrapping(packbund=name):
                    return False
            appid = name
            appdata['policy_changed'] = True
        else:
            logger.debug('assure_app: invalid app type "%s"' % appdata['type'])
            return False

        logger.debug('assure_app: retrieving app metadata for %s' % appid)
        appdata['metadata'] = get_app_metadata(appid)
        if appdata['metadata'] is None:
            return False

    if policy:
        logger.debug('assure_app: current policy id=%s' % str(appdata['metadata']['policy']))
        logger.debug('assure_app: policy id to set=%d' % pid)
        if appdata['metadata']['policy'] != pid:
            logger.debug('assure_app: applying specified policy')

            if appdata['metadata']['policy']:
                logger.debug('assure_app: checking previous policy')
                p = dict(api='/api1/app-policies/%d' % appdata['metadata']['policy'],
                         method='GET')
                sout = call_api(p)
                if sout:
                    policy_old = json.loads(sout)['policy']
                    policy_new = settings.info.app_policies[policy]['data']
                    if policy_old['encryption_required'] != policy_new['encryption_required']:
                        appdata['policy_changed'] = True
                    if policy_old['allow_sdcard_storage'] == True and policy_new['allow_sdcard_storage'] == False:
                        appdata['policy_changed'] = True
                else:
                    appdata['policy_changed'] = True
            else:
                appdata['policy_changed'] = True

            metadata = dict(policy=pid,
                            android_keypair_create_new=True)
            p = dict(api='/api1/apps/%s/metadata' % appdata['metadata']['bundle-identifier'],
                     method='POST',
                     data='metadata=' + urllib.quote(json.dumps(metadata)))
            sout = call_api(p)
            if not sout:
                logger.debug('assure_app: failed to apply app policy')
                return False
            logger.debug('assure_app: policy id "%d" is applied' % pid)
            appdata['metadata']['policy'] = pid
            if not wait_app_wrapping(name):
                return False
        else:
            logger.debug('assure_app: policy id "%d" is already applied' % pid)
    else:
        logger.debug('assure_app: no policy is specified')
    return True


##################
#
#########
def wait_app_wrapping(name=None, packbund=None, uuid=None):
    logger.debug('wait_app_wrapping: name=%s, packbund=%s, uuid=%s' % (name, packbund, uuid))
    if name is not None:
        if name not in settings.info.apps or settings.info.apps[name]['metadata'] is None:
            logger.debug('wait_app_wrapping: invalid app name')
            return False
        aid = settings.info.apps[name]['metadata']['bundle-identifier']
    elif packbund is not None:
        aid = packbund
    elif uuid is not None:
        aid = uuid
    else:
        logger.debug('wait_app_wrapping: parameter is invalid')
        return False
    elapsed = 0
    while elapsed < 600:
        logger.debug('wait_app_wrapping: elapsed=%d' % elapsed)
        p = dict(api='/api1/apps/%s/wrapstatus' % aid,
                 method='GET')
        sout = call_api(p)
        if sout:
            if not json.loads(sout)['wrapping']:
                logger.debug('wait_app_wrapping: wrapping finished')
                return True
        time.sleep(10)
        elapsed += 10
    logger.debug('wait_app_wrapping: timeout')
    return False


##################
#
#########
def rebuild_workhub():
    def check_response_body_none(res):
        return True
    call_api(dict(api='/api1/settings/workhub/buildAndroid', method='POST'),
             check_response_body=check_response_body_none)


##################
#
#########
def rewrap_app(name=None, packbund=None, uuid=None):
    logger.debug('rewrap_app: name=%s, packbund=%s, uuid=%s' % (name, packbund, uuid))
    if name is not None:
        if name not in settings.info.apps or settings.info.apps[name]['metadata'] is None:
            logger.debug('rewrap_app: invalid app name')
            return False
        aid = settings.info.apps[name]['metadata']['bundle-identifier']
    elif packbund is not None:
        aid = packbund
    elif uuid is not None:
        aid = uuid
    else:
        logger.debug('rewrap_app: parameter is invalid')
        return False
    sout = call_api(dict(api='/api1/apps/%s/rewrap' % aid, method='POST'))
    if not sout:
        logger.debug('rewrap_app: failed to re-wrap app')
        return False
    return True


##################
#
#########
def download_workhub(platform, dist_file):
    logger.debug('download_workhub: platform=%s, dist_file=%s' % (platform, dist_file))
    p = dict(api='/api1/download/workhub/%s' % platform,
             method='GET',
             download=dist_file)
    if not call_api(p):
        logger.debug('download_workhub: failed to download')
        return False
    logger.debug('download_workhub: workhub downloaded successfully')
    return True


##################
#
#########
def download_nms(apk_file):
    logger.debug('download_nms: apk_file=%s' % apk_file)
    p = dict(api='/api1/nms/downloads/multiuse.apk',
             method='GET',
             download=apk_file)
    if not call_api(p):
        logger.debug('download_nms: failed to download')
        return False
    logger.debug('download_nms: multi-use nms downloaded successfully')
    return True


##################
#
#########
def download_app(name, apk_file):
    logger.debug('download_app: name=%s, apk_file=%s' % (name, apk_file))
    appinfo = settings.info.apps[name]
    if appinfo['type'] == 'sealed':
        logger.debug('download_app: app is sealed')
        appinfo['file'] = os.path.join(settings.local.apk_folder, settings.local.apk_files[name])
    else:
        packbund = appinfo['metadata']['bundle-identifier']
        if 'production-info' not in appinfo['metadata']:
            logger.debug('download_app: app is not published')
            return None
        vuuid = appinfo['metadata']['production-info']['version-uuid']
        logger.debug('download_app: packbund=%s, version-uuid=%s' % (packbund, vuuid))
        p = dict(api='/api1/apps/%s/%s/bundle' % (packbund, vuuid),
                 method='GET',
                 download=apk_file)
        if not call_api(p):
            logger.debug('download_app: failed to download')
            return None
        logger.debug('download_app: app downloaded successfully')
        appinfo['file'] = apk_file
    return appinfo['file']


##################
#
#########
def get_device_id(serial):
    def check_response_body_none(res):
        return True
    logger.debug('get_device_id: serial=%s' % serial)
    sout = call_api(dict(api='/api1/report/devices',
                         method='GET'),
                    check_response_body=check_response_body_none)
    if sout:
        devices = json.loads(sout)
        for device in devices:
            if 'serial_number' in device and device['serial_number'] == serial:
                return device['device_identifier']
    return None


##################
#
#########
def get_device_info_by_mac(mac):
    logger.debug('get_device_info_by_mac: mac=%s' % mac)
    p = dict(api='/api1/devices/by-mac/%s' % mac,
             method='GET')
    sout = call_api(p)
    if not sout:
        return None
    return json.loads(sout)['device-info']


##################
#
#########
def disassociate_device_by_serial(serial):
    logger.debug('disassociate_device_by_serial: serial=%s' % serial)
    device_id = get_device_id(serial)
    if not device_id:
        return None
    p = dict(api='/api1/devices/%s/dissociate' % device_id,
             method='POST')
    sout = call_api(p)
    if not sout:
        return None
    return json.loads(sout)['status']


##################
#
#########
def set_app_on_device(device_id, packbund, action):
    logger.debug('set_app_on_device_by_mac: device_id=%s, packbund=%s, action=%s' % (device_id, packbund, action))
    if action not in ('enable', 'disable', 'wipe'):
        return False
    p = dict(api='/api1/devices/%s/apps/%s/%s' % (device_id, packbund, action),
             method='POST')
    sout = call_api(p)
    if not sout:
        return False
    return True
