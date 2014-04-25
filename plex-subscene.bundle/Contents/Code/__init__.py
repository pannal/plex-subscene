import string
import os
import urllib
import zipfile
import re
import copy

#Plex Theme Music
#SUBSCENE_LANG_FILTER = "http://subscene.com/filter"
SUBSCENE_LANG_FILTER = "http://localhost/data"
SUBSCENE_RETURN_URL = "/subtitles/release?%s"
SUBSCENE_QUERY = "http://subscene.com/subtitles/release?%s"

def Start():
    HTTP.CacheTime = CACHE_1DAY
    filename = '/media/movies/Get.Low.2010.720p.BRRip.XviD.AC3-FLAWL3SS/Get.Louw.2010.720p.BRRip.XviD.AC3-FLAWL3SS.avi3'
    #Log(distance('a','b'))
    #Log(distance('zzzz','wwwwwwwwwww'))
    #Log(distance('masage','message'))
    Log(searchSubs('en', filename))
    Log("Subscene plugin started!!!")

# data structures
class SubInfo():
    def __init__(self, lang, url, sub, name):
        self.lang = lang
        self.url = url
        self.sub = sub
        self.name = name
        self.ext = string.split(self.name, '.')[-1]


def distance(src, dst):
    src = src.strip().lower()
    dst = dst.strip().lower()
    if src == dst:
        return 0
    
    sizep=len(dst)+1
    sizet=len(src)+1
    matrix = [[0 for x in xrange(sizet)] for x in xrange(sizep)]
    
    matrix[0][0]=0;
    for i in range(1, sizep):
        matrix[i][0] = i

    for i in range(1, sizet):#(i=1;i<=sizet;matriz[0][i]=i++):
        matrix[0][i] = i
        
    for i in range(1, sizep):#(i=1;i<=sizep;i++):
        for j in range(1, sizet):#(j=1;j<=sizet;j++):
            if dst[i-1]==src[j-1]:
                val = matrix[i-1][j-1]
            else:
                val = (1+matrix[i-1][j-1])
            matrix[i][j] = min(1+matrix[i-1][j], min(1+matrix[i][j-1], val))
            
    return matrix[sizep-1][sizet-1]
    

# scrapping functions 
def searchSubs(lang, filename):
    subUrl = None
    
    name = os.path.splitext(os.path.basename(filename))[0]
    baseUrl = (SUBSCENE_RETURN_URL % urllib.urlencode( {'q': name} ))
    request = HTTP.Request(url=SUBSCENE_LANG_FILTER, values={"ReturnUrl":urllib.quote_plus(baseUrl), "SelectedIds": 13, "HearingImpaired": '0'}, immediate=True)
    request.load()
    content = request.content
    
    root = HTML.ElementFromString(content)
    subpages = root.xpath("//tr//td[@class='a1']/a") # @href
    bestScore = len(name)
    
    # for each subpage, analyze the proximity of the 2 strings!
    for subtitle in subpages:
        data = subtitle.xpath('div/span');
        language = data[0]
        alternative = data[1].text
        score = distance(name, alternative)
        if score == 0: #exact match
            Log('Got a perfect match!')
            return subtitle.xpath('@href')
        elif Prefs['closest-match'] and score < bestScore: #closest match available
            Log('it is not a perfect match, needed '+str(score)+' edition change')
            bestScore = score
            subUrl = subtitle.xpath('@href')
    
    return subUrl
    
    
# Agent classes
class PlexSubsceneAgentMovies(Agent.Movies):
    name = 'Plex Subscene Movies'
    languages = [Locale.Language.NoLanguage]
    primary_provider = False
    contributes_to = ['com.plexapp.agents.imdb']

    def search(self, results, media, lang):
        results.Append(MetadataSearchResult(id = media.primary_metadata.id, score = 100))

    def update(self, metadata, media, lang):
        pass


class PlexSubsceneAgentTVShows(Agent.TV_Shows):
    name = 'Plex Subscene TV Shows'
    languages = [Locale.Language.NoLanguage]
    primary_provider = False
    contributes_to = ['com.plexapp.agents.thetvdb']

    def search(self, results, media, lang):
        results.Append(MetadataSearchResult(id = media.primary_metadata.id, score = 100))

    def update(self, metadata, media, lang):
        pass
