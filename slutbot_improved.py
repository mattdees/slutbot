#!/usr/bin/python

# twisted imports
from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from twisted.python import log

# system imports
import time, sys

# extension imports
import google
import pywapi
import urllib
import urllib2
import BeautifulSoup
import random
import re
import yaml

class url_handler:
    def __init__(self):
        self.registered_events = { '.t' : self.get_http_title, '.gettitle': self.get_http_title }
    def get_events(self):
        return self.registered_events
    def get_http_title(self, irc, channel, arguments, user):
        title = self.url_title( arguments )
        if title:
            irc.msg(channel, arguments + ': ' + title.encode('latin-1'))
        else:
            irc.msg(channel, 'Invalid url or url does not contain title tag')
    def url_title(self, url):
        if url.startswith('http') == False:
            url = 'http://' + url
        try:
            ul = urllib2.urlopen(url)
            bs = BeautifulSoup.BeautifulSoup(ul.read(4096))
            title = bs.html.head.title.contents
        except (AttributeError, ValueError):
            return False;
        return title[0]

class roulette:
    def __init__(self):
        self.registered_events = { '.roulette' : self.roulette }
        self.in_session = False
    def get_events(self):
        return self.registered_events
    def roulette(self, irc, channel, arguments, user):
        if self.in_session == False:
            irc.msg(channel, user + ' has started a game of russian roulette, type \'.roulette\' to pull the trigger')
            self.in_session = True
        if ( int(random.random() * 6) == 5 ):
            irc.msg(channel, user + " has pulled the trigger...")
            irc.kick(channel, user, "Bang!" )
            self.in_session = False
            return
        else:
            irc.msg(channel, user + " has pulled the trigger... click!")

class weather_check:
    def __init__(self):
        self.registered_events = {
            '.w':self.wunderground,
            '.pws':self.wu_pws,
        }
    def get_events(self):
        return self.registered_events
    def wunderground( self, irc, channel, arguments, user):
        res_xml = self.http_get_query( 'http://api.wunderground.com/auto/wui/geo/WXCurrentObXML/index.xml', { 'query':arguments } )
        parsed_res = BeautifulSoup.BeautifulStoneSoup( res_xml )
        res = parsed_res.current_observation.display_location.full.string + ' '
        res = self.parse_wunderground_respone( parsed_res, res )
        irc.msg(channel, res.encode('latin-1') )
    def wu_pws( self, irc, channel, arguments, user):
        stations = self.http_get_query( 'http://api.wunderground.com/auto/wui/geo/GeoLookupXML/index.xml', { 'query': arguments } )
        stations_parsed = BeautifulSoup.BeautifulStoneSoup( stations )
        station_id = stations_parsed.location.nearby_weather_stations.pws.station.id.string
        station_id = station_id.replace('<![CDATA[','')
        station_id = station_id.replace(']]>','')
        res_xml = self.http_get_query( 'http://api.wunderground.com/weatherstation/WXCurrentObXML.asp', { 'ID':station_id } )
        parsed_res = BeautifulSoup.BeautifulStoneSoup( res_xml )
        res = parsed_res.current_observation.location.full.string + ' '
        res = self.parse_wunderground_respone( parsed_res, res )
        irc.msg(channel, res.encode('latin-1') )
    
    def parse_wunderground_respone( self, data, response ):
        if len( data.current_observation.temperature_string.contents ) != 0:
            response += ' temp: ' + data.current_observation.temperature_string.string
            
        if len( data.current_observation.relative_humidity.contents ) != 0:
            response += ' humidity: ' + data.current_observation.relative_humidity.string
            
        if len( data.current_observation.wind_string.contents ) != 0:
            response += ' wind: ' + data.current_observation.wind_string.string
            
        if len( data.current_observation.windchill_string.contents) != 0:
            response += ' windchill: ' + data.current_observation.windchill_string.string
            
        if len( data.current_observation.pressure_string.contents ) != 0:
            response += ' pressure: ' + data.current_observation.pressure_string.string
            
        if len( data.current_observation.dewpoint_string.contents ) != 0:
            response += ' dewpoint: ' + data.current_observation.dewpoint_string.string
            
        if len( data.current_observation.station_id.contents ) != 0:
            response += ' station: ' + data.current_observation.station_id.string
            
        return response
        
    def http_get_query( self, url, arguments):
        # Build our query

        http_query = url + '?' + urllib.urlencode( arguments )
        #perform our query
        try:
            response = urllib2.urlopen( http_query )
        except (URLError, HTTPError):
            #error if our query has issues
            print "Error while retrieving http data for " + http_query
            return False
        
        #return the data contained within the http query
        return response.read()

