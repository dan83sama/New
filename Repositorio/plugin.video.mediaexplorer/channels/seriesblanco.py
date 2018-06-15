# -*- coding: utf-8 -*-
from core.libs import *

HOST = 'https://seriesblanco.com'

LNG = Languages({
    Languages.sub_es: ['jpsub', 'japovose', 'vose', 'vos'],
    Languages.sub_en: ['vosi'],
    Languages.es: ['esp', 'es'],
    Languages.vo: ['vo'],
    Languages.la: ['latino', 'la']
})

QLT = Qualities({
    Qualities.hd_full: ['1080p'],
    Qualities.hd: ['720p'],
    Qualities.sd: ['sd']
})


def mainlist(item):
    logger.trace()
    itemlist = list()

    # "Series Actualizadas"
    itemlist.append(item.clone(
        action="tvshows_newest",
        label="Series actualizadas",
        url=HOST,
        type="item",
        content_type='tvshows'
    ))

    # "Últimas series añadidas: (+Novedades Series)" https://seriesblanco.com/fichas_creadas/
    itemlist.append(item.clone(
        action="tvshows_news",
        label="Nuevas series",
        url=HOST + "/fichas_creadas/",
        type="item",
        content_type='tvshows'
    ))

    #
    itemlist.append(item.clone(
        action="newest_episodes",
        label="Episodios de estreno",
        url=HOST,
        type="item",
        content_type='episodes'
    ))

    # "Series más vistas"
    itemlist.append(item.clone(
        action="tvshows",
        label="Series más vistas",
        url=HOST + "/listado-visto/",
        type="item",
        content_type='tvshows'
    ))

    # "Listado alfabético"
    itemlist.append(item.clone(
        action="tvshows_az",
        label="Listado alfabético",
        type="item",
        url=HOST,
        content_type='tvshows'
    ))

    # "Series por género"
    itemlist.append(item.clone(
        action="generos",
        label="Géneros",
        url=HOST,
        type="item"
    ))

    # "Buscar"
    itemlist.append(item.clone(
        action="tv_search",
        label="Buscar",
        query=True,
        type='search',
        category='tvshow',
        content_type='tvshows'
    ))

    return itemlist


def tvshows(item):
    logger.trace()
    itemlist = list()

    data = httptools.downloadpage(item.url).data.replace('"', "'")
    data = re.sub(r"\n|\r|\t|\s{2}| ", "", data)

    patron = "<div style='float:left;width:.*?"
    patron += "<a href='([^']+).*?"
    patron += "src='([^']+).*?"
    if item.query:
        patron += "title='([^']+)"
    else:
        patron += "<p style='width:142px; height:35px'>([^<]+)</p>"

    for url, poster, title in scrapertools.find_multiple_matches(data, patron):
        new_item = item.clone(
            action='seasons',
            label=title,
            tvshowtitle=title,
            title=title,
            url=HOST + url,
            poster=poster,
            type='tvshow',
            content_type='seasons')

        itemlist.append(new_item)

    # Si es necesario añadir paginacion
    if "<span class='label label-info'>" in data and not item.query:
        next_page = scrapertools.find_single_match(data, "</a></span> <a href='([^']+)")
        if "?pagina=" in item.url:
            item.url = item.url.split('?')[0]

        itemlist.append(item.clone(
            url=item.url + next_page,
            type='next'
        ))

    return itemlist


def tvshows_news(item):
    logger.trace()
    itemlist = list()

    data = httptools.downloadpage(item.url).data.replace('"', "'")
    data = re.sub(r"\n|\r|\t|\s{2}| ", "", data)

    patron = "<div class='col-md-4'>.*?"
    patron += "<a href='([^']+).*?"
    patron += "src='([^']+).*?"
    patron += "<h4>([^<]+).*?"
    patron += "<p>([^<]+)</p>"

    for url, poster, title, plot in scrapertools.find_multiple_matches(data, patron):
        new_item = item.clone(
            action='seasons',
            label=title,
            tvshowtitle=title,
            title=title,
            url=HOST + url,
            poster=poster,
            plot=plot,
            type='tvshow',
            content_type='seasons')

        itemlist.append(new_item)

    return itemlist


