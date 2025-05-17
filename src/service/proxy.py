import json
import socket
from typing import Any

from game.card import Card
from service.interface import Interface


_BUFFER_SIZE = 1024


class Proxy(Interface):
    def __init__(self, port: int):
        self.port = port

    def _request(self, **kwargs) -> tuple[bool, Any]:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("127.0.0.1", self.port))

        # Send
        s.send(json.dumps(kwargs).encode("utf-8"))
        # Receive
        data = s.recv(_BUFFER_SIZE)

        s.close()

        returned = json.loads(data.decode("utf-8"))
        ok = returned["ok"]
        data = returned.get("data")

        return ok, data

    def show(self):
        return self._request(action="show")

    def reveal(self):
        return self._request(action="reveal")

    def guess(self, card: Card):
        return self._request(
            action="guess",
            card=dict(
                rank=repr(card.rank),
                suit=repr(card.suit)
            )
        )

    def new_game(self):
        return self._request(action="new_game")
