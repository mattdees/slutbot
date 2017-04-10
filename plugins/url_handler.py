
import urllib2

import BeautifulSoup

from sb_plugins import plugin_base


class url_handler(plugin_base):
    def __init__(self, irc):
        self.registered_events = {
            '.t': self.get_http_title,
            '.gettitle': self.get_http_title
        }
        self.irc = irc

    def messagehandler(self, sbmessage):
        sbmessage.respond('lol THIS WORKS OR SOME SHIT')

    def get_http_title(self, sbmessage):
        url = sbmessage.arguments
        title = self.url_title(url)
        if title:
            sbmessage.respond(url + ': ' + title.encode('latin-1'))
        else:
            sbmessage.respond('Invalid url or url does not contain title tag')

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
