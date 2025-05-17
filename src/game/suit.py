from enum import Enum


class Suit(Enum):
    HEARTS   = "hearts",   '♥', 4
    DIAMONDS = "diamonds", '♦', 3
    CLUBS    = "clubs",    '♣', 2
    SPADES   = "spades",   '♠', 1

    def __init__(self, representation: str, symbol: str, order: int):
        self.representation = representation
        self.symbol = symbol
        self.order = order

    @classmethod
    def by_value(cls, representation: str) -> "Suit":
        for suit in cls.__members__.values():
            if suit.representation == representation.lower():
                return suit
        else:
            raise ValueError

    def __eq__(self, other):
        return self is other

    def __gt__(self, other):
        return isinstance(other, Suit) and self.order > other.order

    def __hash__(self):
        return hash(self.representation)

    def __repr__(self):
        return self.representation
