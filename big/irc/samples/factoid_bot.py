from big.irc.bot import IrcBot
from big.irc.misc import crop_string

import sqlite3

from time import sleep

import socket

class FactoidBot(IrcBot):


    def __init__(self, host, port, nick, ident, realname, owner):
        IrcBot.__init__(self, host, port, nick, ident, realname, owner)
        self.register_command(self.create_factoid, 'addfact')
        self.register_command(self.factoid_history, 'history')
        self.register_command(self.get_factoids_by, 'factby')

        self._conn = sqlite3.connect('factoids.db')
        self.c = self._conn.cursor()
        self._create_table()

    def is_directed_at_me(self, line):
        ''' Checks if command is directed at bot '''
        line = crop_string(line, '@')

        return '!' in line or IrcBot.is_directed_at_me(self, line)

    def _create_table(self):
        c = self._conn.cursor()

        c.execute('''CREATE TABLE IF NOT EXISTS factoids
                     (factor TEXT, factoid TEXT, insert_time DATE PRIMARY KEY, creator TEXT, uses INTEGER)''')

        self._conn.commit()
        c.close()

    def create_factoid(self, message, *args, **kwargs):
        ''' Creates a factoid - split factor and factoid by a | '''
        parts = message.split('|')
        factor = parts[0].strip()
        factoid = ' '.join(parts[1:])

        self._write_factoid(factor, factoid, kwargs['user'])
        return 'Done'

    def _write_factoid(self, factor, factoid, user):
        ''' Writes a new factoid to the db '''
        c = self._conn.cursor()

        c.execute('''INSERT INTO factoids 
                     VALUES (?, ?, datetime("NOW"), ?, 0)''', 
                    (factor, factoid, user))

        self._conn.commit()
        c.close()

    def _update_factoid(self, factor, insert_time):
        ''' Updates the factor use count '''

        self.c.execute('''UPDATE factoids
                          SET uses = uses + 1
                          WHERE factor=? AND insert_time=?
                          ''',
                          (factor, insert_time))
        self._conn.commit()

    def _find_factoid(self, factor):
        ''' Finds the latest factoid for a given factor '''
        
        self.c.execute('''SELECT factoid, insert_time
                          FROM factoids 
                          WHERE factor=? 
                          ORDER BY datetime(insert_time) DESC
                          LIMIT 1''',
                        (factor,))

        result = self.c.fetchall()

        if result is None:
            return 'Not found!'

        result = result[0]

        self._update_factoid(factor, result[1])
        
        return ''.join(result[0])

    def factoid_history(self, message, *args, **kwargs):
        ''' Returns the history of the factoid '''
        
        if len(message.strip()) < 1:
            return 'Need to enter a factor to be found'

        factor = message.split()[0]


        self.c.execute('''SELECT factoid, creator, uses
                          FROM factoids 
                          WHERE factor=? 
                          ORDER BY datetime(insert_time) DESC''', 
                        (factor,))

        results = self.c.fetchall()

        if results is None:
            return 'Factor not found!'

        return '\n'.join('{} : (Creator: {}, Uses: {})'.format(*result) for result in results)

    def get_factoids_by(self, message, *args, **kwargs):
        ''' Returns all the factoids by a certain user - if no name is provided then uses caller's'''

        if len(message.strip()) < 1:
            username = kwargs['user']
        else:
            username = message.split()[0]

        self.c.execute('''SELECT factoid, uses
                          FROM factoids
                          WHERE creator=?
                          ORDER BY datetime(insert_time) DESC''',
                        (username,))

        results = self.c.fetchall()

        if results is None:
            return 'None! What a loser :/'

        return '\n'.join('{}, used {} times'.format(*result) for result in results)


    def process_directed_line(self, line_parts):
        ''' Processes a line directed at the bot '''

        user, target_channel, message = (part.strip() for part in line_parts.groups())

        if self.channels[target_channel]['silenced'] and 'speak' not in message:
            return
                        
        if '~' in message:
            message = crop_string(message, '~')
        elif ':' in message and self.nick.lower() in message.lower():
            message = crop_string(message, ':')
        elif '!' in message:
            message = crop_string(message, '!')
            self._send_messages(target_channel, self._find_factoid(message))
            return
        else:
            return

        if target_channel == self.nick:
            target_channel = user
        
        self.process_command(user, target_channel, message)

    def _close(self):
        self._conn.close()


if __name__ == '__main__':
    

    bot = FactoidBot('irc.freenode.org', 6667, 'SuxBot', 'SuxBot', 'SuxBot', 'SuxBot')
    bot.connect()
    bot.connect_to_channel('##linsuxchat')

    bot.register_command(lambda *args, **kwargs: 'Hi ' + kwargs['user'], 'hi')
    bot.register_command(lambda *args, **kwargs: repr(bot), 'repr')

    with open('errors.log', 'w+') as errors:
        while True:
            try:
                bot.process_next_line()
            except socket.error as e:
                errors.write(e.message)
                bot._close()
                break 
