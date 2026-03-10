import socket
import json


class GameClientModel:
    def __init__(self, host="127.0.0.1", port=4000):
        self.host = host
        self.port = port

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((self.host, self.port))

        self.board = [
            ["", "", ""],
            ["", "", ""],
            ["", "", ""]
        ]
        self.current_turn = "X"
        self.your_turn = False
        self.winner = None

    def receive(self):
        try:
            data = self.client.recv(1024).decode()
            if not data:
                return None

            message = json.loads(data)

            self.board = message["board"]
            self.current_turn = message["current_turn"]
            self.your_turn = message["your_turn"]
            self.winner = message["winner"]

            return message
        except:
            pass

    def send_move(self, row, col):
        move = {
            "row": row,
            "col": col
        }

        try:
            self.client.send(json.dumps(move).encode())
        except:
            pass