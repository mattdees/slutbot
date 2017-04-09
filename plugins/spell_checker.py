import enchant


class spell_checker(object):
    def __init__(self, irc):
        self.registered_events = {'.spellcheck': self.spellcheck, '.sc': self.spellcheck}
        self.enchant = enchant.Dict('en-US')
        self.irc = irc

    def get_events(self):
        return self.registered_events

    def spellcheck(self, channel, arguments, user):
        if (self.enchant.check(arguments)):
            self.irc.msg(channel, 'Spelling of ' + arguments + ' is correct')
        else:
            suggestions = self.enchant.suggest(arguments)[:5]
            self.irc.msg(channel, 'Suggested Spellings: ' + ', '.join(suggestions))
