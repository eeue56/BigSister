from big.irc.bot import IrcBot
from big.irc.misc import crop_string


from time import sleep

import socket



class BetTooSmall(Exception):
	pass

class PlayerNotFound(Exception):
	pass

class Player(object):

	def __init__(self, name, money):
		self.name = name
		self.money = money

	def __eq__(self, other):
		return self.name == other.name


class PokerRound(object):

	def __init__(self, players, min_bet=1):
		self._min_bet = min_bet
		self.pot = 0
		self.players = players

		self.bets_made = []

		self._to_bet = players[:]

	@property
	def minimum_bet(self):
		try:
			return min(self._min_bet, self.bets_made[-1])
		except IndexError:
			return self._min_bet

	def _get_player(self, name):
		for player in self.players:
			if player.name == name:
				return player

	def add_bet(self, player_name, amount):
		if amount < self.minimum_bet:
			raise BetTooSmall("Bet must be more than {}".format(self.minimum_bet))

		if not player_name in self._to_bet:
			raise PlayerNotFound

		self.pot += amount
		player = self._get_player(player_name)

		player.money -= amount

	def __iter__(self):
		return self

	def next(self):
		while self._to_bet:
			yield self._to_bet.pop()
		raise StopIteration


class PokerGame(object):

	def __init__(self, players):
		
		self.players = [Player(player) for player in players]
		self.pot = 0

	def next(self):



class PokerBot(IrcBot):

    def __init__(self, host, port, nick, ident, realname, owner):
        IrcBot.__init__(self, host, port, nick, ident, realname, owner)

