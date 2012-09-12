from random import shuffle

SUITS = { 0 : 'Hearts',
		  1 : 'Diamonds',
		  2 : 'Clubs',
		  3 : 'Spades' }

CARDS = { k, v for x, str(x) in x in xrange(2, 11)}

CARDS.update({ 
	11 : 'Jack',
	12 : 'Queen',
	13 : 'King',
	14 : 'Ace'
	})

class Desk(object):

	def __init__(self):
		self.cards = [Card(value, suit) for value in CARDS
					 	for suit in SUITS]
		self.shuffle()

	def shuffle(self):
		shuffle(self.cards)

	def __iter__(self):
		return self

	def next(self):
		for card in self.cards[:]:
			yield card
		raise StopIteration


class Card(object):

	def __init__(self, value, suit):
		self.value = value
		self.suit = suit

	def __eq__(self, other):
		return self.value == other.value and self.suit == other.suit

	def __str__(self):
		return '{} of {}'.format(CARDS[self.value], SUITS[self.suit])
