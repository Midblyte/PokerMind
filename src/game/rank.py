from enum import Enum


class Rank(Enum):
    ACE   = ('A',  14, 1)
    TWO   = ('2',  2 , 2)
    THREE = ('3',  3 , 3)
    FOUR  = ('4',  4 , 4)
    FIVE  = ('5',  5 , 5)
    SIX   = ('6',  6 , 6)
    SEVEN = ('7',  7 , 7)
    EIGHT = ('8',  8 , 8)
    NINE  = ('9',  9 , 9)
    TEN   = ('10', 10, 10)
    JACK  = ('J',  11, 11)
    QUEEN = ('Q',  12, 12)
    KING  = ('K',  13, 13)

    def __init__(self, representation: str, numeric_value: int, comparation_value: int):
        self.representation = representation
        self.numeric_value = numeric_value
        self.comparation_value = comparation_value

    @classmethod
    def by_value(cls, representation: str) -> "Rank":
        for rank in cls.__members__.values():
            if rank.representation == representation.upper():
                return rank
        else:
            raise ValueError

    def __gt__(self, other):
        if not isinstance(other, Rank):
            return False
        return self.numeric_value > other.numeric_value

    def __repr__(self):
        return self.representation
