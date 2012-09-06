'''module to handle google calendar intergration'''

from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import AccessTokenRefreshError
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.tools import run

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
		if self.credentials is None or credentials.invalid:
			self.credentials = run(self.flow, storage)

	def return_events():
		http = httplib2.Http()
		http = credentials.authorize(http)
		service = build('calendar', 'v3', http=http)

		try:
			request = service.events().list(calendarId='primary')

			while request != None:
				response = request.execute()
				eventlist = []

				for event in response.get('items',[]):
					eventlist.append(event.get('summary') + ' on ' + self._get_start_date(event.get('start')))
				
				return eventlist
				request = service.events().list_next(request, response)
				eventlist = []

		except AccessTokenRefreshError:
			print ('The credentials have been revoked or expired, please re-run'
					'the application to re-authorise')






