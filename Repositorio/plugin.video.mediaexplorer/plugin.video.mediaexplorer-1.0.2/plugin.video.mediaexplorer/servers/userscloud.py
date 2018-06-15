# -*- coding: utf-8 -*-
from core.libs import *


def get_video_url(item):
    logger.trace()
    itemlist = list()
    data = httptools.downloadpage(item.url).data

    if not data or \
            "Not Found" in data or \
            "File was deleted" in data or \
            "The file you are trying to download is no longer available" in data:

        return "El fichero no existe o ha sido borrado"

    # TODO: Por implimentar (no he encontrado ningun enlace funcionando)

    return itemlist
