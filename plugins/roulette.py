import random

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
