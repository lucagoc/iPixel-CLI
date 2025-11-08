"""
File for pypixel package.
"""

class Client:
    def __init__(self):
        self._connected = False
        self._addr = None

    def connect(self, address: str) -> None:
        self._addr = address
        self._connected = True
        print(f"Connected to {address}")

    def send_text(self, text: str) -> None:
        if not self._connected:
            raise RuntimeError("Client not connected")
        print(f"Sending to {self._addr}: {text}")
