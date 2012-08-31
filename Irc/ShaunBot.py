from bot import IrcBot
from time import sleep

class ShaunBot(IrcBot):


    def __init__(self, host, port, nick, ident, realname, owner):
        IrcBot.__init__(self, host, port, nick, ident, realname, owner)
        self.register_command(self.move_to_channel, 'move_to')
        self.register_command(self.list_users, 'users')

    def list_users(self, *args, **kwargs):
        self.send('NAMES ' + kwargs['target_channel'])
        return self.read().split(':')[2]

    def move_to_channel(self, newchan, *args, **kwargs):
        self.send('JOIN '+ newchan)

if __name__ == '__main__':
    bot = ShaunBot('irc.freenode.org', 6667, 'NoahSucksBot', 'Problem', 'Peehead', 'Nob')
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