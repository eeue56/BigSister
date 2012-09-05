'''module to handle SQL database intergration'''

import sqlite3

class MembersDatabase(object):

	def __init__(self, database_name):
		self.database_name = database_name
		self.conn = None

	def _connect_to_db(self):
		self.conn = sqlite3.connect(self.database_name)

	def create_table(self):
		try:
			c = self.conn.cursor()
			c.execute('''CREATE TABLE members
							(bangor_id text, surname text, forename text, email text, mobile text, school text,study_year int)''')
			self.conn.commit()
			c.close()

		except sqlite3.Error, e:
			print "Error: " + e.args[0]

	def add_member(self, bangor_id, surname, forename, email, mobile, school, study_year):
		c = self.conn.cursor()
		print bangor_id
		if not self.validate_user(bangor_id):
			print 'Here I am'
			c.execute('''INSERT INTO members VALUES (?,?,?,?,?,?,?)''', (bangor_id, surname, forename, email, mobile, school, study_year))
		self.conn.commit()
		c.close()

	def remove_member(self, bangor_id):
		c = self.conn.cursor()
		if self.validate_user(bangor_id):
			c.execute('''DELETE FROM members WHERE bangor_id=?''', (bangor_id,))
		else:
			print 'Member not removed'
		self.conn.commit()
		c.close()

	def validate_user(self, bangor_id):
		c = self.conn.cursor()
		c.execute('''SELECT * FROM members WHERE bangor_id=?''', (bangor_id,))
		if c.fetchone() is None:
			return False
		else:
			return True
		c.close()
		


	def _close_connection(self):
		self.conn.close()
