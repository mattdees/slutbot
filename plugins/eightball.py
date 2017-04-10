#!/usr/bin/python
# -*- coding: utf-8 -*-
import random

from sb_plugins import plugin_base


class eightball(plugin_base):
    def __init__(self, irc):
        self.registered_events = {'.8ball': self.eightball}
        string_fh = open('8ball.strings', 'r')
        self.strings = []
        for line in string_fh:
            self.strings.append(line)
        self.irc = irc

    def eightball(self, sbmessage):
        string = random.choice(self.strings)
        if sbmessage.user == 'tmarkovich':
            sbmessage.respond('fuck off, thomas')
            return
        sbmessage.respond(string)
