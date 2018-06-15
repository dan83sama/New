# -*- coding: utf-8 -*-

from core.libs import *

HOST = 'https://arenavision.top/'

def mainlist(item):
    logger.trace()    
    itemlist = list()

    itemlist.append(item.clone(
        label='FrozenLayer',
        action='events',
        url= HOST + 'guide',
        content_type='tvshows',
        type="item"
    ))
    
    return itemlist

def events(item):
    logger.trace()
    itemlist = []

    data = httptools.downloadpage(item.url,cookie='beget=begetok').data
    
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
