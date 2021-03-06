# import base64
import json

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from s4api.graphdb_api import GraphDBApi
from s4api.swagger import ApiClient
from urllib.parse import unquote, quote
from SPARQLWrapper import SPARQLWrapper, JSON
# from BaseXClient import BaseXClient
from lxml import etree
import xmltodict
# import requests
import random
import datetime

# from lxml import etree
# from urllib.requet import urlopen
# import datetime

_endpoint = "http://localhost:7200"
_repositorio = "xpand-music"

client = ApiClient(endpoint=_endpoint)
accessor = GraphDBApi(client)


# Create your views here.

def home(request):
    query = '''PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                    PREFIX cs: <http://www.xpand.com/rdf/>
                    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
                    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    
                    select ?id ?tname ?aname ?youtube
                    where { 
                        ?id rdf:type cs:Track .
                        ?id foaf:name ?tname .
                        ?id cs:youtubeVideo ?youtube .
                        ?id cs:MusicArtist ?artist .
                        ?artist foaf:name ?aname 
                        
                    }'''

    _body = {"query": query}
    res = accessor.sparql_select(body=_body, repo_name=_repositorio)
    res = json.loads(res)
    print(res)
    info = dict()

    for i in range(8):
        m = random.choice(res['results']['bindings'])
        info[unquote(m['tname']['value'])] = dict()
        info[unquote(m['tname']['value'])]['artista'] = unquote(m['aname']['value'])
        info[unquote(m['tname']['value'])]['url'] = "https://www.youtube.com/watch?v=" + unquote(m['youtube']['value'])
        info[unquote(m['tname']['value'])]['embed'] = "https://www.youtube.com/embed/" + unquote(m['youtube']['value'])

    albums = {"Ummagumma" : "Pink Floyd", "JackBoys" : "JackBoys and Travis Scott", "Back in Black" : "AC/DC"}

    tparams = {
        'tracks': info,
        'frase': "Songs",
        'albums' : albums
    }
    return render(request, "home.html", tparams)


def musicas(request):
    query = None
    if 'musicOrder' in request.POST:
        if "Most Played" == request.POST['musicOrder']:
            query = '''PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                        PREFIX cs: <http://www.xpand.com/rdf/>
                        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
                        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
                        
                        select ?id ?tname ?aname
                        where { 
                            ?id rdf:type cs:Track .
                            ?id foaf:name ?tname .
                            ?id cs:MusicArtist ?artist .
                            ?artist foaf:name ?aname .
                            ?id cs:playCount ?streams
                            }order by desc(xsd:integer(?streams))'''

        elif "Songs Name" == request.POST['musicOrder']:
            query = '''PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                        PREFIX cs: <http://www.xpand.com/rdf/>
                        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
                        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

                        select ?id ?tname ?aname
                        where { 
                            ?id rdf:type cs:Track .
                            ?id foaf:name ?tname .
                            ?id cs:MusicArtist ?artist .
                            ?artist foaf:name ?aname .
                            ?id cs:playCount ?streams
                            }order by asc(?tname)'''

        elif "Artist Name" == request.POST['musicOrder']:
            query = '''PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                        PREFIX cs: <http://www.xpand.com/rdf/>
                        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
                        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

                        select ?id ?tname ?aname
                        where { 
                            ?id rdf:type cs:Track .
                            ?id foaf:name ?tname .
                            ?id cs:MusicArtist ?artist .
                            ?artist foaf:name ?aname .
                            ?id cs:playCount ?streams
                            }order by asc(?aname)'''

    else:
        query = '''PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                            PREFIX cs: <http://www.xpand.com/rdf/>
                            PREFIX foaf: <http://xmlns.com/foaf/0.1/>
                            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

                            select ?id ?tname ?aname
                            where { 
                                ?id rdf:type cs:Track .
                                ?id foaf:name ?tname .
                                ?id cs:MusicArtist ?artist .
                                ?artist foaf:name ?aname .
                                ?id cs:playCount ?streams
                                }'''

    _body = {"query": query}
    res = accessor.sparql_select(body=_body, repo_name=_repositorio)
    res = json.loads(res)
    # print(res);
    info = dict()

    for m in res['results']['bindings']:
        info[unquote(m['tname']['value'])] = unquote(m['aname']['value'])

    tparams = {
        'tracks': info,
        'frase': "Songs",
    }
    return render(request, "tracks.html", tparams)