def tvshows_newest(item):
    logger.trace()
    itemlist = list()

    if not item.url:
        item.url = HOST

    data = httptools.downloadpage(item.url).data.replace('"', "'")
    data = re.sub(r"\n|\r|\t|\s{2}| ", "", data)

    patron = "<li style='display: block;padding-top: 20px;'>.*?"
    patron += "<a href='([^']+).*?"
    patron += "src='([^']+).*?"
    patron += "alt='([^']+).*?"
    patron += "<span class='strong'>([^<]+)"



    for url, poster, title, season_episode in scrapertools.find_multiple_matches(data, patron):
        title = title.replace(season_episode, "").strip()
        year = scrapertools.find_single_match(title, "\((\d{4})\)")
        if year:
            title = title.replace("(%s)" % year, "").strip()

        new_item = item.clone(
            action='seasons',
            label=title,
            tvshowtitle=title,
            title=title,
            url=HOST + url,
            poster=poster,
            type='tvshow',
            year=year,
            content_type='seasons')

        itemlist.append(new_item)

    return itemlist


def tvshows_az(item):
    logger.trace()
    itemlist = list()

    for letra in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        itemlist.append(item.clone(
            action="tvshows",
            label=letra,
            type="item",
            content_type='tvshows',
            url=HOST + "/listado-%s/" % letra
        ))

    return itemlist


def tv_search(item):
    logger.trace()
    item.url = "%s/search.php?q1=%s" % (HOST, item.query.replace(" ", "+"))

    return tvshows(item)


def generos(item):
    logger.trace()
    itemlist = list()

    GENEROS = {"Animación": "/listado/animacion/",
               "Aventuras": "/listado/aventuras/",
               "Ciencia Ficción": "/listado/ciencia/",
               "Comedia": "/listado/comedia/",
               "Documental": "/listado/documental/",
               "Fantástico": "/listado/fantatico/",
               "Infantil": "/listado/infantil/",
               "Intriga": "/listado/intriga/",
               "Musical": "/listado/musical/",
               "Programas": "/listado/programa/",
               "Romance": "/listado/romance/",
               "Telenovela": "/listado/telenovela/",
               "Terror": "/listado/terror/",
               "Thriller": "/listado/thriller/",
               "Western": "/listado/western/"}

    for label in sorted(GENEROS.keys()):
        itemlist.append(item.clone(
            action="tvshows",
            label=label,
            type="item",
            content_type='tvshows',
            url=HOST + GENEROS[label]
        ))

    return itemlist


def seasons(item):
    logger.trace()
    itemlist = list()

    data = httptools.downloadpage(item.url).data.replace('"', "'")
    data = re.sub(r"\n|\r|\t|\s{2}| ", "", data)

    if not item.plot:
        item.plot = scrapertools.find_single_match(data,
                                                   "<div role='tabpanel' class='tab-pane' id='profile2'>([^<]+)</div>")

    patron = "<div class='panel panel-primary'><div class='panel-heading'>.*?"
    patron += "<span itemprop='seasonNumber' class='fa fa-arrow-down'>([^<]+)"

    for season in scrapertools.find_multiple_matches(data, patron):
        num_season = scrapertools.find_single_match(season, "Temporada (\d+)")
        itemlist.append(item.clone(
            action="episodes",
            season=int(num_season),
            type='season',
            plot=item.plot,
            content_type='episodes'
        ))

    return itemlist


def newest_episodes(item):
    logger.trace()
    itemlist = list()

    if not item.url:
        item.url = HOST

    data = httptools.downloadpage(item.url).data.replace('"', "'")
    data = re.sub(r"\n|\r|\t|\s{2}| ", "", data)

    patron = "<li><h6 style='text-align: center;'><img src='[^']+' alt='([^']+).*?"
    patron += "href='([^']+).*?"
    patron += "src='([^']+)' data-original-title='([^']+)"

    for lang, url, thumb, title in scrapertools.find_multiple_matches(data, patron):
        season_episode = scrapertools.get_season_and_episode(title)
        if season_episode:
            season, episode = season_episode
            title = scrapertools.find_single_match(title, "(.*?)%dx%02d" % (season, episode))
            year = scrapertools.find_single_match(title, "\((\d{4})\)")

            if year:
                title = scrapertools.find_single_match(title, "(.*?)\(%s\)" % year).strip()

            new_item = item.clone(
                label=title,
                tvshowtitle=title,
                action="findvideos",
                lang=[LNG.get(lang.replace(".", "").lower())],
                url=HOST + url,
                thumb=thumb,
                season=season,
                episode=episode,
                type='episode',
                content_type='servers')

            if year:
                new_item.year = year

            itemlist.append(new_item)

    return itemlist


