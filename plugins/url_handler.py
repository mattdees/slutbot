import BeautifulSoup
from sb_plugins import plugin_base
import urllib2


class url_handler(plugin_base):
    def __init__(self, irc):
        self.registered_events = {'.t': self.get_http_title, '.gettitle': self.get_http_title}
        self.irc = irc

    def get_http_title(self, channel, arguments, user):
        title = self.url_title(arguments)
        if title:
            self.irc.msg(channel, arguments + ': ' + title.encode('latin-1'))
        else:
            self.irc.msg(channel, 'Invalid url or url does not contain title tag')

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
