import random

class eightball:
    def __init__(self, irc):
        self.registered_events = { '.8ball' : self.eightball }
        string_fh = open('8ball.strings','r')
        self.strings =[]
        for line in string_fh:
            self.strings.append(line)
        self.irc = irc
    def get_events(self):
        return self.registered_events
    def eightball(self, channel, arguments, user):
        string = random.choice(self.strings)
        if user == 'tmarkovich':
        	self.irc.msg(channel, "fuck off, thomas")
        	return
        self.irc.msg(channel, string )