def episodes(item):
    logger.trace()
    itemlist = list()

    data = httptools.downloadpage(item.url).data.replace('"', "'")
    data = re.sub(r"\n|\r|\t|\s{2}| ", "", data)

    patron = "<div class='panel panel-primary'><div class='panel-heading'>.*?"
    patron += "<span itemprop='seasonNumber' class='fa fa-arrow-down'>([^<]+).*?"
    patron += "<tbody><form action='' id='demoForm' method='post'>(.*?)</tbody></table></form>"

    for season, data in scrapertools.find_multiple_matches(data, patron):
        num_season = scrapertools.find_single_match(season, "Temporada (\d+)")
        # TODO posible fallo si temporada o episodio buscados son 0
        if item.season and item.season != int(num_season):
            # Si buscamos los episodios de una temporada concreta y no es esta (num_season)...
            continue

        patron = "<a href='([^']+).*?"
        patron += "<span itemprop='episodeNumber'>([^<]+).*?"
        patron += "<td>(.*?)</td>"

        for url, episode, langs in scrapertools.find_multiple_matches(data, patron):
            num_season, num_episode = scrapertools.get_season_and_episode(episode)

            if item.episode and item.episode != num_episode:
                # Si buscamos un episodio concreto y no es este (num_episode)...
                continue

            itemlist.append(item.clone(
                title=item.tvshowtitle,
                url=HOST + url,
                action="findvideos",
                episode=num_episode,
                season=num_season,
                lang=[LNG.get(l) for l in
                      scrapertools.find_multiple_matches(langs, "<img src=/banderas/([^\.]+)\.png")],
                type='episode',
                content_type='servers'
            ))

    return itemlist


def findvideos(item):
    logger.trace()
    itemlist = list()

    data = httptools.downloadpage(item.url).data.replace('"', "'")
    data = re.sub(r"\n|\r|\t|\s{2}| ", "", data)

    patron = "<h1 class='panel-title'>([^<]+)</h1>(.*?)</div></div></div>"
    for panel_title, data in scrapertools.find_multiple_matches(data, patron):
        patron = "<img src='https://seriesblanco.com/banderas/([^\.]+)\.png'.*?"
        patron += "<a href='([^']+).*?"
        patron += "<img src='/servidores/([^\.]+).*?"
        patron += "<div class='grid_content sno'><span>[^<]+</span>.*?"
        patron += "<div class='grid_content sno'><span>([^<]*)</span>"

        for lang, url, server, comment in scrapertools.find_multiple_matches(data, patron):
            comment = re.compile('sub-inglés-?', re.I).sub("", comment)
            if '1080p' in comment:
                quality = QLT.get('1080p')
            elif '720p' in comment or 'HDiTunes' in comment:
                quality = QLT.get('720p')
            elif comment:
                quality = QLT.get('sd')
            else:
                quality = ""

            itemlist.append(item.clone(
                url=HOST + url,
                action='play',
                type='server',
                lang=LNG.get(lang),
                quality=quality,
                server=server,
                stream=('Ver' in panel_title)
            ))

        itemlist = servertools.get_servers_from_id(itemlist)

    return itemlist


def play(item):
    logger.trace()

    if item.url.startswith(HOST):
        data = httptools.downloadpage(item.url).data

        ajax_link = re.findall("loadEnlace\((\d+),(\d+),(\d+),(\d+)\)", data)
        ajax_data = ""
        for serie, temp, cap, linkID in ajax_link:
            # logger.debug(
            #     "Ajax link request: Serie = %s - Temp = %s - Cap = %s - Link = %s" % (serie, temp, cap, linkID))
            ajax_data += httptools.downloadpage(
                HOST + '/ajax/load_enlace.php?serie=' + serie + '&temp=' + temp + '&cap=' + cap + '&id=' + linkID).data

        if ajax_data:
            data = ajax_data

        patron = "window.location.href\s*=\s*[\"']([^\"']+)'"
        item.url = scrapertools.find_single_match(data, patron)
        servertools.normalize_url(item)
    return item
