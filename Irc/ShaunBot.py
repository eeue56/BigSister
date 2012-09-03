from bot import IrcBot
from time import sleep
import socket

import httplib2
import sys

from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import AccessTokenRefreshError
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.tools import run

class ShaunBot(IrcBot):


    def __init__(self, host, port, nick, ident, realname, owner):
        IrcBot.__init__(self, host, port, nick, ident, realname, owner)
        self.register_command(self.move_to_channel, 'move_to')
        self.register_command(self.list_users, 'users')
        self.register_command(self.search_for, 'search_for')
        self.register_command(self.access_cal, 'cal')

    def list_users(self, *args, **kwargs):
        self.send('NAMES ' + kwargs['target_channel'])
        userlist = self.read().split(':')[2].split()

        for item in userlist:
            self.send('PRIVMSG %s :%s\n' % (kwargs['target_channel'], item))
        return '--End of User List--'
        
    def move_to_channel(self, newchan, *args, **kwargs):
        self.send('JOIN '+ newchan)

    def search_for(self, searchterm, *args, **kwargs):
        return 'https://www.google.co.uk/search?q='+searchterm

        def access_cal(self, *args, **kwargs):
        client_id = ''
        client_secret = ''
        scope = 'https://www.googleapis.com/auth/calendar'
        flow = OAuth2WebServerFlow(client_id, client_secret, scope)

        storage = Storage('credentials.dat')
        credentials = storage.get()
        if credentials is None or credentials.invalid:
            credentials = run(flow, storage)

        http = httplib2.Http()
        http = credentials.authorize(http)

        service = build('calendar', 'v3', http=http)

        try:
            request = service.events().list(calendarId='primary')
            while request != None:
                response = request.execute()
                return '\n'.join(event.get('summary')+ ' on '+ event.get('start')[u'date'] for event in response.get('items',[]))
                request = service.events().list_next(request, response)

        except AccessTokenRefreshError:
            print ('The credentials have been revoked or expired, please re-run'
                    'the application to re-authorise')

if __name__ == '__main__':
    bot = ShaunBot('irc.freenode.org', 6667, 'NoahSucksBot', 'Problem', 'Peehead', 'Nob')
    bot.connect()
    bot.connect_to_channel('##dme')

    bot.register_command(lambda *args, **kwargs: 'Hi ' + kwargs['user'], 'hi')

    with open('errors.log', 'w+') as errors:
        while True:
            try:
                bot.process_next_line()
            except socket.error as e:
                errors.write(e.message)
                break 
            sleep(0.5)