def artist_tracks(request):
    id = str(request.GET.get('id'))
    query = '''PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX cs: <http://www.xpand.com/rdf/>
                PREFIX foaf: <http://xmlns.com/foaf/0.1/>
                PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
                
                select ?id ?track ?music ?video
                where {
                    ?id foaf:name  "%s".
                    ?track cs:MusicArtist ?id .
                    ?track foaf:name ?music .
                    ?track cs:youtubeVideo ?video .
                }''' % (quote(id))

    _body = {"query": query}
    res = accessor.sparql_select(body=_body, repo_name=_repositorio)
    res = json.loads(res)
    # print(res)
    info = dict()
    for t in res['results']['bindings']:
        temp = dict()
        temp['img'] = "https://img.youtube.com/vi/" + t['video']['value'] + "/0.jpg"
        temp['video'] = "https://www.youtube.com/embed/" + t['video']['value']
        temp['link'] = "https://www.youtube.com/watch?v=" + t['video']['value']
        info[unquote(t['music']['value'])] = temp
    tparams = {
        'tracks': info,
        'frase': "Músicas do Artista: " + id
    }
    return render(request, "artist_tracks.html", tparams)


def artistas(request):
    if 'artistName' in request.POST:
        query = '''PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                    PREFIX cs: <http://www.xpand.com/rdf/>
                    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
                    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
                    
                    select ?id ?aname ?img
                    where { 
                        ?id rdf:type cs:MusicArtist .
                        ?id foaf:name ?aname .
                        ?id foaf:Image ?img
                    }order by asc(?aname)'''

    else:
        query = '''PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                            PREFIX cs: <http://www.xpand.com/rdf/>
                            PREFIX foaf: <http://xmlns.com/foaf/0.1/>
                            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    
                            select ?id ?aname ?img
                            where { 
                                ?id rdf:type cs:MusicArtist .
                                ?id foaf:name ?aname .
                                ?id foaf:Image ?img
                            }'''

    _body = {"query": query}
    res = accessor.sparql_select(body=_body, repo_name=_repositorio)
    res = json.loads(res)
    # print(res);
    info = dict()
    for a in res['results']['bindings']:
        temp = dict()
        temp['id'] = a['id']['value']
        temp['img'] = a['img']['value']
        info[unquote(a['aname']['value'])] = temp
        # info[a['id']['value']] = unquote(a['aname']['value'])

    # print(info)
    tparams = {
        'info': info,
        'frase': "Artistas:",
    }

    return render(request, "artistas.html", tparams)


def albums(request):
    query = '''PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX cs: <http://www.xpand.com/rdf/>
                PREFIX foaf: <http://xmlns.com/foaf/0.1/>
                PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
                
                select ?albumName ?aname ?producer ?data ?count ?img
                where {
                    ?album rdf:type cs:Album .
                    ?album foaf:name ?albumName .
                    ?album cs:MusicArtist ?idArt .
                    ?idArt foaf:name ?aname .
                    optional{
                        ?album cs:producer ?producer .
                    }
                    ?album cs:datePublished ?data .
                    ?album cs:playCount ?count .
                    ?album foaf:Image ?img .
                }order by asc(?albumName)'''

    _body = {"query": query}
    res = accessor.sparql_select(body=_body, repo_name=_repositorio)
    res = json.loads(res)
    # print(res);
    info = dict()
    for a in res['results']['bindings']:
        temp = dict()
        temp['artista'] = unquote(a['aname']['value'])
        if 'producer' in a.keys():
            temp['producer'] = unquote(a['producer']['value'])
        else:
            temp['producer'] = None
        temp['data'] = a['data']['value']
        temp['streams'] = a['count']['value']
        temp['nome'] = a['albumName']['value']
        temp['img'] = a['img']['value']
        info[unquote(a['albumName']['value'])] = temp
        # info[a['id']['value']] = unquote(a['aname']['value'])

    tparams = {
        'albums': info,
        'frase': "Albums:",
    }
    return render(request, "albums.html", tparams)


