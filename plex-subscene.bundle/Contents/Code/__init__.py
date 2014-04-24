import string
import os
import urllib
import zipfile
import re
import copy

__author__= "kronenthaler"
__date__ = "$Apr 24, 2014 11:50:46 AM$"

SUBSCENE_LANG_FILTER = "http://subscene.com/filter"
SUBSCENE_QUERY = "http://subscene.com/subtitles/release?q=%s"

# data structures
class SubInfo():
    def __init__(self, lang, url, sub, name):
        self.lang = lang
        self.url = url
        self.sub = sub
        self.name = name
        self.ext = string.split(self.name, '.')[-1]

# scrapping functions 
def searchSubs(lang, filename):
	subUrls = []
	
	baseUrl = (SUBSCENE_QUERY % urllib.urlencode(filename))
	urlFiltered = "ReturnUrl=%s&SelectedIds=%s&HearingImpaired=" % baseUrl , 13
	
	request = HTTP.request(url=SUBSCENE_LANG_FILTER, values={"ReturnUrl":baseUrl, "SelectedIds": 13, "HearingImpaired": ''})
	request.load()
		
	root = HTML.ElementFromString(request.content)
	subpages = root.xpath("//tr//td[@class='a1']/a/@href")
	
	
	return subUrls

def getSubsForPart(media_title, filename):
	# looking for subtitle for: filename
	# list of objects with: language, url, subtitle path, extension.
	siList = []
	
	subUrls = searchSubs(Prefs['language'], filename)
	for url in subUrls:
		zipArchive = Archive.ZipFromURL(subUrl)
		for name in zipArchive:
			if name[-1] == "/":
				Log("Ignoring folder")
				continue

			subData = zipArchive[name]
			si = SubInfo(lang, subUrl, subData, name)
			siList.append(si)

	return siList

'''
# create 2 parsers, one for movies and one for tv shows.
class PlexSubsceneMovies (Agent.Movies):
	name = 'Plex Subscene Movies'
	languages = [ Locale.Language.English ]
	primary_provider = True
	fallback_agent = False
	accepts_from = None
	contributes_to = None


	def search(self, results, media, lang, manual):
		uuid = String.UUID()
		results.Append(MetadataSearchResult(id = uuid, score = 100))

	def update(self, metadata, media, lang, force):
		for item in media.items:
            for part in item.parts:
                siList = getSubsForPart(media.title, part.title)

                for si in siList:
                    part.subtitles[Locale.Language.Match(si.lang)][si.url] = Proxy.Media(si.sub, ext=si.ext)

        del(mediaCopies[metadata.id])


class PlexSubsceneTVShows (Agent.TV_Shows):
	name = 'Plex Subscene TV Shows'
	languages = [ Locale.Language.English ]
	primary_provider = True
	fallback_agent = False
	accepts_from = None
	contributes_to = None


	def search(self, results, media, lang, manual):
		results.Append(MetadataSearchResult(id = 'null', score = 100))

	def update(self, metadata, media, lang, force):
		pass
'''

# plugin entry point
def Start():
	# initialize the plugin
	pass