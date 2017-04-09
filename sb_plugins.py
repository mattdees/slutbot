#!/usr/bin/python
# -*- coding: utf-8 -*-


class plugin_base(object):
    def __init__(self, irc):
        self.registered_events = {}

    def get_events(self):
        return self.registered_events
