#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function

import pprint


class plugin_base(object):
    registered_events = {}

    def __init__(self, irc):
        self.irc = irc

    def get_events(self):
        pp = pprint.PrettyPrinter(indent=4)
        print(self.__class__.__name__)
        pp.pprint(self.registered_events)
        return self.registered_events