def albumInfo(request):
    id = str(request.GET.get('id'))
    print(request.GET)
    tparams = dict()
    query_BasicInfo = '''PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                            PREFIX cs: <http://www.xpand.com/rdf/>
                            PREFIX foaf: <http://xmlns.com/foaf/0.1/>
                            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

                            select ?album ?idArt ?aname ?wiki ?bio ?data ?genero ?prevAlbum ?nextAlbum ?count ?img ?recorder ?producer
                            where {
                                ?album foaf:name "%s" .
                                ?album rdf:type cs:Album .
                                ?album cs:MusicArtist ?idArt .
                                ?idArt foaf:name ?aname .
                                ?album cs:WikiData ?wiki .
                                ?album cs:biography ?bio .
                                ?album cs:datePublished ?data .
                                ?album cs:genre ?genero .
                                optional{
                                    ?album cs:previousAlbum ?prevAlbum .
                                }
                                optional{
                                    ?album cs:nextAlbum ?nextAlbum .
                                }
                                ?album cs:playCount ?count .
                                optional{
                                     ?album cs:producer ?producer .
                                }
                            #    ?album cs:similarAlbum ?simAlbum .
                                ?album foaf:Image ?img .

                            }''' % (quote(id))
    _body = {"query": query_BasicInfo}
    res = accessor.sparql_select(body=_body, repo_name=_repositorio)
    res = json.loads(res)
    res = res['results']['bindings'][0]
    print(res)
    tparams['name'] = id
    tparams['uri'] = res['album']['value']
    tparams['idArtista'] = res['idArt']['value']
    tparams['aname'] = unquote(res['aname']['value'])
    tparams['img'] = res['img']['value']
    tparams['bio'] = unquote(res['bio']['value'])
    tparams['data'] = res['data']['value']
    tparams['genero'] = unquote(res['genero']['value'])
    tparams['playCount'] = res['count']['value']
    tparams['prevAlbum'] = None
    tparams['nextAlbum'] = None
    tparams['producer'] = None
    print(res.keys())
    if ('prevAlbum' in res.keys()):
        tparams['prevAlbum'] = unquote(res['prevAlbum']['value'])
    if ('nextAlbum' in res.keys()):
        tparams['nextAlbum'] = unquote(res['nextAlbum']['value'])
    if ('producer' in res.keys()):
        tparams['producer'] = unquote(res['producer']['value'])

    query_Tags = '''PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                        PREFIX cs: <http://www.xpand.com/rdf/>
                        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
                        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

                        select ?idTag ?tag 
                        where {
                            ?album foaf:name "%s" .
                            ?album rdf:type cs:Album .
                            ?album cs:Tag ?idTag .
                            ?idTag foaf:name ?tag .
                        }
                        ''' % (quote(id))

    _body = {"query": query_Tags}
    res = accessor.sparql_select(body=_body, repo_name=_repositorio)
    res = json.loads(res)

    tags = dict()
    for t in res['results']['bindings']:
        tags[unquote(t['tag']['value'])] = t['idTag']['value']
    tparams['tags'] = tags

    query_simAlbums = '''PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                        PREFIX cs: <http://www.xpand.com/rdf/>
                        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
                        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

                        select ?simAlbum ?name
                        where {
                            ?album foaf:name "%s" .
                            ?album rdf:type cs:Album .
                            ?album cs:similarAlbum ?simAlbum .
                            ?simAlbum foaf:name ?name .
                        } ''' % (quote(id))

    _body = {"query": query_simAlbums}
    res = accessor.sparql_select(body=_body, repo_name=_repositorio)
    res = json.loads(res)

    simAlbums = dict()
    for a in res['results']['bindings']:
        temp = dict()
        temp['uri'] = a['simAlbum']['value']
        temp['id'] = a['name']['value']
        simAlbums[unquote(a['name']['value'])] = temp
    tparams['simAlbums'] = simAlbums

    query_recorders = '''PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                            PREFIX cs: <http://www.xpand.com/rdf/>
                            PREFIX foaf: <http://xmlns.com/foaf/0.1/>
                            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

                            select ?recorder
                            where {
                                ?album foaf:name "%s" .
                                ?album rdf:type cs:Album .
                                ?album cs:recorder ?recorder .

                            }  ''' % (quote(id))

    _body = {"query": query_recorders}
    res = accessor.sparql_select(body=_body, repo_name=_repositorio)
    res = json.loads(res)

    recorders = []
    for r in res['results']['bindings']:
        recorders.append(unquote(r['recorder']['value']))
    tparams['recorders'] = recorders

    return render(request, "albumRDFa.html", tparams)


