import json
import argparse

from game.card import Card
from game.suit import Suit
from game.rank import Rank
from service.proxy import Proxy


deck_ranks = ("A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "a", "j", "q", "k")
deck_suits = ("hearts", "diamonds", "clubs", "spades")


def main():
    parser = argparse.ArgumentParser("pokermind")

    parser.add_argument("--port", "-p", default=2231, type=int)

    subparsers = parser.add_subparsers()

    show_parser = subparsers.add_parser("show")
    show_parser.set_defaults(action="show")

    reveal_parser = subparsers.add_parser("reveal")
    reveal_parser.set_defaults(action="reveal")

    guess_parser = subparsers.add_parser("guess")
    guess_parser.set_defaults(action="guess")

    guess_parser.add_argument("rank", choices=deck_ranks)
    guess_parser.add_argument("suit", choices=deck_suits)

    new_game_parser = subparsers.add_parser("new_game")
    new_game_parser.set_defaults(action="new_game")

    args = parser.parse_args()

    port = args.port

    proxy = Proxy(port)

    match getattr(args, "action", None):
        case "show":
            ok, data = proxy.show()

            data = json.dumps(data, indent=4)
        case "reveal":
            ok, data = proxy.reveal()
        case "new_game":
            ok, data = proxy.new_game()
        case "guess":
            rank = Rank.by_value(args.rank)
            suit = Suit.by_value(args.suit)

            card = Card(rank, suit)

            ok, data = proxy.guess(card)
        case _:
            parser.print_help()
            exit(1)

    print(json.dumps(data, indent=4))

    exit(0 if ok else 1)


if __name__ == "__main__":
    main()
