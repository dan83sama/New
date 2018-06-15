# -*- coding: utf-8 -*-
from core.libs import *


def get_video_url(item):
    logger.trace()
    itemlist = []
    
    data = httptools.downloadpage(item.url).data
    
    if 'File was deleted' in data or 'Not Found' in data or 'File was locked by administrator' in data:
        return 'El archivo no existe o ha sido borrado'
    if 'Video is processing now' in data:
        return 'El video está procesándose en estos momentos. Inténtelo mas tarde'

    url = scrapertools.find_single_match(data, 'file: "([^"]+v.mp4)"')
    itemlist.append(Video(url=url))
    return itemlist