def criarPlayList(request):
    query = '''PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                    PREFIX cs: <http://www.xpand.com/rdf/>
                    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
                    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

                    select ?id ?tname ?aname
                    where { 
                        ?id rdf:type cs:Track .
                        ?id foaf:name ?tname .
                        ?id cs:MusicArtist ?artist .
                        ?artist foaf:name ?aname
                    }'''

    _body = {"query": query}
    res = accessor.sparql_select(body=_body, repo_name=_repositorio)
    res = json.loads(res)
    # print(res);
    info = dict()

    for m in res['results']['bindings']:
        info[unquote(m['tname']['value'])] = dict()
        info[unquote(m['tname']['value'])]["artista"] = unquote(m['aname']['value'])
        info[unquote(m['tname']['value'])]["id"] = m['id']['value']

    if 'playlistName' in request.POST:
        nomes = request.POST.getlist('nameMusica')
        playlistNome = request.POST['playlistName']
        # print(len(nomes))
        print(nomes)
        if len(nomes) == 0 or playlistNome == "":
            tparams = {
                'tracks': info,
                'frase': "Songs:",
                'erro': True
            }
            return render(request, "criarPlayList.html", tparams)
        else:

            querysIDS = """
                        PREFIX cs: <http://www.xpand.com/rdf/>
                        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                        select * where { 
                            ?p rdf:type cs:Playlist
                        } 
                    """
            _body = {"query": querysIDS}
            res = accessor.sparql_select(body=_body, repo_name=_repositorio)
            res = json.loads(res)

            id = "http://www.xpand.com/playlist/" + quote(playlistNome)

            for i in res['results']['bindings']:
                if id == i['p']['value']:
                    tparams = {
                        'tracks': info,
                        'frase': "Songs:",
                        'erro': True
                    }
                    return render(request, "criarPlayList.html", tparams)

            query_insert = """
                            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                            PREFIX cs: <http://www.xpand.com/rdf/>
                            PREFIX foaf: <http://xmlns.com/foaf/0.1/>

                            insert data {
                                <%s> rdf:type cs:Playlist .
                                <%s> foaf:name "%s" .
                                <%s> cs:NumItems "%s" .
                                <%s> cs:datePublished "%s"
                            }
                            """ % (id, id, playlistNome, id, len(nomes), id, str(datetime.date.today()))
            _body = {"update": query_insert}
            res1 = accessor.sparql_update(body=_body, repo_name=_repositorio)

            for musica in nomes:
                query_de_insert = """
                                PREFIX cs: <http://www.xpand.com/rdf/>
                                insert data {<%s> cs:Track <%s>}
                            """ % (id, musica)
                print(musica)
                print(id)
                # listArtistas.append(a['outras']['value'])
                _body = {"update": query_de_insert}
                res1 = accessor.sparql_update(body=_body, repo_name=_repositorio)

            tparams = {
                'tracks': info,
                'frase': "Songs:",
                'erro': False
            }

            return render(request, "criarPlayList.html", tparams)
    else:
        tparams = {
            'tracks': info,
            'frase': "Songs",
            'erro': False
        }
        return render(request, "criarPlayList.html", tparams)


