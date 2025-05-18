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

    reveal_parser.add_argument("--training-mode", "-T", action="store_true", help="output as CSV and create a new game")

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
        case "reveal":
            if args.training_mode:
                ok = training(proxy)

                exit(0 if ok else 1)
            else:
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


def training(proxy: Proxy) -> bool:
    ok_reveal,   data_reveal   = proxy.reveal()
    ok_show,     data_show     = proxy.show()
    ok_new_game, data_new_game = proxy.new_game()

    if not (ok_reveal and ok_show and ok_new_game):
        return False

    print(','.join(map(str, [
        # Input

        # Unrolled version:
        #   data_show[player][n][kind]["value"]
        #   for player in ("player1", "player2")
        #   for n in range(4)
        #   for kind in ("rank", "suit")

        data_show["player1"][0]["rank"]["value"],
        data_show["player1"][0]["suit"]["value"],
        data_show["player1"][1]["rank"]["value"],
        data_show["player1"][1]["suit"]["value"],
        data_show["player1"][2]["rank"]["value"],
        data_show["player1"][2]["suit"]["value"],
        data_show["player1"][3]["rank"]["value"],
        data_show["player1"][3]["suit"]["value"],

        data_show["player2"][0]["rank"]["value"],
        data_show["player2"][0]["suit"]["value"],
        data_show["player2"][1]["rank"]["value"],
        data_show["player2"][1]["suit"]["value"],
        data_show["player2"][2]["rank"]["value"],
        data_show["player2"][2]["suit"]["value"],
        data_show["player2"][3]["rank"]["value"],
        data_show["player2"][3]["suit"]["value"],

        data_show["round1"]["value"],
        data_show["round2"]["value"],

        # Output

        data_reveal["card"]["rank"]["value"],
        data_reveal["card"]["suit"]["value"]
    ])))

    return True


if __name__ == "__main__":
    main()
