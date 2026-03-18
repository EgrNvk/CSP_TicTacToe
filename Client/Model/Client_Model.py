import socket
import json
import os


class GameClientModel:
    def __init__(self, host="127.0.0.1", port=4000):
        self.host = host
        self.port = port

        self.client = None
        self.current_login = None

        self.board = [
            ["", "", ""],
            ["", "", ""],
            ["", "", ""]
        ]

        self.current_turn = "X"
        self.your_turn = False
        self.winner = None

        self.your_symbol = None
        self.opponent_symbol = None

        self.your_name = ""
        self.opponent_login = ""
        self.opponent_name = ""

        self.your_avatar = b""
        self.opponent_avatar = b""

    def connect(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((self.host, self.port))

    def close(self):
        try:
            if self.client:
                self.client.close()
        except:
            pass

    def recv_line(self):
        data = b""

        while True:
            b = self.client.recv(1)

            if not b:
                return ""

            if b == b"\n":
                break

            data += b

        return data.decode("utf-8", errors="replace")

    def recv_exact(self, size):
        data = b""

        while len(data) < size:
            chunk = self.client.recv(size - len(data))

            if not chunk:
                return b""

            data += chunk

        return data

    def send_form(self, action, login, password, name=""):

        form = {
            "action": action,
            "login": login,
            "password": password,
            "name": name
        }

        data = json.dumps(form, ensure_ascii=False) + "\n"

        try:
            self.client.sendall(data.encode("utf-8"))

            resp = self.recv_line()

            if resp in ("OK LOGIN", "OK REGISTER"):
                self.current_login = login
                self.your_name = name

            return resp.strip()

        except Exception as e:
            return f"ERROR {e}"

    def send_file(self, login, path):

        if not os.path.exists(path):
            return "ERROR FILE NOT FOUND"

        if not os.path.isfile(path):
            return "ERROR NOT A FILE"

        filename = os.path.basename(path)
        name, ext = os.path.splitext(filename)
        size = os.path.getsize(path)

        try:
            self.client.sendall("UPLOAD\n".encode())
            self.client.sendall((login + "\n").encode())
            self.client.sendall((name + "\n").encode())
            self.client.sendall((ext + "\n").encode())
            self.client.sendall((str(size) + "\n").encode())

            with open(path, "rb") as f:
                while True:
                    data = f.read(1024)
                    if not data:
                        break
                    self.client.sendall(data)

            resp = self.recv_line()
            return resp.strip()

        except Exception as e:
            return f"ERROR {e}"

    def receive_avatar_status(self):
        return self.recv_line()

    def receive_match_status(self):
        return self.recv_line()

    def receive_start_info(self):
        line = self.recv_line()

        if not line:
            return None

        try:
            message = json.loads(line)
        except:
            return None

        if message.get("type") != "start":
            return None

        self.your_symbol = message.get("your_symbol")
        self.opponent_symbol = message.get("opponent_symbol")

        self.current_login = message.get("your_login", "")
        self.your_name = message.get("your_name", "")

        self.opponent_login = message.get("opponent_login", "")
        self.opponent_name = message.get("opponent_name", "")

        return message

    def receive_avatars(self):

        avatar_type = self.recv_line()
        size = int(self.recv_line())
        self.your_avatar = self.recv_exact(size)

        avatar_type = self.recv_line()
        size = int(self.recv_line())
        self.opponent_avatar = self.recv_exact(size)

        return {
            "your_avatar": self.your_avatar,
            "opponent_avatar": self.opponent_avatar
        }
    def receive(self):
        line = self.recv_line()

        if not line:
            return None

        try:
            message = json.loads(line)
        except:
            return None

        if message.get("type") != "game_state":
            return message

        self.board = message["board"]
        self.current_turn = message["current_turn"]
        self.your_turn = message["your_turn"]
        self.winner = message["winner"]

        return message

    def send_move(self, row, col):
        move = {
            "row": row,
            "col": col
        }

        try:
            data = json.dumps(move) + "\n"
            self.client.sendall(data.encode("utf-8"))
        except:
            pass