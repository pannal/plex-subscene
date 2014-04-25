#Plex Theme Music
THEME_URL = 'http://tvthemes.plexapp.com/%s.mp3'

def Start():
  HTTP.CacheTime = CACHE_1DAY
  Log("Subscene plugin started!!!")
 

class PlexSubsceneAgentMovies(Agent.Movies):
    name = 'Plex Subscene Movies'
    languages = [Locale.Language.NoLanguage]
    primary_provider = False
    contributes_to = ['com.plexapp.agents.imdb']

    def search(self, results, media, lang):
      results.Append(
        MetadataSearchResult(
          id    = media.primary_metadata.id,
          score = 100
        )    
      )

    def update(self, metadata, media, lang):
        pass

 
class PlexSubsceneAgentTVShows(Agent.TV_Shows):
    name = 'Plex Subscene TV Shows'
    languages = [Locale.Language.NoLanguage]
    primary_provider = False
    contributes_to = ['com.plexapp.agents.thetvdb']

    def search(self, results, media, lang):
      results.Append(
        MetadataSearchResult(
          id    = media.primary_metadata.id,
          score = 100
        )    
      )

    def update(self, metadata, media, lang):
        pass
