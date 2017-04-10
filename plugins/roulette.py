
import random

from sb_plugins import plugin_base


class roulette(plugin_base):
    def __init__(self, irc):
        self.registered_events = {'.roulette': self.roulette}
        self.chamber = -1  # where the bullet is in the chamber
        self.current = 0   # The chamber being fired
        self.irc = irc

    def roulette(self, sbmessage):
        user = sbmessage.username
        if self.chamber == -1:
            sbmessage.respond(user + ' loaded the gun for russian roulette, type \'.roulette\' to pull the trigger')
            self.chamber = random.randint(0, 6)
        else:
            sbmessage.respond(user + " has pulled the trigger...")

        if self.chamber == self.current:
            self.irc.kick(
                sbmessage.channel,
                sbmessage.username,
                "These violent delights have violent ends"
            )
            self.chamber = -1
            self.current = 0

        self.current += 1
