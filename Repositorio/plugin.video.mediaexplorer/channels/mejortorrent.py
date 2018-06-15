# -*- coding: utf-8 -*-

from core.libs import *

HOST = 'http://www.mejortorrent.com'

def mainlist(item):
    logger.trace()
    itemlist = list()

    itemlist.append(item.clone(
        action="newest_movies",
        label="Peliculas",
        url=HOST+'/torrents-de-peliculas.html',
        type="item",
        group=True,
        content_type='movies'
    ))

    itemlist.append(item.clone(
        action="newest_movies",
        label="Peliculas HD",
        url=HOST + '/torrents-de-peliculas-hd-alta-definicion.html',
        type="item",
        group=True,
        content_type='movies'
    ))
    
    itemlist.append(item.clone(
        action="newest_series",
        label="Series",
        url=HOST+'/torrents-de-series.html',
        type="item",
        group=True,
        content_type='tvshows'
    ))

    itemlist.append(item.clone(
        action="newest_series",
        label="Series HD",
        url=HOST + '/torrents-de-series-hd-alta-definicion.html',
        type="item",
        group=True,
        content_type='tvshows'
    ))
    
    itemlist.append(item.clone(
        label='Buscar',
        action='busqueda',
        type='search'
    ))

    return itemlist

def busqueda(item):
    logger.trace()
    itemlist = list()

    itemlist.append(item.clone(
        label='Buscar Peliculas',
        action='movie_search',
        content_type='movies',
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
    data = unicode(data, "iso-8859-1", errors="replace").encode("utf-8")
    
    #extraemos bloque informacion
    bloque = scrapertools.find_multiple_matches(data, "<td><div align='justify'><center>(.*?)<br>")
    bloque = ''.join(bloque) #unimos los resultados
    #---------------------------

    patron = '<a href="([^<]+)">.*?<img src="(.*?)" '

    bloque_quality = scrapertools.find_multiple_matches(data,'<br>(.*?)</table>')
    bloque_quality = ''.join(bloque_quality)
    
    for url, poster in scrapertools.find_multiple_matches(bloque, patron):
        #
        title = scrapertools.find_single_match(url, '\d+-(.*?).html')
        title = title.replace('-',' ').replace('4K HDR','').replace('FullBluRay','')
        #
        quality = scrapertools.find_single_match(url, '(\d+)')
        quality = scrapertools.find_single_match(bloque_quality, quality+'.*?b>(.*?)<')
        quality = quality.replace('-',' ')
        #     
        url =  HOST + url
        poster = HOST + poster
        fulltitle= title+'[COLOR yellow]'+quality+'[/COLOR]'
        
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
    next_url = scrapertools.find_single_match(data, "</span> <a href='(.*?)'")
    if next_url:
        next_url = HOST + next_url
        itemlist.append(item.clone(
            action="newest_movies",
            url=next_url,
            type='next'
        ))
      
    return itemlist

def newest_series(item):
    logger.trace()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = unicode(data, "iso-8859-1", errors="replace").encode("utf-8")
    
    #extraemos bloque informacion
    bloque = scrapertools.find_multiple_matches(data, "<td><div align='justify'><center>(.*?)</center>")
    bloque = ''.join(bloque) #unimos los resultados   
    #---------------------------
    #extraemos bloque para titulo
    bloque_quality = scrapertools.find_multiple_matches(data,'</center>(.*?)</table>') 
    bloque_quality = ''.join(bloque_quality)
    #---------------------------

    patron = '<a href="([^<]+)">.*?<img src="([^<]+)" '
    
    for url, poster in scrapertools.find_multiple_matches(bloque, patron):
        #
        title = scrapertools.find_single_match(url,'\d+-(.*?).html')
        info = scrapertools.find_single_match(bloque_quality,url+'.*?\[(.*?)\]')
        info = '['+info+']'

        episode = scrapertools.find_single_match(bloque_quality, url+'.*?<b>(.*?)</b>')
        
        #titulo limpio para tmdb
        fulltitle = scrapertools.find_single_match(bloque_quality, url+'">([^<]+)<')
        temporada = scrapertools.find_single_match(fulltitle, '- (\d+).*?Temporada')
        temporada = temporada+'ªTemporada'
        fulltitle = scrapertools.find_single_match(fulltitle, '(.*?)- .+?')
        #-----------------------

        #     
        url =  HOST + url
        poster = HOST + poster
        title= episode+temporada+fulltitle+info

        if "episodio" in url:
            action="findvideos"
            content_type='servers'
        else:
            action="episodes"
            content_type='episodes'
                  
        new_item = item.clone(
            title=fulltitle,
            label=title,
            url=url,
            poster=poster,
            type="tvshow",
            content_type=content_type,
            extra="series",
            action=action
            )
        
        itemlist.append(new_item)

    # Paginador
    next_url = scrapertools.find_single_match(data, "</span> <a href='(.*?)'")
    if next_url:
        next_url = HOST + next_url
        itemlist.append(item.clone(
            action="newest_series",
            url=next_url,
            type='next'
        ))
      
      
    return itemlist

def findvideos(item):
    logger.trace()
    itemlist = list()

    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    
    urlserie = scrapertools.find_single_match(data,"<td valign='top'>.*?<a href='(.*?)'")
        
    data_torrent = scrapertools.find_single_match(data, "Torrent:.*?<a href='(.*?)'")
    url2 = HOST+"/"+data_torrent

    #descargamos la siguiente pagina
    data = httptools.downloadpage(url2).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    
    data_enlace = "Pincha <a href='(.*?)'>"

    url = scrapertools.find_single_match(data, data_enlace)

    #sacamos el tamaño del torrent    
    size = scrapertools.find_single_match(url,'(\d+,\d+.*?)\.')
    
    #-----------------------------------
    url = HOST + url
    
    if "series" in item.extra:
        urlserie = HOST+urlserie
        
        itemlist.append(item.clone( label=item.label, action="play", type='server', url=url, server='torrent'))
        itemlist = servertools.get_servers_from_id(itemlist)
        itemlist.append(item.clone( label='Ir a la serie', type='item', action="episodes", content_type="episodes", url=urlserie))

    else:
        itemlist.append(item.clone( label=item.title, action="play", url=url, type='server'))
        itemlist = servertools.get_servers_from_id(itemlist)
        
    return itemlist

def episodes(item):
    logger.trace()
    itemlist = list()

    data = httptools.downloadpage(item.url).data
    
    bloque = scrapertools.find_single_match(data,"<form name='episodios'.*?Descargar Seleccionados")   
    
    for url, title in scrapertools.find_multiple_matches(bloque, "<a href='(.*?)'>(.*?)</a>"):
        season = scrapertools.find_single_match(title,'([^<]+)[x,X]')
        episode = scrapertools.find_single_match(title,'[x,X]([^<]+)')
        
        new_item = item.clone(
            title=title,
            label=title,#quitar si se pone type
            url=url,
            episode=episode,
            season=season,
            #type='episode',   #da error en algunos enlaces,se pierde el tmdb capitulos
            content_type="servers",
            action="findvideos"
            )
        
        itemlist.append(new_item)

    return itemlist

def movie_search(item):
    logger.trace()
    #para busqueda con ñ
    item.query = item.query.replace('ñ','%F1')
    #-------------------
    item.url = 'http://www.mejortorrent.com/secciones.php?sec=buscador&valor=%s' % item.query
    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = unicode(data, "iso-8859-1", errors="replace").encode("utf-8")
    
    bloque = scrapertools.find_single_match(data,'squeda(.*?)</table></td>')
    
    patron = "<td><a href='(.*?)'.*?textDecoration.*?\">(.*?)</a>.*?'>(.*?)<(.*?)height"
    
    for url, title, quality, category in scrapertools.find_multiple_matches(bloque, patron):

        title=title.replace('<font Color=\'darkblue\'>','').replace('</font>','').replace('(fullbluray)','').replace('(hdr)','').replace('(hevc X265)','').replace('[3d]','').replace('(4k-hdr)','').replace('[subs. Integrados]','').replace('-.*?Temporada','').replace('[720p]','')
        title=title.strip('.')
        
        url = HOST+url
        fulltitle =title+'[COLOR yellow]'+quality+'[/COLOR]'
        #filtramos solo las peliculas
        if "Película" in category:
            new_item = item.clone(
                title=title,
                label=fulltitle,
                url=url,
                type="movie",
                action="findvideos"
                )
        
            itemlist.append(new_item)
        
    return itemlist

def tv_search(item):
    logger.trace()
    #para busqueda con ñ
    item.query = item.query.replace('ñ','%F1')
    #--------------------
    item.url = 'http://www.mejortorrent.com/secciones.php?sec=buscador&valor=%s' % item.query
    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = unicode(data, "iso-8859-1", errors="replace").encode("utf-8")
    
    bloque = scrapertools.find_single_match(data,'squeda(.*?)</table></td>')
    
    patron = "<td><a href='(.*?)'.*?textDecoration.*?\">(.*?)</a>.*?'>(.*?)<(.*?)</tr>"
    
    for url, title, quality, category in scrapertools.find_multiple_matches(bloque, patron):
        title=title.replace('<font Color=\'darkblue\'>','').replace('</font>','').replace('[720p]','').replace('[1080p]','')
        title=title.strip('.')
        fulltitle =title+'[COLOR yellow]'+quality+'[/COLOR]'
        #limpiamos titulo
        if "Temporada" or "Miniserie" in title:
            title = scrapertools.find_single_match(title, '(.*?)-')
        
        url = HOST+url        
        #filtramos solo las peliculas
        if "Serie" in category:
            new_item = item.clone(
                title=title,
                label=fulltitle,
                url=url,
                poster="",
                type="tvshow",
                content_type='episodes',
                action="episodes"
                )
        
            itemlist.append(new_item)
        
    return itemlist

