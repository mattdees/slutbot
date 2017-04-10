#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function

import sys
import time

from twisted.internet import protocol
from twisted.internet import reactor
from twisted.python import log
from twisted.words.protocols import irc

import yaml


sys.path.append('plugins')
sys.path.append('lib')


class SlutBot(irc.IRCClient):

    nickname = 'slutbot'

    def __init__(self):
        pass

    def load_plugins(self):
        plugins = self.factory.server_config['plugins']
        self.triggers = {}
        self.messagehandlers = []
        for plugin in plugins:
            try:
                plugin_config = self.get_plugin_config(plugin)
                plugin_module = __import__(plugin)
                plugin_obj = getattr(plugin_module, plugin)
                plugin_obj = plugin_obj(self, plugin_config)
                plugin_events = plugin_obj.get_events()
                self.triggers.update(plugin_events.items())
                if hasattr(plugin_obj, 'messagehandler'):
                    self.messagehandlers.append(plugin_obj)
            except TypeError as e:
                print('Something terrible happened: ' + e.message)

    def get_plugin_config(self, plugin):
        plugin_config = None
        if plugin in self.factory.server_config['plugin_config']:
            plugin_config = self.factory.server_config['plugin_config'][plugin]
        return plugin_config

    def connectionMade(self):
        irc.IRCClient.connectionMade(self)
        sys.stdout.write('[connected at %s]'
                         % time.asctime(time.localtime(time.time())))

    def connectionLost(self, reason):
        sys.stdout.write('[disconnected at %s]'
                         % time.asctime(time.localtime(time.time())))

    def signedOn(self):
        print('connection from', self.transport.getPeer())
        self.load_plugins()
        self.setNick(self.factory.server_config['nickname'])
        channel_list = self.factory.server_config['channels']
        for channel in channel_list.keys():
            self.join(channel, channel_list[channel])

    def joined(self, channel):
        """This will get called when the bot joins the channel."""

        sys.stdout.write('[I have joined %s]' % channel)

    def privmsg(self, user, channel, msg):

        sbmessage = SBMessage(self, channel, msg, user)
        user = sbmessage.username
        print(self.messagehandlers)

        for obj in self.messagehandlers:
            obj.messagehandler(sbmessage)

        if sbmessage.command:
            if sbmessage.command in self.triggers.keys():
                self.triggers[sbmessage.command](sbmessage)

    def action(self, user, channel, msg):
        user = user.split('!', 1)[0]
        sys.stdout.write('* %s %s' % (user, msg))

    def irc_NICK(self, prefix, params):
        """Called when an IRC user changes their nickname."""

        old_nick = prefix.split('!')[0]
        new_nick = params[0]
        sys.stdout.write("%s is now known as %s\n" % (old_nick, new_nick))

    # For fun, override the method that determines how a nickname is changed on
    # collisions. The default method appends an underscore.

    def alterCollidedNick(self, nickname):
        return nickname + '^'


class SlutBotFactory(protocol.ClientFactory):

    # the class of the protocol to build when new connection is made

    protocol = SlutBot

    def __init__(self, server_config):
        self.server_config = server_config

    def clientConnectionLost(self, connector, reason):
        """If we get disconnected, reconnect to server."""

        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print('connection failed:', reason)
        reactor.stop()


class SBMessage(object):
    """Base Class for different message types"""
    username = ''
    hostname = ''
    name = ''

    def __init__(self, irc, channel, msg, user=None):
        if user is not None:
            (self.username, self.hostname) = user.split('!', 2)
            (self.name, self.hostname) = self.hostname.split('@', 2)
        if msg.find('.') == 0:
            # If this looks like a command (starts with .) save the parts off
            try:
                (self.command, self.arguments) = msg.split(' ', 2)
            except ValueError:
                self.command = msg
                self.arguments = False
        else:
            self.command = False
            self.arguments = False
        self.channel = channel
        self.msg = msg
        self.irc = irc

    def respond(self, message):
        self.irc.msg(self.channel, message)

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
