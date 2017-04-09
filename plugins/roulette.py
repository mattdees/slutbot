from sb_plugins import plugin_base
import random


class roulette(plugin_base):
    def __init__(self, irc):
        self.registered_events = {'.roulette': self.roulette}
        self.in_session = False
        self.irc = irc

    def roulette(self, channel, arguments, user):
        if self.in_session is False:
            self.irc.msg(channel, user + ' has started a game of russian roulette, type \'.roulette\' to pull the trigger')
            self.in_session = True
        if (int(random.random() * 6) == 5):
            self.irc.msg(channel, user + " has pulled the trigger...")
            self.irc.kick(channel, user, "Bang!")
            self.in_session = False
            return
        else:
            self.irc.msg(channel, user + " has pulled the trigger... click!")
