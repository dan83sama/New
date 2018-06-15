# -*- coding: utf-8 -*-

import unicodedata

from core.libs import *

QLT = Qualities({
    Qualities.rip: ['HD Rip', 'HD RIP'],
    Qualities.hd_full: ['1080p'],
    Qualities.hd: ['720p'],
    Qualities.m3d: ['3D'],
})


def mainlist(item):
    logger.trace()

    itemlist = list()

    itemlist.append(item.clone(
        label='Novedades',
        action='movies',
        url='http://alltorrent.net/',
        content_type='movies',
        type="item"
    ))

    itemlist.append(item.clone(
        label='Géneros',
        action='menu_category',
        url='http://alltorrent.net/',
        content_type='items',
        type="item"
    ))

    itemlist.append(item.clone(
        label='Calidades',
        action='menu_quality',
        url='http://alltorrent.net/',
        content_type='items',
        type="item"
    ))

    itemlist.append(item.clone(
        label='Años',
        action='menu_year',
        url='http://alltorrent.net/',
        content_type='items',
        type="item"
    ))

    itemlist.append(item.clone(
        label='Rating IMDb',
        action='menu_imbd',
        url='http://alltorrent.net/',
        content_type='items',
        type="item"
    ))

    itemlist.append(item.clone(
        label='Buscar',
        action='movie_search',
        content_type='movies',
        query=True,
        type='search'
    ))
    return itemlist


def movie_search(item):
    logger.trace()
    item.url = 'http://alltorrent.net/?s=%s' % item.query
    return movies(item)


def menu_category(item):
    logger.trace()
    itemlist = list()

    data = httptools.downloadpage(item.url).data

    data = scrapertools.find_single_match(data,
                                          "<select  name='ofcategory' id='ofcategory' class='postform' >(.*?)</select>")

    patron = '<option class="level-0" value="[^"]+">(?P<label>[^<]+)</option>'

    for result in re.compile(patron, re.DOTALL).finditer(data):
        itemlist.append(item.clone(
            label=result.group('label'),
            action='movies',
            type='item',
            url='http://alltorrent.net/category/%s/' % ''.join(
                (c for c in unicodedata.normalize('NFD', unicode(result.group('label'), 'utf8')) if
                 unicodedata.category(c) != 'Mn')),
            content_type='movies'
        ))

    return itemlist


def menu_quality(item):
    logger.trace()
    itemlist = list()

    data = httptools.downloadpage(item.url).data

    data = scrapertools.find_single_match(data,
                                          "<select  name='ofrezolucia' id='ofrezolucia' "
                                          "class='postform' >(.*?)</select>")

    patron = '<option class="level-0" value="[^"]+">(?P<label>[^<]+)</option>'

    for result in re.compile(patron, re.DOTALL).finditer(data):
        itemlist.append(item.clone(
            label=result.group('label'),
            action='movies',
            type='item',
            url='http://alltorrent.net/rezolucia/%s/' % result.group('label'),
            content_type='movies'
        ))

    return itemlist


def menu_year(item):
    logger.trace()
    itemlist = list()

    data = httptools.downloadpage(item.url).data

    data = scrapertools.find_single_match(data, "<select  name='ofweli' id='ofweli' class='postform' >(.*?)</select>")

    patron = '<option class="level-0" value="[^"]+">(?P<label>[^<]+)</option>'

    for result in re.compile(patron, re.DOTALL).finditer(data):
        itemlist.append(item.clone(
            label=result.group('label'),
            action='movies',
            type='item',
            url='http://alltorrent.net/weli/%s/' % result.group('label'),
            content_type='movies'
        ))

    return itemlist


def menu_imbd(item):
    logger.trace()
    itemlist = list()

    data = httptools.downloadpage(item.url).data

    data = scrapertools.find_single_match(data, "<select  name='ofimdb' id='ofimdb' class='postform' >(.*?)</select>")

    patron = '<option class="level-0" value="[^"]+">(?P<label>[^<]+)</option>'

    for result in re.compile(patron, re.DOTALL).finditer(data):
        itemlist.append(item.clone(
            label=result.group('label'),
            action='movies',
            type='item',
            url='http://alltorrent.net/imdb/%s/' % result.group('label')[0],
            content_type='movies'
        ))

    return itemlist


def movies(item):
    logger.trace()
    itemlist = list()

    data = httptools.downloadpage(item.url).data

    data = scrapertools.find_single_match(data, '<div class="container">[^<]+<h2>\s?</h2>(.*?)<footer>')

    patron = '<a href="(?P<url>[^"]+)" class="browse-movie-link">.*?' \
             'src="(?P<thumb>[^"]+)".*?movie-title"> (?P<title>[^<]+).*?' \
             'rel="tag">(?P<year>[\d]+)'

    for result in re.compile(patron, re.DOTALL).finditer(data):
        itemlist.append(item.clone(
            title=result.group('title'),
            action='findvideos',
            poster=result.group('thumb'),
            url=result.group('url'),
            year=result.group('year'),
            type='movie',
            content_type='servers'
        ))

    # Paginador
    next_url = scrapertools.find_single_match(data, '<a href="([^"]+)" rel="nofollow">Next Page &raquo;</a></li>')
    if next_url:
        itemlist.append(item.clone(
            action='movies',
            url=next_url,
            type='next'
        ))

    return itemlist


def findvideos(item):
    logger.trace()
    itemlist = list()

    data = httptools.downloadpage(item.url).data

    online = scrapertools.find_single_match(data,
                                            '<a class="youtube cboxElement button-green-download-big" href="([^"]+)">'
                                            '<span class="icon-play"></span> Online </a></a>')
    if online:
        itemlist.append(item.clone(
            url=online,
            action='play',
            type='server'
        ))
        itemlist = servertools.get_servers_itemlist(itemlist)

    patron = '<div class="modal-torrent">[^<]+' \
             '<div class="modal-quality" id="[^"]+"><span>(?P<quality>[^<]+)</span></div>[^<]+' \
             '<p>Tamaño de archivo</p>[^<]+' \
             '<p class="quality-size">(?P<size>[\d.]+) GB</p>[^<]+' \
             '<a download="" class="download-torrent button-green-download-big" href="(?P<url>[^"]+)" rel="nofollow" ' \
             'title="[^"]+"><span class="icon-in"></span>Descargar</a>[^<]+' \
             '</div>'
    for result in re.compile(patron, re.DOTALL).finditer(data):
        itemlist.append(item.clone(
            url=result.group('url'),
            action='play',
            type='server',
            server='torrent',
            quality=QLT.get(result.group('quality')),
            size=float(result.group('size')) * 1024 * 1024
        ))

    itemlist = servertools.get_servers_from_id(itemlist)
    return itemlist
