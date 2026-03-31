import threading
import json
import os


class GameSession:
    def __init__(self, session_id, player_x, player_o, game_server):
        self.session_id = session_id
        self.game_server = game_server

        self.clients = {
            "X": player_x,
            "O": player_o
        }

        self.board = [
            ["", "", ""],
            ["", "", ""],
            ["", "", ""]
        ]

        self.current_turn = "X"
        self.winner = None
        self.lock = threading.Lock()

        self.images_dir = "images"

        self.is_closed = False
        self.history_saved = False

    def start(self):
        print(f"Session #{self.session_id} started")

        self.send_start_info()
        self.send_avatars()
        self.broadcast()

        threading.Thread(target=self.service_client, args=("X",), daemon=True).start()
        threading.Thread(target=self.service_client, args=("O",), daemon=True).start()

    def service_client(self, symbol):
        client = self.clients[symbol]

        while True:
            try:
                line = client.recv_line()

                if not line:
                    print(f"Session #{self.session_id}: {symbol} disconnected")
                    self.close_session()
                    break

                message = json.loads(line)

                if message.get("type") == "play_again":
                    if self.winner is not None:
                        self._handle_play_again(symbol, client)
                    break

                row = message["row"]
                col = message["col"]

                self.move(symbol, row, col)

            except Exception as e:
                print(f"Session #{self.session_id}: error for {symbol}: {e}")
                self.close_session()
                break

    def _handle_play_again(self, symbol, client):
        with self.lock:
            self.clients.pop(symbol, None)
            all_left = len(self.clients) == 0

        if all_left and self.game_server:
            self.game_server.remove_session(self.session_id)

        print(f"Session #{self.session_id}: {symbol} goes to rematch")
        self.game_server.add_to_matchmaking(client)

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
                self._save_history(winner_symbol=symbol)
            else:
                all_filled = all(
                    self.board[r][c] != ""
                    for r in range(3)
                    for c in range(3)
                )
                if all_filled:
                    self.winner = "draw"
                    self._save_history(winner_symbol=None)
                else:
                    self.current_turn = "O" if self.current_turn == "X" else "X"

            self.broadcast()

    def _save_history(self, winner_symbol):
        if self.history_saved:
            return
        self.history_saved = True

        try:
            user_repo = self.game_server.user_repo
            x_login = self.clients["X"].login
            o_login = self.clients["O"].login

            if winner_symbol is None:
                user_repo.save_game(self.session_id, x_login, o_login, "draw")
                user_repo.save_game(self.session_id, o_login, x_login, "draw")
            else:
                loser_symbol = "O" if winner_symbol == "X" else "X"
                winner_login = self.clients[winner_symbol].login
                loser_login = self.clients[loser_symbol].login
                user_repo.save_game(self.session_id, winner_login, loser_login, "win")
                user_repo.save_game(self.session_id, loser_login, winner_login, "loss")
        except Exception as e:
            print(f"Session #{self.session_id}: failed to save history: {e}")

    def check_winner(self, symbol):
        for i in range(3):
            if (
                self.board[i][0] == symbol and
                self.board[i][1] == symbol and
                self.board[i][2] == symbol
            ):
                return True

            if (
                self.board[0][i] == symbol and
                self.board[1][i] == symbol and
                self.board[2][i] == symbol
            ):
                return True

        if (
            self.board[0][0] == symbol and
            self.board[1][1] == symbol and
            self.board[2][2] == symbol
        ):
            return True

        if (
            self.board[0][2] == symbol and
            self.board[1][1] == symbol and
            self.board[2][0] == symbol
        ):
            return True

        return False

    def send_start_info(self):
        for symbol, client in self.clients.items():
            opponent = self.clients["O"] if symbol == "X" else self.clients["X"]

            message = {
                "type": "start",
                "your_symbol": symbol,
                "opponent_symbol": "O" if symbol == "X" else "X",
                "your_login": client.login,
                "your_name": client.name,
                "opponent_login": opponent.login,
                "opponent_name": opponent.name
            }

            try:
                client.send_line(json.dumps(message))
            except Exception as e:
                print(f"Session #{self.session_id}: start info error for {symbol}: {e}")

    def send_avatars(self):
        for symbol, client in self.clients.items():
            opponent = self.clients["O"] if symbol == "X" else self.clients["X"]

            try:
                your_filename = client.image if client.image else ""
                your_path = os.path.join(self.images_dir, your_filename)

                if your_filename and os.path.isfile(your_path):
                    with open(your_path, "rb") as f:
                        your_data = f.read()
                else:
                    your_data = b""

                client.send_line("YOUR_AVATAR")
                client.send_line(your_filename)
                client.send_bytes(your_data)

                opponent_filename = opponent.image if opponent.image else ""
                opponent_path = os.path.join(self.images_dir, opponent_filename)

                if opponent_filename and os.path.isfile(opponent_path):
                    with open(opponent_path, "rb") as f:
                        opponent_data = f.read()
                else:
                    opponent_data = b""

                client.send_line("OPPONENT_AVATAR")
                client.send_line(opponent_filename)
                client.send_bytes(opponent_data)

            except Exception as e:
                print(f"Session #{self.session_id}: avatar send error for {symbol}: {e}")

    def broadcast(self):
        for symbol, client in self.clients.items():
            message = {
                "type": "game_state",
                "board": self.board,
                "current_turn": self.current_turn,
                "your_turn": symbol == self.current_turn and self.winner is None,
                "winner": self.winner
            }

            try:
                client.send_line(json.dumps(message))
            except Exception as e:
                print(f"Session #{self.session_id}: broadcast error for {symbol}: {e}")

    def get_info(self):
        return {
            "session_id": self.session_id,
            "x_login": self.clients["X"].login if self.clients.get("X") else "",
            "o_login": self.clients["O"].login if self.clients.get("O") else "",
            "current_turn": self.current_turn,
            "winner": self.winner
        }

    def kick_player(self, symbol):
        client = self.clients.get(symbol)

        if not client:
            return

        try:
            client.conn.close()
        except:
            pass

        other_symbol = "O" if symbol == "X" else "X"
        other = self.clients.get(other_symbol)

        try:
            if other:
                other.send_line(json.dumps({
                    "type": "opponent_disconnected"
                }))
        except:
            pass

    def close_session(self):
        with self.lock:
            if self.is_closed:
                return
            self.is_closed = True

            if self.winner is None:
                self._save_history(winner_symbol=None)

            clients_to_close = list(self.clients.values())
            self.clients.clear()

        for client in clients_to_close:
            try:
                client.conn.close()
            except:
                pass

        if self.game_server:
            self.game_server.remove_session(self.session_id)