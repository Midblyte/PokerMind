from functools import reduce, cache
from typing import Unpack

from game.card import Card
from game.handranking import HandRanking
from game.rank import Rank
from game.suit import Suit


_ROYAL_FLUSHES: dict[Suit, set[Card]] = {
    Suit.HEARTS: {
        Card(rank=Rank.ACE,   suit=Suit.HEARTS),
        Card(rank=Rank.KING,  suit=Suit.HEARTS),
        Card(rank=Rank.QUEEN, suit=Suit.HEARTS),
        Card(rank=Rank.JACK,  suit=Suit.HEARTS),
        Card(rank=Rank.TEN,   suit=Suit.HEARTS)
    },
    Suit.DIAMONDS: {
        Card(rank=Rank.ACE,   suit=Suit.DIAMONDS),
        Card(rank=Rank.KING,  suit=Suit.DIAMONDS),
        Card(rank=Rank.QUEEN, suit=Suit.DIAMONDS),
        Card(rank=Rank.JACK,  suit=Suit.DIAMONDS),
        Card(rank=Rank.TEN,   suit=Suit.DIAMONDS)
    },
    Suit.CLUBS: {
        Card(rank=Rank.ACE,   suit=Suit.CLUBS),
        Card(rank=Rank.KING,  suit=Suit.CLUBS),
        Card(rank=Rank.QUEEN, suit=Suit.CLUBS),
        Card(rank=Rank.JACK,  suit=Suit.CLUBS),
        Card(rank=Rank.TEN,   suit=Suit.CLUBS)
    },
    Suit.SPADES: {
        Card(rank=Rank.ACE,   suit=Suit.SPADES),
        Card(rank=Rank.KING,  suit=Suit.SPADES),
        Card(rank=Rank.QUEEN, suit=Suit.SPADES),
        Card(rank=Rank.JACK,  suit=Suit.SPADES),
        Card(rank=Rank.TEN,   suit=Suit.SPADES)
    }
}


