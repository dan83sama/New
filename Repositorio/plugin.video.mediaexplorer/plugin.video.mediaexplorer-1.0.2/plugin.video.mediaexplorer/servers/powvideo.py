# -*- coding: utf-8 -*-

import base64

from core.libs import *
from lib import jsunpack


def get_video_url(item):
    logger.trace()
    itemlist = []

    referer = item.url.replace('iframe', 'preview')
    data = httptools.downloadpage(item.url, headers={'referer': referer}).data

    if data == "File was deleted"  in data:
        return "El archivo no existe o ha sido borrado"

    if 'Video is processing now' in data:
        return "El vídeo está siendo procesado, intentalo de nuevo mas tarde"

    packed = scrapertools.find_single_match(data, "<script type=[\"']text/javascript[\"']>(eval.*?)</script>")

    """if not packed:
        form = scrapertools.find_single_match(data, '<form method="POST" action=\'\' id="d0Form">(.*?)</form>')
        post = {}
        if form:
            for name, value in scrapertools.find_multiple_matches(form, 'name="([^"]+)" value="([^"]+)"'):
                post[name] = value

            data = httptools.downloadpage(item.url, post=post).data
            packed = scrapertools.find_single_match(data, "<script type=[\"']text/javascript[\"']>(eval.*?)</script>")"""

    unpacked = jsunpack.unpack(packed)
    url = scrapertools.find_single_match(unpacked, "(?:src):\\\\'([^\\\\]+.mp4)\\\\'")
    itemlist.append(Video(url=re.compile('[0-9a-z]{40,}', re.IGNORECASE).sub(lambda x: x.group(0)[::-1][1:], url)))

    return itemlist
