from config import settings


sites = {
    'edit': '%s/edittext' % settings.local.testweb_url,
    'text': '%s/plaintext/input.html' % settings.local.testweb_url,
    'popup': '%s/popup/popup.html' % settings.local.testweb_url,
    'basic': '%s/basic' % settings.local.testweb_url,
    'digest': '%s/digest' % settings.local.testweb_url,
    'ipaddr': 'http://%s/plaintext/input.html' % settings.local.testweb_ip_addr,
    'symantec': 'http://m.symantec.com',
    'google': 'https://www.google.com/imghp',
    'yahoo': 'http://search.yahoo.com',
    'linkedin': 'https://www.linkedin.com/uas/login'
}
