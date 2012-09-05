from big.irc.bot import IrcBot
from time import sleep
import socket

import smtplib
import string

import httplib2
import sys

from big.database.sql import MembersDatabase

from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import AccessTokenRefreshError
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.tools import run

class ShaunBot(IrcBot):


    def __init__(self, host, port, nick, ident, realname, owner, database):
        IrcBot.__init__(self, host, port, nick, ident, realname, owner)
        self.database = database
        self.register_command(self.move_to_channel, 'move_to')
        self.register_command(self.list_users, 'users')
        self.register_command(self.search_for, 'search_for')
        self.register_command(self.access_cal, 'cal')
        self.register_command(self.send_mail, 'mail')
        self.register_command(self.add_new_member, 'add_member')
        self.register_command(self.print_members, 'print_members')
        self.register_command(self.remove_member, 'remove_member')
        self.register_command(self.validate, 'validate')

    def list_users(self, *args, **kwargs):
        self.send('NAMES ' + kwargs['target_channel'])
        userlist = self.read().split(':')[2].split()

        for item in userlist:
            return 'Online Members: ' + ', '.join(userlist)
        
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

    def send_mail(self, message, *args, **kwargs):
        '''using smtplib to email BigSister notifications
           syntax ~mail <recipient> - <message>'''

        if '-' in message:
            recipient, message = message.split('-')
            '''convert to list in case of more than one recipient'''
            recipient = recipient.split(',')

        else:
            return 'Error - Syntax: mail <recipient address> - <message>'
        
        smtp_server = smtplib.SMTP('smtp.gmail.com:587')
        username = 'BigSister1379@gmail.com'
        password = ''
        sub = 'Big Sister Notification'
        body = '\r\n'.join(('From: BigSister',
                            'To: {}'.format(', '.join(recipient)),
                            'Subject: {}'.format(sub),
                            '',
                            message))

        try:
            smtp_server.ehlo()
            smtp_server.starttls()
            smtp_server.login(username, password)
            smtp_server.sendmail('BigSister', recipient, body)
            smtp_server.quit()
            return 'Mail Sent'

        except smtplib.SMTPException, error:
            return 'Unable to Send Mail: {}.'.format(str(error))

    def add_new_member(self, member_details, *args, **kwargs):
        '''adding a new member to the database if it does not already exist'''
        if ',' in member_details:
            bangor_id, surname, forename, email, mobile, school, study_year = (detail.strip() for detail in member_details.split(','))
            if not self.database.validate_user(bangor_id):
                self.database.add_member(bangor_id, surname, forename, email, mobile, school, study_year)
                return 'Member Added'
            else:
                return 'Member {} already exists'.format(bangor_id)

    def print_members(self, *args, **kwargs):
        return "\n".join(', '.join(map(str,member)) for member in self.database.print_members())

    def remove_member(self, bangor_id, *args, **kwargs):
        '''remove member from database if it exists'''
        if not self.database.validate_user(bangor_id):
            return 'Member {} does not exist'.format(bangor_id)
        else:
            self.database.remove_member(bangor_id)
            return 'Member Removed'

    def validate(self, bangor_id, *args, **kwargs):
        '''checks to see if member is in database or not'''
        if not self.database.validate_user(bangor_id):
            return 'Member not Found'
        else:
            name = ' '.join(self.database.return_name(bangor_id))
            print name
            return '{} is already a Member'.format(name)

if __name__ == '__main__':
    database = MembersDatabase('members.db')
    database._connect_to_db()

    bot = ShaunBot('irc.freenode.org', 6667, 'NoahSucksBot', 'Problem', 'Peehead', 'Nob', database)
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
