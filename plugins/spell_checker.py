import enchant

from sb_plugins import plugin_base


class spell_checker(plugin_base):
    def __init__(self, irc):
        self.registered_eventss = {
            '.spellcheck': self.spellcheck,
            '.sc': self.spellcheck
        }
        self.enchant = enchant.Dict('en-US')
        self.irc = irc

    def spellcheck(self, channel, arguments, user):
        if (self.enchant.check(arguments)):
            self.irc.msg(channel, 'Spelling of ' + arguments + ' is correct')
        else:
            suggestions = self.enchant.suggest(arguments)[:5]
            self.irc.msg(
                channel,
                'Suggested Spellings: ' + ', '.join(suggestions)
            )
