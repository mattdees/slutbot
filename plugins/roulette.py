
import random

from sb_plugins import plugin_base


class roulette(plugin_base):
    def __init__(self, irc):
        self.registered_events = {'.roulette': self.roulette}
        self.in_session = False
        self.irc = irc

    def roulette(self, sbmessage):
        user = sbmessage.username
        if self.in_session is False:
            sbmessage.respond(user + ' has started a game of russian roulette, type \'.roulette\' to pull the trigger')
            self.in_session = True
        if (int(random.random() * 6) == 5):
            sbmessage.respond(user + " has pulled the trigger...")
            self.irc.kick(sbmessage.channel, user, "Bang!")
            self.in_session = False
            return
        else:
            sbmessage.respond(user + " has pulled the trigger... click!")