class SlutBot(irc.IRCClient):
    """A logging IRC bot."""
    
    nickname = "slutbot"
    
    def __init__(self):
        plugins = [url_handler(), roulette(), weather_check()]
        self.triggers = {}
        for plugin in plugins:
            plugin_events = plugin.get_events()
            self.triggers.update( plugin_events.items() )   

        print "Plugins loaded: " + ' '.join(self.triggers.keys())

    def connectionMade(self):
        irc.IRCClient.connectionMade(self)
        sys.stdout.write("[connected at %s]" % 
                        time.asctime(time.localtime(time.time())))

    def connectionLost(self, reason):
        sys.stdout.write("[disconnected at %s]" % 
                        time.asctime(time.localtime(time.time())))

    def signedOn(self):
        print "connection from", self.transport.getPeer()
        for channel in self.factory.channels.keys():
            self.join( channel, self.factory.channels[channel] )

    def joined(self, channel):
        """This will get called when the bot joins the channel."""
        sys.stdout.write("[I have joined %s]" % channel)

    def privmsg(self, user, channel, msg):
        user = user.split('!', 1)[0]
        
        if msg.find(' '):
            [ command, null, arguments ] = msg.partition(' ')
            for trigger in self.triggers.keys():
                if command == trigger:
                    self.triggers[trigger](self, channel, arguments, user)
    def action(self, user, channel, msg):
        """This will get called when the bot sees someone do an action."""
        user = user.split('!', 1)[0]
        sys.stdout.write("* %s %s" % (user, msg))

    # irc callbacks

    def irc_NICK(self, prefix, params):
        """Called when an IRC user changes their nickname."""
        old_nick = prefix.split('!')[0]
        new_nick = params[0]
        sys.stdout.write("%s is now known as %s" % (old_nick, new_nick))


    # For fun, override the method that determines how a nickname is changed on
    # collisions. The default method appends an underscore.
    def alterCollidedNick(self, nickname):
        return nickname + '^'

    

class SlutBotFactory(protocol.ClientFactory):
    # the class of the protocol to build when new connection is made
    protocol = SlutBot

    def __init__(self, channel_list ):
        self.channels = channel_list

    def clientConnectionLost(self, connector, reason):
        """If we get disconnected, reconnect to server."""
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print "connection failed:", reason
        reactor.stop()


if __name__ == '__main__':
    log.startLogging(sys.stdout)
    
    config_fh = open('servers.yaml', 'r')
    servers = yaml.load(config_fh)

    for server in servers.keys():
        channel_list = servers[server]['channels']
        port = servers[server]['port']
        factory = SlutBotFactory(channel_list)
        reactor.connectTCP(server, port, factory)

    reactor.run()

# this expects to be run in a directory containing a file called
# servers.yamls, this file should have the following structure

#    {
#        'irc.someserver.net': {
#            'port': 6667,
#            'channels':{
#                '#geckbot':False,    # connect to an unkeyed channel
#                '#blah':False,       # connect to some other channel
#            }
#        },
#        'irc.someotherserver.net': {
#            'port': 6667,
#            'channels':{
#                '#reddit-nowhere':'onepersonliveshere',  # connect to a key channel
#            }
#        }
#    }
