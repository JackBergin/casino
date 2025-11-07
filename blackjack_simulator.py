import random
from collections import namedtuple

Card = namedtuple("Card", ["rank", "suit"])

RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
SUITS = ['♠', '♥', '♦', '♣']
VALUES = {
    '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
    '10': 10, 'J': 10, 'Q': 10, 'K': 10, 'A': 11
}


class Shoe:
    """Represents one or more decks shuffled together."""
    def __init__(self, num_decks=6):
        self.num_decks = num_decks
        self.cards = []
        self.shuffle()

    def shuffle(self):
        self.cards = [Card(rank, suit) for rank in RANKS for suit in SUITS] * self.num_decks
        random.shuffle(self.cards)

    def draw(self):
        if len(self.cards) < 15:
            self.shuffle()
        return self.cards.pop()


def hand_value(hand):
    """Return best blackjack value treating Aces as 1 or 11."""
    value = sum(VALUES[c.rank] for c in hand)
    aces = sum(1 for c in hand if c.rank == 'A')
    while value > 21 and aces:
        value -= 10
        aces -= 1
    return value


def hand_str(hand):
    return " ".join(f"{c.rank}{c.suit}" for c in hand)


def is_blackjack(hand):
    return len(hand) == 2 and hand_value(hand) == 21


def is_soft_17(hand):
    """True if hand is a soft 17 (Ace counted as 11)."""
    total = sum(VALUES[c.rank] for c in hand)
    aces = sum(1 for c in hand if c.rank == 'A')
    return aces > 0 and total == 17


def simulate_blackjack_hand(shoe, num_players=1, bet=10, dealer_hits_soft_17=False):
    """
    Simulates a single blackjack hand.
    Returns (result, payout, dict with player/dealer hands and values)
    """
    dealer = [shoe.draw(), shoe.draw()]
    player = [shoe.draw(), shoe.draw()]
    other_players = [[shoe.draw(), shoe.draw()] for _ in range(num_players - 1)]

    player_bj = is_blackjack(player)
    dealer_bj = is_blackjack(dealer)

    if player_bj and not dealer_bj:
        return "win", 1.5 * bet, _hand_data(player, dealer)
    elif dealer_bj and not player_bj:
        return "lose", 0, _hand_data(player, dealer)
    elif player_bj and dealer_bj:
        return "push", 0, _hand_data(player, dealer)

    # Player: hit until 17 or more
    while hand_value(player) < 17:
        player.append(shoe.draw())
    if hand_value(player) > 21:
        return "lose", 0, _hand_data(player, dealer)

    # Dealer: hit until ≥17, optional hit soft 17
    while True:
        val = hand_value(dealer)
        if val < 17 or (dealer_hits_soft_17 and is_soft_17(dealer)):
            dealer.append(shoe.draw())
        else:
            break

    p_val, d_val = hand_value(player), hand_value(dealer)
    if d_val > 21:
        return "win", bet, _hand_data(player, dealer)
    if p_val > d_val:
        return "win", bet, _hand_data(player, dealer)
    if p_val < d_val:
        return "lose", 0, _hand_data(player, dealer)
    return "push", 0, _hand_data(player, dealer)


def _hand_data(player, dealer):
    return {
        "player": hand_str(player),
        "dealer": hand_str(dealer),
        "player_value": hand_value(player),
        "dealer_value": hand_value(dealer),
    }
