# -*- coding: utf-8 -*-

#poner menus de cine y series
#ver menus, amarillo la calidad
#codificar pagina para resultados para ñ

from core.libs import *

HOST = 'http://descargas2020.com'

def mainlist(item):
    logger.trace()
    itemlist = list()

    itemlist.append(item.clone(
        action="newest_movies",
        label="Peliculas",
        url=HOST+'/peliculas/',
        type="item",
        group=True,
        content_type='movies'
    ))

    itemlist.append(item.clone(
        action="newest_movies",
        label="Peliculas HD",
        url=HOST + '/peliculas-hd/',
        type="item",
        group=True,
        content_type='movies'
    ))
        
    itemlist.append(item.clone(
        action="newest_movies",
        label="Otras Peliculas",
        url=HOST+'/otras-peliculas/',
        type="item",
        group=True,
        content_type='movies'
    ))

    itemlist.append(item.clone(
        action="newest_movies",
        label="Estrenos Cine",
        url=HOST+'/estrenos-de-cine/',
        type="item",
        group=True,
        content_type='movies'
    ))

    itemlist.append(item.clone(
        action="newest_movies",
        label="Peliculas x264 MKV",
        url=HOST+'/peliculas-x264-mkv/',
        type="item",
        group=True,
        content_type='movies'
    ))

    itemlist.append(item.clone(
        action="newest_movies",
        label="Peliculas Subtituladas",
        url=HOST+'/peliculas-vo/',
        type="item",
        group=True,
        content_type='movies'
    ))
    
    itemlist.append(item.clone(
        action="newest_series",
        label="Series",
        url=HOST+'/series/',
        type="item",
        group=True,
        content_type='tvshows'
    ))

    itemlist.append(item.clone(
        action="newest_series",
        label="Series HD",
        url=HOST + '/series-hd/',
        type="item",
        group=True,
        content_type='tvshows'
    ))

    itemlist.append(item.clone(
        action="newest_series",
        label="Series Subtituladas",
        url=HOST + '/series-vo/',
        type="item",
        group=True,
        content_type='tvshows'
    ))
    
    itemlist.append(item.clone(
        label='Buscar',
        action='busqueda',
    ))

    return itemlist

def busqueda(item):
    logger.trace()
    itemlist = list()

    itemlist.append(item.clone(
        label='Buscar Peliculas',
        action='movie_search',
        content_type='movies',
        url=HOST+'/index.php?page=buscar&q=%s',
        query=True,
        type='search'
    ))

    itemlist.append(item.clone(
        label='Buscar Series',
        action='tv_search',
        content_type='tvshows',
        query=True,
        type='search'
    ))

    return itemlist

def newest_movies(item):
    logger.trace()
    itemlist = list()

    data = httptools.downloadpage(item.url).data
    
    bloque = scrapertools.find_single_match(data, '<ul class="pelilist">(.*?)<ul class="pagination">')

    patron = '<a href="(.*?)".*?<img src="(.*?)".*?<h2>(.*?)</h2>.*?<span>(.*?)</span>'
    
    for url, poster, title, quality in scrapertools.find_multiple_matches(bloque, patron):

        fulltitle = title+'[COLOR yellow]'+quality+'[/COLOR]'
        
        new_item = item.clone(
            title=title,
            label=fulltitle,
            url=url,
            type="movie",
            content_type="servers",
            poster=poster,
            action="findvideos",
            quality=quality
            )
        
        itemlist.append(new_item)

    # Paginador
    bloque = scrapertools.find_single_match(data, '<ul class="pagination">.*?end .pagination -->')
       
    for url in scrapertools.find_multiple_matches(bloque, 'href="(.*?)<'):
        if "Next" in url:
            next_url = scrapertools.find_single_match(url, '(.*?)"')
            if next_url:
                itemlist.append(item.clone(
                    action="newest_movies",
                    url=next_url,
                    type='next'
                ))
      
    return itemlist

def newest_series(item):
    logger.trace()
    itemlist = list()

    data = httptools.downloadpage(item.url).data
    
    bloque = scrapertools.find_single_match(data, '<ul class="pelilist">(.*?)<ul class="pagination">')

    patron = '<a href="(.*?)".*?<img src="(.*?)".*?<h2.*?>(.*?)</h2>.*?<span>(.*?)</span>'
    
    for url, poster, title, quality in scrapertools.find_multiple_matches(bloque, patron):

        fulltitle = title+'[COLOR yellow]'+quality+'[/COLOR]'
        
        new_item = item.clone(
            title=title,
            label=fulltitle,
            url=url,
            content_type="episodes",
            poster=poster,
            type="tvshow",
            action="episodes",
            quality=quality
            )
        
        itemlist.append(new_item)

    # Paginador
    bloque = scrapertools.find_single_match(data, '<ul class="pagination">.*?end .pagination -->')
       
    for url in scrapertools.find_multiple_matches(bloque, 'href="(.*?)<'):
        if "Next" in url:
            next_url = scrapertools.find_single_match(url, '(.*?)"')
            if next_url:
                itemlist.append(item.clone(
                    action="newest_series",
                    url=next_url,
                    type='next'
                ))

      
    return itemlist

