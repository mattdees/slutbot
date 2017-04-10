import enchant

from sb_plugins import plugin_base


class spell_checker(plugin_base):
    def __init__(self, irc):
        self.registered_events = {
            '.spellcheck': self.spellcheck,
            '.sc': self.spellcheck
        }
        self.enchant = enchant.Dict('en-US')
        self.irc = irc

    def spellcheck(self, sbmessage):
        arguments = sbmessage.arguments
        if (self.enchant.check(arguments)):
            sbmessage.respond('Spelling of ' + arguments + ' is correct')
        else:
            suggestions = self.enchant.suggest(arguments)[:5]
            sbmessage.respond('Suggested Spellings: ' + ', '.join(suggestions))
