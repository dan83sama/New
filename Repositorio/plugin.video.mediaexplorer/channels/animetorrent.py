# -*- coding: utf-8 -*-

#ver newest
#cambiar tv_search a anime_search???,tvshows a animeshows??
#ver library
#repriducir desde biblioteca falla mediaexplorer??

from core.libs import *

HOST = 'https://www.frozen-layer.com'

def mainlist(item):
    logger.trace()    
    itemlist = list()

    itemlist.append(item.clone(
        label='FrozenLayer',
        action='newest_episodes',
        url= HOST + '/descargas/detallada/bittorrent/anime',
        content_type='tvshows',
        type="item"
    ))

    itemlist.append(item.clone(
        label='Buscar',
        action='tv_search',
        content_type='tvshows',
        query=True,
        type='search'
    ))

    return itemlist

def tv_search(item):
    logger.trace()
    item.url = HOST + '/buscar/descargas/anime?sort=titulo&direction=asc&busqueda=%s' % item.query

    return seasons(item)

def seasons(item):
    logger.trace()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    patron = 'jtf.*?title=\'(.*?)\'.*?<td class=\'tit\'>.*?<a href="([^"]+)" class="detalles_link">([^"]+)</a>.*?<td>.*?(\d+) Mb'
    
    for fansub, url, title, size in scrapertools.find_multiple_matches(data, patron):
        #scraper titulo
        subtitle = scrapertools.find_single_match(title,"(.*?) Episodio \d+")
        subtitle = re.sub(r"\n|TV|\(|\)|-", "", subtitle)
        #-------------
        size = "[B]["+size+"MB"+"][/B]"
        title = size+fansub+title
        #para que no salga en el listado de capitulos//findvideos
        if item.extra:
            extra="extra"
        
        new_item = item.clone(title=subtitle, label=title, url=url, type='tvshow', content_type="servers", action="findvideos")
        itemlist.append(new_item)

    # Paginador
    next_url = scrapertools.find_single_match(data, '<span class=\'next\'>.*?<a href="(.*?)"')
    if next_url:
        next_url = HOST + next_url
        itemlist.append(item.clone(
            action="seasons",
            url=next_url,
            type='next'
        ))

    return itemlist

def newest_episodes(item):
    logger.trace()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;|</p>|<p>|&amp;|amp;","",data)

    patron = "<h1 class='descarga_titulo'>(.*?)<a href=\"(.*?)\">(.*?)</a>.*?"
    patron += "<div class='twocol'><a href='(.*?)'.*?Tamaño:.*?>(.*?)<"

    for fansub, url, titulo, poster, size in scrapertools.find_multiple_matches(data, patron):
        size = "[B]["+size+"][/B]"
        title = size+fansub+titulo
        #scraper titulo
        subtitle = scrapertools.find_single_match(titulo,"(.*?) Episodio \d+")
        subtitle = re.sub(r"\n|TV|\(|\)|-", "", subtitle)
        #-------------
        
        new_item = item.clone(title=subtitle, label=title, url=url, type="video", content_type="servers", poster=poster, action="findvideos")
        itemlist.append(new_item)
            
                
    # Paginador
    next_url = scrapertools.find_single_match(data, '<span class=\'next\'>.*?<a href="(.*?)"')
    if next_url:
        next_url = HOST + next_url
        itemlist.append(item.clone(
            action=item.action,
            url=next_url,
            type='next'
        ))
      
    return itemlist

def findvideos(item):
    logger.trace()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    patron = 'Seeds:.*?"stats.*?">(\d+)<.*?Peers:.*?"stats.*?">(\d+)<.*?descargar_torrent.*?href=\'(.*?)\'.*?<span class=\'mas_desc\'>.*?<a href=\'(.*?)\''
    
    for seeds, peers, url, urlserie in scrapertools.find_multiple_matches(data, patron):
        
        seeds = " Enlace Torrent [[COLOR red]Seeds: "+seeds+"[/COLOR]"+ " "
        peers = "[COLOR yellow]Peers: "+peers+"[/COLOR]]"
        label = seeds + peers
        urlserie = HOST + urlserie
        
        itemlist.append(item.clone(
            label=label,
            action="play",
            url=url,
            type="item",
            thumb=item.poster,
            server='torrent'
        ))

        #para que no salga en el listado de capitulos
        if not item.extra:

            itemlist.append(item.clone(
                label="Ir a la serie",
                action='seasons',
                type="tvshow",
                content_type='episodes',
                url=urlserie,
                thumb="",
                extra="extra"
            ))
        
    return itemlist