def episodes(item):
    logger.trace()
    itemlist = list()

    data = httptools.downloadpage(item.url).data

    bloque = scrapertools.find_single_match(data, '<ul class="buscar-list">.*?end .buscar-list')

    patron = '<a href="(.*?)".*?<img src="(.*?)".*?none;">(.*?)</strong>.*?' \
            ';">(.*?)</span>.*?;">(.*?)</span>.*?</span>.*?>(.*?)<'

    matches = scrapertools.find_multiple_matches(bloque,patron)

    for url, poster, title, idioma, quality, size in matches:
        title = title.replace('Serie ','').replace('Temporada','T.')
        #'Serie (.*?) Temporada (\d+) Capitulo (\d+)'
        new_item = item.clone(
        title=title,
        url=url,
        poster=poster,
        content_type='servers',
        type='item',
        action="findvideos"
        )
        
        itemlist.append(new_item)

    # Paginador
    bloque = scrapertools.find_single_match(data, '<ul class="pagination">.*?end .pagination -->')
       
    for url in scrapertools.find_multiple_matches(bloque, 'href="(.*?)<'):
        if "Next" in url:
            next_url = scrapertools.find_single_match(url, '(.*?)"')
            if next_url:
                itemlist.append(item.clone(
                    action="episodes",
                    url=next_url,
                    type='next'
                ))

    return itemlist

def findvideos(item):
    logger.trace()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    url = scrapertools.find_single_match(data, 'window.location.href = "(.*?)"')
 
    itemlist.append(item.clone( label=item.label, action="play", url=url, type='server', server='torrent'))
    itemlist = servertools.get_servers_from_id(itemlist)
    
    return itemlist

def movie_search(item):
    logger.trace()
    itemlist = []
    
    #busqueda con ñ
    item.query = item.query.replace('ñ','%F1')
    #--------------------
    url = HOST+'/index.php?page=buscar&q=%s' % item.query

    #primera busqueda
    item.url_1 = url+'&categoryIDR=757'
    
    data = httptools.downloadpage(item.url_1).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    
    bloque_1 = scrapertools.find_single_match(data,'<ul class="buscar-list">(.*?)end .buscar-list')
 
    patron_1 = '<a href="(.*?)".*?<img src="(.*?)".*?<b>(.*?)</h2>.*?</span>.*?</span>.*?<span>(.*?)</span>.*?href'

    matches_1 = scrapertools.find_multiple_matches(bloque_1, patron_1)

    #segunda busqueda en calidad HD
    item.url_2 = url+'&categoryIDR=1027'
    
    data = httptools.downloadpage(item.url_2).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)

    bloque_2 = scrapertools.find_single_match(data,'<ul class="buscar-list">(.*?)end .buscar-list')
 
    patron_2 = '<a href="(.*?)".*?<img src="(.*?)".*?<b>(.*?)</h2>.*?</span>.*?</span>.*?<span>(.*?)</span>.*?href'

    matches_2 = scrapertools.find_multiple_matches(bloque_2, patron_2)
    
    #unimos busquedas
    matches = matches_1+matches_2
    
    for url, poster, title, size in matches:
        title = title.replace('</b>','').replace('</font>','')
        quality = scrapertools.find_single_match(title,'\[(.*?)\]\[')
        title = scrapertools.find_single_match(title,'(.*?)\[')
        fulltitle= title + '[' + quality + ']' + size
        new_item = item.clone(
            title=title,
            label=fulltitle,
            url=url,
            poster=poster,
            type="movie",
            content_type='servers',
            action="findvideos"
            )
        
        itemlist.append(new_item)
        
    return itemlist

def tv_search(item):
    logger.trace()
    itemlist = []
    
    #busqueda con ñ
    item.query = item.query.replace('ñ','%F1')
    #--------------------
    url = HOST+'/index.php?page=buscar&q=%s' % item.query

    #primera busqueda
    item.url_1 = url+'&categoryIDR=767'
    
    data = httptools.downloadpage(item.url_1).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    
    bloque_1 = scrapertools.find_single_match(data,'<ul class="buscar-list">(.*?)end .buscar-list')
 
    patron_1 = '<a href="(.*?)".*?<img src="(.*?)".*?<b>(.*?)</b>.*?">(.*?)<.*?">(.*?)</span>.*?">(.*?)<'

    matches_1 = scrapertools.find_multiple_matches(bloque_1, patron_1)

    #segunda busqueda en calidad HD
    item.url_2 = url+'&categoryIDR=1469'
    
    data = httptools.downloadpage(item.url_2).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)

    bloque_2 = scrapertools.find_single_match(data,'<ul class="buscar-list">(.*?)end .buscar-list')
     
    patron_2 = '<a href="(.*?)".*?<img src="(.*?)".*?<b>(.*?)</b>.*?">(.*?)<.*?">(.*?)</span>.*?">(.*?)<'

    matches_2 = scrapertools.find_multiple_matches(bloque_2, patron_2)
    
    #unimos busquedas
    matches = matches_1+matches_2
    
    for url, poster, title, temporadas, idioma, quality in matches:
        temporadas = temporadas+' Temporadas'
        fulltitle= title+temporadas+quality 
        new_item = item.clone(
            title=title,
            label=fulltitle,
            url=url,
            poster=poster,
            type="tvshow",
            content_type='episodes',
            action="episodes"
            )
        
        itemlist.append(new_item)
        
    return itemlist