def insertKnowsArtist(artista):


    query = '''PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                        PREFIX cs: <http://www.xpand.com/rdf/>
                        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
                        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

                        select ?banda  ?outras
                        where
                        {
                            ?banda foaf:name "%s" .
                            ?banda cs:recorder ?recorder .
                            ?outras cs:recorder ?recorder .
                            ?outras rdf:type cs:MusicArtist .
                        }''' % (quote(artista))

    _body = {"query": query}
    res = accessor.sparql_select(body=_body, repo_name=_repositorio)
    res = json.loads(res)
    print(res)

    # listArtistas = []
    art = res['results']['bindings'][0]['banda']['value']
    print(art)
    for a in res['results']['bindings']:
        if a['outras']['value'] != art:
            query_insert = """
                        insert data {<%s> foaf:knows <%s>}
                    """ % (art, a['outras']['value'])
            # listArtistas.append(a['outras']['value'])
            _body = {"update": query_insert}
            res1 = accessor.sparql_update(body=_body, repo_name=_repositorio)


def knowArtists(request):
    info = dict()
    if 'ArtistName' in request.POST:
        artistNome = request.POST['ArtistName']
        print(artistNome)

        if artistNome == "":
            tparams = {
                'info': info,
                'frase': "Artists",
                'erro': True,
                'erroFrase': "Insert the information requested"
            }
            return render(request, "knowArtists.html", tparams)

        query_ask = '''PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                    PREFIX cs: <http://www.xpand.com/rdf/>
                    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
                    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
                    ask{
                        ?id foaf:name "%s"
                        }'''%(quote(artistNome))

        _body = {"query": query_ask}
        res = accessor.sparql_select(body=_body, repo_name=_repositorio)
        res = json.loads(res)
        print("ASK:",res['boolean'])
        if res['boolean'] == False:
            print("Aqui")
            tparams = {
                'info': info,
                'frase': "Artists",
                'erro': True,
                'erroFrase': "Insert a correct Artist"
            }
            return render(request, "knowArtists.html", tparams)

        insertKnowsArtist(artistNome)
        query = '''PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                    PREFIX cs: <http://www.xpand.com/rdf/>
                    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
                    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

                    select ?banda  ?anome ?img
                    where
                    {
                        ?banda foaf:name "%s" .
                        ?banda foaf:knows ?outra .
                        ?outra foaf:name ?anome .
                        ?outra foaf:Image ?img .
                    }''' % (quote(artistNome))

        _body = {"query": query}
        res = accessor.sparql_select(body=_body, repo_name=_repositorio)
        res = json.loads(res)
        print(res)

        for a in res['results']['bindings']:
            info[unquote(a['anome']['value'])] = a['img']['value']

    tparams = {
        'info': info,
        'frase': "Artists:",
        'erro': False
    }
    return render(request, "knowArtists.html", tparams)


