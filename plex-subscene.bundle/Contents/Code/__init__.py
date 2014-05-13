import string
import os
import urllib
import tempfile
import zipfile
import re
import copy
import sys
import traceback
import smtplib
from email.mime.text import MIMEText


SUBSCENE_LANG_FILTER = "http://u.subscene.com/filter"
SUBSCENE_RETURN_URL = "http://subscene.com/subtitles/release?q=%s"
#SUBSCENE_QUERY = "http://subscene.com/subtitles/release?%s"
SUBSCENE_HOST = "http://subscene.com"
SUBSCENE_LANGUAGE_LOOKUP = {'Swedish': '39', 'German': '19', 'Farsi/Persian': '46', 'Hungarian/ English': '24', 'Estonian': '16', 'Telugu': '63', 'Vietnamese': '45', 'Romanian': '33', 'Azerbaijani': '55', 'Slovenian': '37', 'Malay': '50', 'Icelandic': '25', 'Hindi': '51', 'Dutch': '11', 'Brazillian Portuguese': '4', 'Korean': '28', 'Latvian': '29', 'Danish': '10', 'Indonesian': '44', 'Hungarian': '23', 'Catalan': '49', 'Bosnian': '60', 'Georgian': '62', 'Lithuanian': '43', 'Greenlandic': '57', 'French': '18', 'Norwegian': '30', 'Bengali': '54', 'Russian': '34', 'Thai': '40', 'Croatian': '8', 'Tamil': '59', 'Macedonian': '48', 'Bulgarian/ English': '6', 'Kurdish': '52', 'Finnish': '17', 'Ukranian': '56', 'Albanian': '1', 'Hebrew': '22', 'Bulgarian': '5', 'Turkish': '41', 'Tagalog': '53', 'Greek': '21', 'Burmese': '61', 'Chinese BG code': '7', 'English': '13', 'Serbian': '35', 'Esperanto': '47', 'Italian': '26', 'Portuguese': '32', 'Dutch/ English': '12', 'Big 5 code': '3', 'Japanese': '27', 'Manipuri': '65', 'Czech': '9', 'Slovak': '36', 'Spanish': '38', 'Urdu': '42', 'Polish': '31', 'Arabic': '2', 'English/ German': '15', 'Sinhala': '58'}


def Start():
    HTTP.CacheTime = 0
    Log("Subscene plugin started!!!")
    
    
# data structures
class SubInfo():
    def __init__(self, lang, url, sub, name):
        self.lang = lang
        self.url = url
        self.sub = sub
        self.name = name
        self.ext = string.split(self.name, '.')[-1]
        
    def __str__( self ):
        return (self.lang, self.url, self.sub, self.name, self.ext).__str__()

def distance(src, dst):
    src = src.strip().lower()
    dst = dst.strip().lower()
    if src == dst:
        return 100
    
    sizep=len(dst)+1
    sizet=len(src)+1
    matrix = [[0 for x in xrange(sizet)] for x in xrange(sizep)]
    
    matrix[0][0] = 0
    for i in range(1, sizep):
        matrix[i][0] = i

    for i in range(1, sizet):
        matrix[0][i] = i
        
    for i in range(1, sizep):
        for j in range(1, sizet):
            if dst[i-1]==src[j-1]:
                val = matrix[i-1][j-1]
            else:
                val = (1+matrix[i-1][j-1])
            matrix[i][j] = min(1+matrix[i-1][j], min(1+matrix[i][j-1], val))
            
    error = abs(((matrix[sizep-1][sizet-1] / len(src)) * 100) - 100)
    return 100 - error

