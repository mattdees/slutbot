import urllib2
import BeautifulSoup


class url_handler:
    def __init__(self):
        self.registered_events = { '.t' : self.get_http_title, '.gettitle': self.get_http_title }
    def get_events(self):
        return self.registered_events
    def get_http_title(self, irc, channel, arguments, user):
        title = self.url_title( arguments )
        if title:
            irc.msg(channel, arguments + ': ' + title.encode('latin-1'))
        else:
            irc.msg(channel, 'Invalid url or url does not contain title tag')
    def url_title(self, url):
        if url.startswith('http') == False:
            url = 'http://' + url
        try:
            ul = urllib2.urlopen(url)
            bs = BeautifulSoup.BeautifulSoup(ul.read(4096))
            title = bs.html.head.title.contents
        except (AttributeError, ValueError):
            return False;
        return title[0]