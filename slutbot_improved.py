#!/usr/bin/python

# twisted imports
from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from twisted.python import log

# system imports
import time, sys
import yaml

sys.path.append('plugins')

class SlutBot(irc.IRCClient):
    nickname = "slutbot"
    
    def __init__(self):
        pass
    def load_plugins(self):
        plugins = self.factory.server_config['plugins']
        self.triggers = {}
        for plugin in plugins:
            try:
                plugin_module = __import__(plugin)
                plugin_obj = getattr(plugin_module, plugin)
                plugin_obj = plugin_obj(self)
                plugin_events = plugin_obj.get_events()
                self.triggers.update( plugin_events.items() )   
            except TypeError as e:
                print "Something terrible happened: " + e.message


    def connectionMade(self):
        irc.IRCClient.connectionMade(self)
        sys.stdout.write("[connected at %s]" % 
                        time.asctime(time.localtime(time.time())))

    def connectionLost(self, reason):
        sys.stdout.write("[disconnected at %s]" % 
                        time.asctime(time.localtime(time.time())))

    def signedOn(self):
        print "connection from", self.transport.getPeer()
        self.load_plugins()
        self.setNick(self.factory.server_config['nickname'])
        channel_list = self.factory.server_config['channels']
        for channel in channel_list.keys():
            self.join( channel, channel_list[channel] )

    def joined(self, channel):
        """This will get called when the bot joins the channel."""
        sys.stdout.write("[I have joined %s]" % channel)

    def privmsg(self, user, channel, msg):
        user = user.split('!', 1)[0]
        
        if msg.find(' '):
            [ command, null, arguments ] = msg.partition(' ')
            for trigger in self.triggers.keys():
                if command == trigger:
                    self.triggers[trigger]( channel, arguments, user)
    def action(self, user, channel, msg):
        user = user.split('!', 1)[0]
        sys.stdout.write("* %s %s" % (user, msg))
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

    def __init__(self, server_config ):
        self.server_config = server_config

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
        server_config = servers[server]
        channel_list = server_config['channels']
        port = server_config['port']
        factory = SlutBotFactory(server_config)
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
