'''module to handle google calendar intergration'''

from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import AccessTokenRefreshError
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.tools import run

import httplib2

class GoogleCalendar(object):

    def __init__(self):
        self.client_id = ''
        self.client_secret = ''
        self.scope = 'https://www.googleapis.com/auth/calendar'
        self.flow = OAuth2WebServerFlow(self.client_id, self.client_secret, self.scope)
        self.credentials = None

    def _store_credentials(self):
        storage = Storage('credentials.dat')
        self.credentials = storage.get()
        if self.credentials is None or self.credentials.invalid:
        	self.credentials = run(self.flow, storage)

    def _get_start_date(self, start):
        '''checks whether key is date or dateTime'''
        if 'date' in start:
            return start['date']
        elif 'dateTime' in start:
            return start['dateTime'].split('T')[0]
        else :
            return ''

    @staticmethod
    def return_events(self):
        print('1')
        http = httplib2.Http()
        http = self.credentials.authorize(http)
        service = build('calendar', 'v3', http=http)

        try:
            print('2')
            request = service.events().list(calendarId='primary')

            while request != None:
                response = request.execute()
                eventlist = []
                print('3')
                for event in response.get('items',[]):
                    eventlist.append(event.get('summary') + ' on ' + self._get_start_date(event.get('start')))

                return eventlist
                print('4')
                request = service.events().list_next(request, response)
                eventlist = []
                print('5')

        except AccessTokenRefreshError:
            print ('The credentials have been revoked or expired, please re-run'
                    'the application to re-authorise')

if __name__ == '__main__':
    gc = GoogleCalendar()
    gc._store_credentials()
    print(('\n'.join(gc.return_events())))

