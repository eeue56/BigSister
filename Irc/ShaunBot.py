from bot import IrcBot
from time import sleep
import socket

import smtplib

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
        self.register_command(self.send_mail, 'mail')

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

    def _get_start_date(self, start, *args, **kwargs):
        '''checks whether key is date or dateTime'''
        if u'date' in start:
            return start[u'date']
        elif u'dateTime' in start:
            return start[u'dateTime'].split('T')[0]
        else :
            return ''

    def access_cal(self, *args, **kwargs):
        '''use google cal API to return events'''
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
                eventlist= []

                for event in response.get('items',[]):
                    eventlist.append(event.get('summary') + ' on '+ self._get_start_date(event.get('start')))
                return '\n'.join(eventlist)
                request = service.events().list_next(request, response)
                eventlist = []

        except AccessTokenRefreshError:
            print ('The credentials have been revoked or expired, please re-run'
                    'the application to re-authorise')

    def send_mail(self, receiver, *args, **kwargs):
        sender = 'BigSister1379@gmail.com'
        sub = 'Big Sister Notification'
        message = ''

        try:
            smtp_server = smtplib.SMTP('smtp.gmail.com:587')
            username = 'BigSister1379@gmail.com'
            password = ''
            smtp_server.ehlo()
            smtp_server.starttls()
            smtp_server.login(username, password)
            smtp_server.sendmail(sender, receiver, message)
            smtp_server.quit()
            return 'Mail Sent'
        except smtplib.SMTPException, error:
            return 'Unable to Send Mail: %s.' % str(error)


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