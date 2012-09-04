'''module to handle SQL database intergration'''

import sqlite3

class MembersDatabase(object):

	def __init__(self, database_name):
		self.database_name = database_name
		self.conn = None

	def _connect_to_db():
		conn = sqlite3.connect(self.database_name)

	def create_table():
		try:
			c = conn.cursor()
			c.execute('''CREATE TABLE members
							(bangor_id text, surname text, forname text, email text, mobile text, school text,study_year int)''')
			c.close()
		except sqlite3.Error, e:
			print "Error: " + e.args[0]

	def add_member(bangor_id, surname, forename, email, mobile, school, study_year):
		c = conn.cursor()
		if not self.validate_user(bangor_id):
			c.execute('''INSERT INTO members VALUES (bangor_id, surname, forename, email, mobile, school, study_year)''')
		c.close()

	def remove_member(bangor_id):
		c = conn.cursor()
		if self.validate_user(bangor_id):
			c.execute('''DELETE FROM members WHERE bangor_id=?''', (bangor_id))
		else:
			print 'Member not removed'
		c.close()

	def validate_user(bangor_id):
		c = conn.cursor()
		if c.execute('''SELECT forename FROM members WHERE bangorid=?''', (bangor_id)) != '':
			return True
		c.close()


	def _close_connection():
		c.commit()
		c.close()
