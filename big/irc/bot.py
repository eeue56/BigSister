import socket
import re
import sys
from time import sleep
from big.irc.misc import crop_string

class IrcBot(object):


    def __init__(self, host, port, nick, ident, realname, owner, registered=None):
        self.host = host
        self.port = port
        self.nick = nick
        self.name = '{id} {host} bal :{realname}'.format(id=ident, host=host, realname=realname)
        self.owner = owner
        self.registered = registered

        self.channels = {}

        self.actions = {
                        'quit' : self.quit,
                        'silence' : self.silence,
                        'speak' : self.speak,
                        '!!' : self.last_command
                        }

        self.commands = []
        self._to_join = []

        self.identified = False


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
        self._register_channel(self.nick)

    def register(self, password):
        ''' Identifies with NickServ using the constant password'''
        self._send_message('NickServ', 'identify {password}'.format(password=password))
        self.read()

    def register_command(self, func, key):
        ''' Registers a command as an action '''
        self.actions[key] = func
        
    def silence(self, *args, **kwargs):
        ''' Silences the bot '''
        self.channels[kwargs['target_channel']]['silenced'] = True
        return 'Fine. I\'ll be quiet.'

    def speak (self, *args, **kwargs):
        ''' Allows the bot to speak again '''
        self.channels[kwargs['target_channel']]['silenced'] = False
        return 'Hello you'

    def last_command(self, *args, **kwargs):
        ''' Passes args and kwargs to last used command and returns the response.
            Returns error message if no commands have been used before
            
        '''
        
        try:
            return self.commands[-1](*args, **kwargs)
        except IndexError:
            return 'Need to use a command before you can reuse it'

    def connect_to_channel(self, channel, *args, **kwargs):
        ''' Connects to an IRC on the current network
            
            channel - a given channel to join
        '''
        self.send('JOIN {}'.format(channel))
        self._register_channel(channel)
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

    def _break_message_down(self, message):
        length = 255
        parts = []
        message_length = len(message)
        words = message.split()
        current_part = []
        
        for word in words:
            if sum(len(x) for x in current_part) + len(word) < length:
                current_part.append(word)
            else:
                parts.append(' '.join(current_part))            
                current_part = [word]
        else:
            if current_part:
                parts.append(' '.join(current_part))
        return parts

    def _send_message(self, channel, message):
        self.send('PRIVMSG {} :{}'.format(channel, message))    
            
    def _send_messages(self, channel, messages):
        for message in messages.split('\n'):
            message = message.strip()
            if len(message) > 200:
                new_messages = self._break_message_down(message)
                for message_ in new_messages:
                    self._send_message(channel, message_.strip())
            elif message != '':
                self._send_message(channel, message)

    def _register_channel(self, channel):
        self.channels[channel] = {'silenced' : False}
            
    def is_directed_at_me(self, line):
        ''' Checks if command is directed at bot '''
        line = crop_string(line, '@')
        
        return self.nick.lower() in line.lower() or '~' in line

    def is_identified(self, line):

        if 'You are now identified' in line:
                return True
        return False

    def get_action(self, message):
        ''' Gets the action from the message and returns it if it is valid action'''
        if message.split()[0].strip() in self.actions:
            command, action = message.split()[0], self.actions[message.split()[0]]

            return command, action
        return None, None

    def read(self, amount=4096):
        ''' Wrapper for self.s.recv. Recieves data and strips it '''
        return self.s.recv(amount).strip()
    
    def send(self, text):
        ''' Send text to connected socket '''
        self.s.send(text.strip() + '\r\n')

    def _join_waiting_channels(self):
        for chan in self.to_join:
            self.connect_to_channel(chan)
        self.to_join = []

    def next_line(self):
        ''' Gets the next line from the socket '''
        return self.read()

    def _add_command_to_history(self, command,  action):
        ''' Adds command to history '''
        if command != '!!':
                self.commands.append(action)

    def _is_identify_check_needed(self):
        '''  Checks if identity check is needed '''
        return self.registered is not None and not self.identified
            

    def process_command(self, user, target_channel, message):
        ''' Processes a command '''

        command, action = self.get_action(message)

        if command is not None: 
            self._add_command_to_history(command, action)
            message = crop_string(message, command)
            message = message.strip()
            response = action(message, user=user,target_channel=target_channel)
            self._send_messages(target_channel, '{message}'.format(message=response))
        else:
            self._send_message(target_channel, '{user}: Piss off.'.format(user=user))  


    def process_directed_line(self, line_parts):
        ''' Processes a line directed at the bot '''

        user, target_channel, message = (part.strip() for part in line_parts.groups())

        if self.channels[target_channel]['silenced'] and 'speak' not in message:
            return
                        
        if '~' in message:
            message = crop_string(message, '~')
        elif ':' in message and self.nick.lower() in message.lower():
            message = crop_string(message, ':')
        else:
            return

        if target_channel == self.nick:
            target_channel = user
        
        self.process_command(user, target_channel, message)


    def process_next_line(self):
        ''' Reads a line from the socket and processes it, calling the right action and ponging '''
        line = self.next_line()

        if 'PING' in line:
            self.pong()
            return
        
        if self._is_identify_check_needed():

            self.identified = self.is_identified(line)

            if not self.identified:
                return
            else:
               self._join_waiting_channels()

        if self.is_directed_at_me(line):
            useful_parts = self.useful_parts(line)
            if useful_parts is not None:
                self.process_directed_line(useful_parts)
    

if __name__ == '__main__':
    bot = IrcBot('irc.freenode.org', 6667, 'ShaunSmellsBot', 'Problem', 'Peehead', 'Nob')

    bot.connect()
    bot.connect_to_channel('##dme')

    bot.register_command(lambda *args, **kwargs: 'Hi ' + kwargs['user'], 'hi')

    with open('errors.log', 'w+') as errors:
        while True:
            try:
                bot.process_next_line()
            except socket.error as e:
                errors.write(e.message)
                errors.write('\n')
                break 
            except Exception as e:
                errors.write(e.message)
                errors.write('\n')
                raise
            sleep(0.5)