class Hand:
    def __init__(self, *cards: Unpack[Card]):
        self.cards = frozenset(cards)

    def __eq__(self, other) -> bool:
        if not isinstance(other, Hand):
            return False

        hand_ranking1, _, value1, kickers1 = self._analyse()
        hand_ranking2, _, value2, kickers2 = other._analyse()

        return hand_ranking1 == hand_ranking2 and value1 == value2 and all((
            Hand(k1) == Hand(k2) for k1, k2 in zip(kickers1, kickers2)
        ))

    def __gt__(self, other) -> bool:
        if not isinstance(other, Hand):
            return False

        hand_ranking1, _, value1, kickers1 = self._analyse()
        hand_ranking2, _, value2, kickers2 = other._analyse()

        if hand_ranking1 != hand_ranking2:
            return hand_ranking1 > hand_ranking2

        if value1 != value2:
            return value1 > value2

        for k1, k2 in zip(kickers1, kickers2):
            hk1, hk2 = Hand(k1), Hand(k2)

            if hk1 == hk2:
                continue

            return hk1 > hk2
        else:
            return False

    @staticmethod
    @cache
    def _catalog(cards: frozenset[Card]) -> tuple[HandRanking, tuple[Card], int]:
        if (number_of_cards := len(cards)) == 0:
            raise ValueError

        at_least_five: bool = number_of_cards >= 5

        # Highest to lowest
        # noinspection PyTypeChecker
        by_value: tuple[Card] = tuple(sorted(cards, key=lambda card: card.rank.numeric_value, reverse=True))

        if at_least_five:
            # 1. Royal flush
            for suit in Suit:
                royal_flush_set: set = _ROYAL_FLUSHES[suit]

                if all((card in cards for card in royal_flush_set)):
                    royal_flush = tuple(sorted(royal_flush_set, key=lambda k: k.rank.numeric_value, reverse=True))

                    # noinspection PyTypeChecker
                    return HandRanking.ROYAL_FLUSH, royal_flush, 0

            # 2. Straight flush
            for suit in Suit:
                streak = []
                max_rank: Rank = ...
                for rank in reversed(tuple(Rank)):
                    if (this := Card(rank=rank, suit=suit)) in cards:
                        if len(streak) == 0:
                            max_rank = rank

                        streak.append(this)

                        if len(streak) == 5:
                            # noinspection PyTypeChecker
                            return HandRanking.STRAIGHT_FLUSH, tuple(streak), max_rank.numeric_value

                    else:
                        streak = []
                        max_rank = ...

        # 3. Four of a kind
        for rank in sorted(list(Rank), reverse=True):
            four_of_a_kind: tuple = tuple(Card(rank=rank, suit=suit) for suit in Suit)

            if all((card in cards for card in four_of_a_kind)):
                return HandRanking.FOUR_OF_A_KIND, four_of_a_kind, rank.numeric_value

        count = []  # A, K, Q, ..., 3, 2
        ranks: list[Rank] = [card.rank for card in by_value]

        for rank in sorted(list(Rank), reverse=True):
            count.append(ranks.count(rank))

        three_index = count.index(3) if 3 in count else -1
        two_index = count.index(2) if 2 in count else -1

        if at_least_five:
            # 4. Full House
            if three_index >= 0 and two_index >= 0:
                threes = tuple(filter(lambda card: card.rank.numeric_value == 12 - three_index, by_value))
                twos   = tuple(filter(lambda card: card.rank.numeric_value == 12 - two_index  , by_value))

                # noinspection PyTypeChecker
                return HandRanking.FULL_HOUSE, threes + twos, (12-three_index) * 13 + (12-two_index)

            # 5. Flush
            suit_groups: dict[Suit, list[Card]] = {suit: [] for suit in Suit}
            for card in by_value:
                suit = card.suit
                suit_groups[suit].append(card)

            suit_groups_filtered = {suit: group[:5] for suit, group in suit_groups.items() if len(group) >= 5}

            if len(suit_groups_filtered) > 0:
                suit_groups_values: dict[Suit, int] = {suit: (
                    group[0].rank.numeric_value * 13**4 +
                    group[1].rank.numeric_value * 13**3 +
                    group[2].rank.numeric_value * 13**2 +
                    group[3].rank.numeric_value * 13**1 +
                    group[4].rank.numeric_value * 13**0
                ) for suit, group in suit_groups_filtered.items()}

                suit, value = reduce(lambda prev, next: prev if prev[1] > next[1] else next, suit_groups_values.items())
                flush = suit_groups_filtered[suit]

                # noinspection PyTypeChecker
                return HandRanking.FLUSH, tuple(flush), flush[0].rank.numeric_value

            # 6. Straight
            streak = list()
            max_rank: Rank = ...
            for rank in reversed(tuple(Rank)):
                for suit in Suit:
                    if (this := Card(rank=rank, suit=suit)) in cards:
                        if len(streak) == 0:
                            max_rank = rank

                        streak.append(this)

                        if len(streak) == 5:
                            # noinspection PyTypeChecker
                            return HandRanking.STRAIGHT, tuple(streak), max_rank.numeric_value

                        break
                else:
                    streak = list()

        # 7. Three of a kind
        if three_index >= 0:
            threes = tuple(filter(lambda card: card.rank.numeric_value == 12 - three_index, by_value))

            # noinspection PyTypeChecker
            return HandRanking.THREE_OF_A_KIND, threes, 12-three_index

        # 8. Two Pair
        second_two_index = count.index(2, two_index + 1) if 2 in count[two_index+1:] else -1

        if two_index >= 0 and second_two_index >= 0:
            twos        = tuple(filter(lambda card: card.rank.numeric_value == 12 - two_index       , by_value))
            second_twos = tuple(filter(lambda card: card.rank.numeric_value == 12 - second_two_index, by_value))

            # noinspection PyTypeChecker
            return HandRanking.TWO_PAIR, twos + second_twos, (12-two_index) * 13 + (12-second_two_index)

        # 9. Pair
        if two_index >= 0:
            twos = tuple(filter(lambda card: card.rank.numeric_value == 12 - two_index, by_value))

            # noinspection PyTypeChecker
            return HandRanking.PAIR, twos, 12-two_index

        # 10. High Card
        high_card: Card = reduce(lambda prev, next: prev if prev > next else next, cards)
        return HandRanking.HIGH_CARD, (high_card, ), high_card.rank.numeric_value

    def _analyse(self) -> tuple[HandRanking, set[Card], int, tuple[Card]]:
        copy = frozenset(self.cards)

        ranking, cards, value = Hand._catalog(copy)

        # noinspection PyTypeChecker
        kickers: tuple[Card] = tuple(sorted(copy.difference(cards), reverse=True))

        return ranking, cards, value, kickers

    @property
    def ranking(self) -> HandRanking:
        hand_ranking, cards, value = Hand._catalog(self.cards)

        return hand_ranking
