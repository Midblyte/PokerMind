import multiprocessing
import os
import time
from random import sample as random_sample, shuffle as random_shuffle
from multiprocessing import Process, Queue
from threading import Lock
from typing import Optional

from game.card import Card, DECK
from game.game import Game
from game.guess import Guess
from log import logger


class PokerMind:
    # threshold = [4..31]
    def __init__(self, threshold: int = 4):
        self.threshold = threshold

        self.lock = Lock()

        self.game: Game = ...

    @staticmethod
    def _shuffle(full_deck: frozenset[Card]) -> list[Card]:
        deck = list(DECK)

        random_shuffle(deck)

        return deck

    def show(self) -> Game:
        with self.lock:
            return self.game

    def reveal(self) -> Card:
        with self.lock:
            return self.game.card

    def guess(self, card: Card) -> Guess:
        with self.lock:
            rank_matches = card.rank == self.game.card.rank
            suit_matches = card.suit == self.game.card.suit

            if rank_matches and suit_matches:
                return Guess.CORRECT
            elif not rank_matches and not suit_matches:
                return Guess.WRONG

            return Guess.PARTIAL

    def new_game(self) -> Game:
        logger.info("Generating...")
        start = time.time()

        self.lock.acquire()

        processes: list[Process] = []
        queue: Queue = Queue()

        for i in range(min(self.threshold, os.cpu_count())):
            process = multiprocessing.Process(target=self._find, args=(queue, ), name=f"Finder_{i}")
            processes.append(process)
            process.start()

        for process in processes:
            if (game := queue.get()) is not None:
                for p in processes:
                    p.terminate()

                break

            process.join()
        else:
            raise RuntimeError("Time out")

        end = time.time()
        logger.info(f"Done! ({end - start:.3} s)")

        self.game = game
        self.lock.release()

        logger.debug(repr(game))

        return game

    def _find(self, queue: Queue, iterations: int = 5000) -> Optional[Game]:
        for i in range(iterations):
            deck = self._shuffle(DECK)

            sample = tuple(random_sample(deck, 9))

            player1 = tuple(sorted(sample[0:4], key=lambda k: k.rank.numeric_value))
            player2 = tuple(sorted(sample[4:8], key=lambda k: k.rank.numeric_value))

            card = sample[8]

            # noinspection PyTypeChecker
            game = Game(player1, player2, card)

            hands = game.hand1round1, game.hand1round2, game.hand2round1, game.hand2round2

            if sum(map(lambda h: h.ranking.value, hands)) >= self.threshold and game.round1 != game.round2:
                queue.put(game)

                return game
        else:
            return None
