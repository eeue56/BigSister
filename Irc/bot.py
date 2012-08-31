import socket
import re
import sys
from misc import crop_string

class IrcBot(object):


    def __init__(self, host, port, nick, ident, realname, owner):
        self.host = host
        self.port = port
        self.nick = nick
        self.name = '{id} {host} bal :{realname}'.format(id=ident, host=host, realname=realname)
        self.owner = owner

        self.channels = {}

        self.actions = {}

        self.commands = []

    def connect(self):
        ''' Connects to IRC port given on creation and sets nick and 
            user names
        '''
        self.s = socket.socket()
        self.s.connect((self.host, self.port))
        self.send('NICK {}'.format(self.nick))
        self.read(1024)
        self.send('USER {}'.format(self.name))
        self.read(1024)

    def register(self):
        ''' Identifies with NickServ using the constant password'''
        self.send_message('NickServ', 'identify {password}'.format(password=PASSWORD))
        self.read()

    def register_command(self, func, key):
        ''' Registers a command as an action '''
        self.actions[key] = func
            
    def connect_to_channel(self, channel, *args, **kwargs):
        ''' Connects to an IRC on the current network
            
            channel - a given channel to join
        '''
        self.send('JOIN {}'.format(channel))
        return 'Done'

    def quit(self, *args, **kwargs):
        ''' Quits the network and calls sys.exit '''
        self.send('QUIT')
        sys.exit(0)
    
    def pong(self):
        '''Sends PONG to server'''
        self.send('PONG')
    
    def ping(self):
        ''' Pings the host '''
        self.send('PING {}'.format(self.host))

    def useful_parts(self, line):
        '''If a line is a PRIVMSG, it strips out the channel name, the username, and the message
            
            Return format - None if not PRIVMSG or no matches, else (<channel>,<username>,<message>)
        '''
        
        if 'PRIVMSG' in line:
            return re.search(':(.+)[!].+ PRIVMSG (.+) :(.+)', line)

    def send_message(self, channel, message):
        self.send('PRIVMSG {} :{}'.format(channel, message))    
            
    def send_messages(self, channel, messages):
        for message in messages.split('\n'):
            message = message.strip()
            if len(message) > 200:
                new_messages = self.break_message_down(message)
                for message_ in new_messages:
                    self.send_message(channel, message_.strip())
            elif message != '':
                self.send_message(channel, message)
            
    def is_directed_at_me(self, line):
        line = crop_string(line, '@')
        
        return self.nick.lower() in line.lower() or '~' in line

    def get_action(self, message):
    
        if message.split()[0].strip() in self.actions:
            command, action = message.split()[0], self.actions[message.split()[0]]
            
            if command != '!!':
                self.commands.append(action)
            return command, action
        return None, None

    def read(self, amount=4096):
        return self.s.recv(amount).strip()
    
    def send(self, text):
        self.s.send(text.strip() + '\r\n')

    def read_and_work(self):
        line = self.read()

        if 'PING' in line:
            self.pong()
            return

        if self.is_directed_at_me(line):
            useful_parts = self.useful_parts(line)

            if useful_parts is not None:
                user, target_channel, message = (part.strip() for part in useful_parts.groups())
                                
                if '~' in message:
                    message = crop_string(message, '~')
                elif ':' in message and self.nick.lower() in message.lower():
                    message = crop_string(message, ':')
                else:
                    return
    
                command, action = self.get_action(message)
                
                if target_channel == self.nick:
                    target_channel = user
                
                if command is not None: 
                    message = crop_string(message, command)
                    message = message.strip()
                    response = action(message, user=user,target_channel=target_channel)
                    self.send_messages(target_channel, '{message}'.format(message=response))
                else:
                    self.send_message(target_channel, '{user}: Piss off.'.format(user=user))  

if __name__ == '__main__':
    bot = IrcBot('irc.freenode.org', 6667, 'ShaunSmellsBot', 'Problem', 'Peehead', 'Nob')

    bot.connect()
    bot.connect_to_channel('##dme')

    bot.register_command(lambda *args, **kwargs: 'Hi ' + kwargs['user'], 'hi')

    while True:
        bot.read_and_work()