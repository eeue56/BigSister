from bot import IrcBot
from time import sleep

class InsultBot(IrcBot):


    def __init__(self, host, port, nick, ident, realname, owner):
        IrcBot.__init__(self, host, port, nick, ident, realname, owner)
        self.register_command(self.piss_off_twat, 'piss_on')

    def piss_off_twat(self, message, *args, **kwargs):
        return 'Piss off {}, you fucking shithead dogballs'.format(message.split()[0])

if __name__ == '__main__':
    bot = InsultBot('irc.freenode.org', 6667, 'ShaunSmellsBot', 'Problem', 'Peehead', 'Nob')
    bot.connect()
    bot.connect_to_channel('##dme')

    bot.register_command(lambda *args, **kwargs: 'Hi ' + kwargs['user'], 'hi')

    with open('errors.log', 'w+') as errors:
        while True:
            try:
                bot.read_and_process()
            except socket.error as e:
                errors.write(e.message)
                break 
            sleep(0.5)
