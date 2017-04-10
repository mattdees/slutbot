from __future__ import print_function

import re
import urllib2

import BeautifulSoup

from sb_plugins import plugin_base


class url_handler(plugin_base):
    def __init__(self, irc):
        self.irc = irc
        self.url_regex = re.compile(r"(https?://[^ ]+)")

    def messagehandler(self, sbmessage):
        for url in self.url_regex.findall(sbmessage.msg):
            title = self.url_title(url)
            sbmessage.respond(title.encode('latin-1'))

    def url_title(self, url):
        if url.startswith('http') is False:
            url = 'http://' + url
        try:
            ul = urllib2.urlopen(url)
            bs = BeautifulSoup.BeautifulSoup(ul.read(4096))
            title = bs.html.head.title.contents
        except (AttributeError, ValueError):
            return False
        return title[0]