# scrapping functions 
def searchSubs(lang, filename):
    subUrl = []
    
    name = os.path.splitext(os.path.basename(filename))[0]
    baseUrl = (SUBSCENE_RETURN_URL % urllib.urlencode( {'q': name} ))
    request = HTTP.Request(url=SUBSCENE_LANG_FILTER, 
        values={"ReturnUrl":urllib.quote_plus(baseUrl), 
            "SelectedIds": SUBSCENE_LANGUAGE_LOOKUP[lang], 
            "HearingImpaired": '0'}, 
        immediate=True)
    request.load()
    content = request.content
    
    root = HTML.ElementFromString(content)
    subpages = root.xpath("//tr//td[@class='a1']/a") # @href
    bestScore = 0
    
    # for each subpage, analyze the proximity of the 2 strings!
    for subtitle in subpages:
        data = subtitle.xpath('div/span');
        language = data[0].text.strip().lower()
        alternative = data[1].text
        
        if language != lang.strip().lower():
            continue
        
        score = distance(name, alternative)
        if score == 100: #exact match
            Log('Got a perfect match!')
            return subtitle.xpath('@href')
        elif Prefs['closest-match'] and score > bestScore: #closest match available
            Log('it is not a perfect match, needed '+str(score)+'% edition changes | '
                +name.strip().lower()+" @ " +alternative.strip().lower()
                +" for "+language )
            bestScore = score
            subUrl = subtitle.xpath('@href')
    
    return subUrl
    
def getSubsForPart(filename):
    # looking for subtitle for: filename
    # list of objects with: language, url, subtitle path, extension.
    siList = []
    lang = Prefs['language']
    subUrls = searchSubs(lang, filename)
    
    for url in subUrls:
        # go to the url and scrap the actual zip file to download.
        root = HTML.ElementFromURL(SUBSCENE_HOST + url)
        downloadItem = root.xpath("//a[@id='downloadButton']/@href")[0]
        finalDownload = SUBSCENE_HOST + downloadItem
        
        request = HTTP.Request(url=finalDownload, immediate=True)
        request.load()
        file = tempfile.NamedTemporaryFile(mode='w+b',delete=False)
        file.write(request.content)
        file.close()
        
        zipArchive = zipfile.ZipFile(file.name)
        for subName in zipArchive.namelist():
            subData = zipArchive.read(subName)
            si = SubInfo(lang, finalDownload, subData, subName)
            siList.append(si)
                
    return siList

# Agent classes
class PlexSubsceneAgentMovies(Agent.Movies):
    name = 'Plex Subscene Movies'
    languages = [Locale.Language.NoLanguage]
    primary_provider = False
    contributes_to = ['com.plexapp.agents.imdb']

    def search(self, results, media, lang):
        results.Append(MetadataSearchResult(id = media.primary_metadata.id, score = 100))

    def update(self, metadata, media, lang):
        for item in media.items:
            for part in item.parts:
                try:
                    Log("Title: %s" % media.title)
                    Log("Filename: %s" % part.file)
                    siList = getSubsForPart(part.file)

                    for si in siList:
                        part.subtitles[Locale.Language.Match(si.lang)][si.url] = Proxy.Media(si.sub, ext=si.ext)
                except Exception as e:
                    Log(traceback.format_exc(e))



class PlexSubsceneAgentTVShows(Agent.TV_Shows):
    name = 'Plex Subscene TV Shows'
    languages = [Locale.Language.NoLanguage]
    primary_provider = False
    contributes_to = ['com.plexapp.agents.thetvdb']

    def search(self, results, media, lang):
        results.Append(MetadataSearchResult(id = media.primary_metadata.id, score = 100))

    def update(self, metadata, media, lang):
        for season in media.seasons:
            for episode in media.seasons[season].episodes:
                for item in media.seasons[season].episodes[episode].items:
                    Log("show: %s" % media.title)
                    Log("Season: %s, Ep: %s" % (season, episode))
                    for part in item.parts:
                        try:
                            siList = getSubsForPart(part.file)

                            for si in siList:
                                part.subtitles[Locale.Language.Match(si.lang)][si.url] = Proxy.Media(si.sub, ext=si.ext)
                        except Exception as e:
                            Log(traceback.format_exc(e))

