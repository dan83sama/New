# -*- coding: utf-8 -*-
from core.libs import *

LNG = Languages({
    Languages.es: ['español'],
    Languages.en: ['ingles'],
    Languages.la: ['latino'],
    Languages.vos: ['sub']
})

QLT = Qualities({
    Qualities.hd_full: ['1080'],
    Qualities.hd: ['720', 'hdtv'],
    Qualities.rip: ['rip'],
    Qualities.scr: ['screener', 'cam']
})


def findvideos(item):
    logger.trace()
    itemlist = []

    servers = 'vidlox.tv,streamango.com,openload.co,oload.tv,ok.ru,gamovideo.com,vidoza.net,rapidvideo.com'
    url = "http://www.olimpo.link/?server=%s" % urllib.quote_plus(servers)

    if item.mediatype == 'movie':
        q = item.title
        url += '&order=recent&category=1'
    elif item.mediatype:
        q = item.tvshowtitle
        url += '&order=series&category=2'
        if item.season and item.episode:
            url += '&season=%s&episode=%s' % (item.season, item.episode)
    else:
        return

    if item.tmdb_id:
        url += '&tmdb=%s' % item.tmdb_id

    if item.year:
        q += ' (%s)' % item.year

    url += '&q=%s' % urllib.quote_plus(q)

    itemlist = find_more_videos(item.clone(url=url, stream=True))

    # Filtrar por idioma
    if item.lang:
        MAX_PAG = 3  # Numero maximo de paginas en los resultados de olimpo.link donde filtrar
        SERVERS_MIN = 20 # Dejar de buscar en las paginas siguientes si ya hay como minimo este numero de servidores
        n_page = 1

        logger.debug('sin filtrar en pagina %s: %s' %(n_page, len(itemlist)))
        new_itemlist = filter(lambda x: x.lang in item.lang or x.action == 'find_more_videos', itemlist)
        logger.debug('filtrados %s' %len(new_itemlist))
        itemlist = new_itemlist[:]

        while new_itemlist and new_itemlist[-1].action == 'find_more_videos' and n_page < MAX_PAG and len(itemlist) < SERVERS_MIN:
            n_page += 1
            url = itemlist.pop().url
            new_itemlist = find_more_videos(item.clone(url=url, stream=True))
            logger.debug('sin filtrar en pagina %s: %s' % (n_page, len(new_itemlist)))

            new_itemlist = filter(lambda x: x.lang in item.lang or x.action == 'find_more_videos', new_itemlist)
            logger.debug('filtrados %s' % len(new_itemlist))

            itemlist.extend(new_itemlist)
            logger.debug('acumulados: %s' % len(itemlist))

        if itemlist and itemlist[-1].action == 'find_more_videos':
            itemlist.pop()


    logger.debug('totales: %s' % len(itemlist))
    return itemlist


def find_more_videos(item):
    logger.trace()
    #logger.debug(item.url)
    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)

    patron = '<img src="http://www.google.com/s2/favicons\?domain=([^.]+).*?'
    patron += '<a class="text-overflow" target="_blank" href="([^"]+)">'
    patron += '([^<]+)</a>'

    for server, url, title in scrapertools.find_multiple_matches(data, patron):
        title = title.replace('[', '{').replace(']', '}').lower()
        patron = '\(\d{4}\).*?{([^}]+)}.*?{([^}]+)}'

        info = scrapertools.find_single_match(title, patron)  # lang, quality
        if info:
            lng = info[0]
            if 'sub' in lng: lng = 'sub'

            qlt = info[1]
            if 'screener' in qlt or 'ts' in qlt or 'cam' in qlt:
                qlt = 'screener'
            elif 'rip' in qlt:
                qlt = 'rip'
            elif '1080' in qlt:
                qlt = '1080'
            elif '720' in qlt:
                qlt = '720'

            itemlist.append(item.clone(
                action='play',
                type='server',
                url=url,
                server=server,
                lang=LNG.get(lng),
                quality=QLT.get(qlt)
            ))

    itemlist = servertools.get_servers_from_id(itemlist)

    # Paginador
    next_url = scrapertools.find_single_match(data, '(?s)<a href="([^"]+)">»</a>')
    if next_url and '&page=0' not in next_url:
        itemlist.append(item.clone(
            label='Ver mas enlaces online',
            action='find_more_videos',
            url=urlparse.urljoin(item.url, next_url),
            type='highlight'))

    return itemlist


def play(item):
    logger.trace()

    data = httptools.downloadpage(item.url).data
    url = 'http://olimpo.link' + scrapertools.find_single_match(data, '<iframe src="([^"]+)')
    item.url = httptools.downloadpage(url + "&ge=1", follow_redirects=False, only_headers=True).headers.get("location",
                                                                                                            "")
    return item
