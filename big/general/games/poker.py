from big.irc.bot import IrcBot
from big.irc.misc import crop_string
from big.general.games.cards import Deck


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
        self.cards = []

    def add_card(self, card):
        self.cards.append(card)

    def add_cards(self, cards):
        self.cards.extend(cards)

    def __eq__(self, other):
        return self.name == other.name


class PokerRound(object):

    def __init__(self, players, pot=0, min_bet=1):
        self._min_bet = min_bet
        self.pot = pot
        self.players = players

        self.bets_made = []

        self._to_bet = players[:]
        self._next = self._to_bet.pop()


    @property
    def minimum_bet(self):
        try:
            return min(self._min_bet, self.bets_made[-1])
        except IndexError:
            return self._min_bet

    def _update_player(self):
        self._next = self._to_bet.pop()

    def _get_player(self, name):
        for player in self.players:
            if player.name == name:
                return player
        raise PlayerNotFound

    def add_bet(self, player_name, amount):
        if amount < self.minimum_bet:
            raise BetTooSmall("Bet must be more than {}".format(self.minimum_bet))

        if not player_name in self._to_bet:
            raise PlayerNotFound

        self.pot += amount
        player = self._get_player(player_name)

        player.money -= amount

    def see(self, player_name):
        if not player_name in self._to_bet:
            raise PlayerNotFound

        last_bet = self.bets_made[-1]
        player = self._get_player(player_name)

        self.pot += last_bet
        player.money -= last_bet

    def fold(self, player_name):
        folding_player = self._get_player(player_name)

        self.players.remove(folding_player)

    @property
    def next_player_to_bet(self):
        return self._to_bet[self._index]


class PokerGame(object):

    def __init__(self, players):
        
        self.players = [Player(player) for player in players]
        self.pot = 0
        self.state = None
        self.cards = []
        self.deck = Deck()

        self._stages = [self._pre_flop,
                        self._flop,
                        self._turn,
                        self._river]

    def next_round(self):
        return PokerRound(self.players, self.pot)

    def _pre_flop(self):
        self.state = 'Pre-flop'

        for player in self.players:
            player.add_cards(self.deck.draw_cards(2))

        return self.next_round()

    def _flop(self):
        self.state = 'Flop'
        self.cards.extend(self.deck.draw_cards(3))

        return self.next_round()

    def _turn(self):
        self.state = 'Turn'
        self.cards.extend(self.deck.draw_cards(1))

        return self.next_round()

    def _river(self):
        self.state = 'River'
        self.cards.extend(self.deck.draw_cards(1))

        return self.next_round()

    def next(self):
        while self._stages:
            yield self._stages.pop(0)
        raise StopIteration


class PokerBot(IrcBot):

    def __init__(self, host, port, nick, ident, realname, owner):
        IrcBot.__init__(self, host, port, nick, ident, realname, owner)
        self.game = None

    def new_game(self, message, *args, **kwargs):
        players = [name.strip() for name in message.split()]

        self.game = PokerGame(players)
        return 'Done'

    def bet(self, *args, **kwargs):


    def play_game(self, *args, **kwargs):
        for round in self.game:


