# -*- coding: utf-8 -*-

from core.libs import *
from lib import jsunpack


def get_video_url(item):
    logger.trace()
    itemlist = []

    referer = re.sub(r"embed-|player-", "", item.url)[:-5]

    data = httptools.downloadpage(item.url, headers={'Referer': referer}).data

    if data == "File was deleted":
        return "El archivo no existe o ha sido borrado"

    packed = scrapertools.find_single_match(data, "<script type=[\"']text/javascript[\"']>(eval.*?)</script>")
    unpacked = jsunpack.unpack(packed)

    url = scrapertools.find_single_match(unpacked, '(http[^,]+\.mp4)')
    itemlist.append(Video(url=re.compile('[0-9a-z]{40,}', re.IGNORECASE).sub(
        lambda x: x.group(0)[::-1][:3] + x.group(0)[::-1][4:],
        url
    )))

    return itemlist