def myPlayList(request):
    query = '''PREFIX cs: <http://www.xpand.com/rdf/>
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                select * where { 
                    ?p rdf:type cs:Playlist
                } '''
    _body = {"query": query}
    res = accessor.sparql_select(body=_body, repo_name=_repositorio)
    res = json.loads(res)
    #print(res)
    info = dict()
    for p in res['results']['bindings']:
        query = '''PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                    PREFIX cs: <http://www.xpand.com/rdf/>
                    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    
                    select ?nome ?numItems ?data ?track ?tname ?idYT 
                    where{
                        <%s> rdf:type cs:Playlist .
                        <%s> foaf:name ?nome .
                        <%s> cs:NumItems ?numItems .
                        <%s> cs:datePublished ?data .
                        optional{
                            <%s> cs:Track ?track .
                            ?track foaf:name ?tname .
                            optional{
                                ?track cs:youtubeVideo ?idYT .
                            }
                        }
                    }''' % (p['p']['value'], p['p']['value'], p['p']['value'], p['p']['value'], p['p']['value'])
        _body = {"query": query}
        res1 = accessor.sparql_select(body=_body, repo_name=_repositorio)
        res1 = json.loads(res1)
        #print(res1)
        key = res1['results']['bindings'][0]
        info[p["p"]["value"]] = dict()
        info[p["p"]["value"]]["name"] = key["nome"]["value"]
        info[p["p"]["value"]]["data"] = key["data"]["value"]
        info[p["p"]["value"]]["numItems"] = key["numItems"]["value"]
        info[p["p"]["value"]]["tracks"] = dict()
        for t in res1['results']['bindings']:
            print(t)
            if "track" in t.keys():
                temp = dict()
                temp['tname'] = unquote(t['tname']['value'])
                if 'idYT' in t.keys():
                    temp['idYT'] = "https://img.youtube.com/vi/" + t['idYT']['value'] + "/0.jpg"
                else:
                    temp['idYT'] = "https://songdewnetwork.com/sgmedia/assets/images/default-album-art.png"
                info[p["p"]["value"]]["tracks"][t["track"]["value"]] = temp

    print(info)
    tparams = {
        'playlist': info,
        'frase': "Playlists:",
    }
    return render(request, "myPlayList.html", tparams)


def delete(request):
    id = int(request.GET['id']) - 1
    query = '''PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX cs: <http://www.xpand.com/rdf/>
                PREFIX foaf: <http://xmlns.com/foaf/0.1/>

                select ?p ?nome 
                where{
                    ?p rdf:type cs:Playlist .
                    ?p foaf:name ?nome .
                }'''
    _body = {"query": query}
    res = accessor.sparql_select(body=_body, repo_name=_repositorio)
    res = json.loads(res)

    playlists = []
    for a in res['results']['bindings']:
        playlists.append(a["p"]["value"])

    print(playlists[id])

    query_delete = '''
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX cs: <http://www.xpand.com/rdf/>

            delete data {
                <%s> rdf:type cs:Playlist
            } 
            ''' % playlists[id]

    _body = {"update": query_delete}
    res = accessor.sparql_update(body=_body, repo_name=_repositorio)

    return redirect(myPlayList)

def Recommendations(request):
    album = request.GET['album'].replace(" ","_")
    album = "http://dbpedia.org/resource/"+album
    print(album)
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    sparql.setQuery("""
                    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                    PREFIX dbo:  <http://dbpedia.org/ontology/>
                    PREFIX dbp:  <http://dbpedia.org/property/>
                    SELECT ?label ?artist ?date ?genre ?cover ?abstract ?thumbnail
                    WHERE { <%s> rdfs:label ?label .
                            <%s> dbp:artist ?artist . 
                            optional{
                                <%s> dbp:released ?date .
                            } 
                            optional{
                                <%s> dbp:genre ?genre .
                            }
                            optional{
                                <%s> rdfs:comment ?abstract .
                            } 
                             optional{
                                <%s> dbo:thumbnail ?thumbnail .
                                }
                     }
                """ % (album,album,album,album,album,album))
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    print(results)
    tparams = dict()
    for result in results["results"]["bindings"]:
        tparams["name"] = result["label"]["value"]
        tparams["artist"] = result["artist"]["value"]
        if "date" in result.keys():
            tparams["date"] = result["date"]["value"]
        if "genre" in result.keys():
            tparams["genre"] = result["genre"]["value"]
        if "abstract" in result.keys():
            if result["abstract"]["xml:lang"] == "pt" or result["abstract"]["xml:lang"] == "en":
                tparams["abstract"] = result["abstract"]["value"]
        if "thumbnail" in result.keys():
            tparams["thumbnail"] = result["thumbnail"]["value"]
        else:
            tparams["thumbnail"] = "https://songdewnetwork.com/sgmedia/assets/images/default-album-art.png"

    # print('---------------------------')

    # for result in results["results"]["bindings"]:
    #     print('%s: %s' % (result["label"]["xml:lang"], result["label"]["value"]))

    return render(request, "Recommendations.html", tparams)