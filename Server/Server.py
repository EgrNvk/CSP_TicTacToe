import socket
import threading
import json


class GameServer:
    def __init__(self, host="127.0.0.1", port=4000):
        self.host = host
        self.port = port

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen(2)

        self.clients = {}
        self.board = [
            ["", "", ""],
            ["", "", ""],
            ["", "", ""]
        ]
        self.current_turn = "X"
        self.winner = None
        self.lock = threading.Lock()

    def start(self):
        print("Server started")

        conn_x, addr_x = self.server.accept()
        self.clients["X"] = conn_x
        print("X connected:", addr_x)

        conn_o, addr_o = self.server.accept()
        self.clients["O"] = conn_o
        print("O connected:", addr_o)

        self.broadcast()

        threading.Thread(target=self.service_client, args=("X",), daemon=True).start()
        threading.Thread(target=self.service_client, args=("O",), daemon=True).start()

        while True:
            pass

    def service_client(self, symbol):
        conn = self.clients[symbol]

        while True:
            try:
                data = conn.recv(1024).decode()
                if not data:
                    break

                move = json.loads(data)
                row = move["row"]
                col = move["col"]

                self.move(symbol, row, col)
            except:
                pass

    def move(self, symbol, row, col):
        with self.lock:
            if self.winner is not None:
                return

            if symbol != self.current_turn:
                return

            if row < 0 or row > 2 or col < 0 or col > 2:
                return

            if self.board[row][col] != "":
                return

            self.board[row][col] = symbol

            if self.check_winner(symbol):
                self.winner = symbol
            else:
                self.current_turn = "O" if self.current_turn == "X" else "X"

            self.broadcast()

    def check_winner(self, symbol):
        for i in range(3):
            if self.board[i][0] == symbol and self.board[i][1] == symbol and self.board[i][2] == symbol:
                return True

            if self.board[0][i] == symbol and self.board[1][i] == symbol and self.board[2][i] == symbol:
                return True

        if self.board[0][0] == symbol and self.board[1][1] == symbol and self.board[2][2] == symbol:
            return True

        if self.board[0][2] == symbol and self.board[1][1] == symbol and self.board[2][0] == symbol:
            return True

        return False

    def broadcast(self):
        for symbol, conn in self.clients.items():
            message = {
                "board": self.board,
                "current_turn": self.current_turn,
                "your_turn": symbol == self.current_turn and self.winner is None,
                "winner": self.winner
            }

            try:
                conn.send(json.dumps(message).encode())
            except:
                pass



server = GameServer()
server.start()