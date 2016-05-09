import os.path
from helper.imgtmpl import ImageTemplate
from helper import logger
from config import settings

_templates = {
    'ww_bookmarks_icon':
        dict(filename='ww_bookmarks_icon.png', threshold=0.8),
    'symantec_logo':
        dict(filename='symantec_logo.png', threshold=0.7),
    'google_main':
        dict(filename='google_main.png', threshold=0.7),
    'google_main2':
        dict(filename='google_main2.png', threshold=0.7),
    'yahoo_main':
        dict(filename='yahoo_main.png', threshold=0.75),
    'yahoo_main2':
        dict(filename='yahoo_main2.png', threshold=0.75),
    'yahoo_main3':
        dict(filename='yahoo_main3.png', threshold=0.7),
    'linkedin_logo_1':
        dict(filename='linkedin_logo_1.png', threshold=0.8),
    'linkedin_logo_2':
        dict(filename='linkedin_logo_2.png', threshold=0.8),
    'symc_logo':
        dict(filename='symc_logo.png', threshold=0.6),
    'administrative_block':
        dict(filename='administrative_block.png', threshold=0.6)
}


def match(template_name, image_path):
    logger.debug('screenmatch: template_name=%s, image_path=%s' % (template_name, image_path))
    if template_name not in _templates:
        logger.debug('screenmatch: invalid template name')
        return (None, None), (None, None)
    template = ImageTemplate(os.path.join(settings.local.ss_folder, _templates[template_name]['filename']))
    return template.match(image_path, _templates[template_name]['threshold'])
