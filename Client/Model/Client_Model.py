import socket
import json
import os

from cryptography.fernet import Fernet
from Client.config import SERVER_HOST, SERVER_PORT, FERNET_KEY


class GameClientModel:
    def __init__(self, host, port):
        self.host = host
        self.port = port

        self.client = None
        self.current_login = None

        self.cipher_suite = Fernet(FERNET_KEY)

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

        self.your_avatar_filename = ""
        self.opponent_avatar_filename = ""

        self.your_avatar_path = ""
        self.opponent_avatar_path = ""

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
        token = b""

        while True:
            b = self.client.recv(1)

            if not b:
                return ""

            if b == b"\n":
                break

            token += b

        try:
            plain = self.cipher_suite.decrypt(token)
            return plain.decode("utf-8")
        except:
            return ""

    def send_form(self, action, login, password, name=""):
        form = {
            "action": action,
            "login": login,
            "password": password,
            "name": name
        }

        data = json.dumps(form, ensure_ascii=False)

        try:
            self.send_line(data)

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

        try:
            self.send_line("UPLOAD")
            self.send_line(login)
            self.send_line(name)
            self.send_line(ext)

            with open(path, "rb") as f:
                file_data = f.read()

            self.send_bytes(file_data)

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
        os.makedirs("avatars_cache", exist_ok=True)

        avatar_type = self.recv_line()
        filename = self.recv_line()

        if avatar_type != "YOUR_AVATAR":
            return None

        data = self.recv_bytes()

        if data is None:
            return None

        self.your_avatar_filename = filename
        if filename:
            self.your_avatar_path = os.path.join("avatars_cache", filename)
            with open(self.your_avatar_path, "wb") as f:
                f.write(data)
        else:
            self.your_avatar_path = ""

        avatar_type = self.recv_line()
        filename = self.recv_line()

        if avatar_type != "OPPONENT_AVATAR":
            return None

        data = self.recv_bytes()

        if data is None:
            return None

        self.opponent_avatar_filename = filename
        if filename:
            self.opponent_avatar_path = os.path.join("avatars_cache", filename)
            with open(self.opponent_avatar_path, "wb") as f:
                f.write(data)
        else:
            self.opponent_avatar_path = ""

        return {
            "your_avatar_path": self.your_avatar_path,
            "opponent_avatar_path": self.opponent_avatar_path
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
            self.send_line(json.dumps(move))
        except:
            pass

    def send_play_again(self):
        try:
            self.send_line(json.dumps({"type": "play_again"}))
        except:
            pass

    def reset_game_state(self):
        self.board = [["", "", ""], ["", "", ""], ["", "", ""]]
        self.current_turn = "X"
        self.your_turn = False
        self.winner = None
        self.your_symbol = None
        self.opponent_symbol = None
        self.opponent_login = ""
        self.opponent_name = ""
        self.your_avatar_path = ""
        self.opponent_avatar_path = ""

    def send_line(self, text):
        token = self.cipher_suite.encrypt(text.encode("utf-8"))
        self.client.sendall(token + b"\n")

    def send_bytes(self, data):
        encrypted = self.cipher_suite.encrypt(data)
        self.send_line(str(len(encrypted)))
        self.client.sendall(encrypted)

    def recv_bytes(self):
        size_line = self.recv_line()

        if not size_line:
            return None

        try:
            encrypted_size = int(size_line)
        except:
            return None

        received = 0
        encrypted_data = b""

        while received < encrypted_size:
            chunk = self.client.recv(min(4096, encrypted_size - received))

            if not chunk:
                return None

            encrypted_data += chunk
            received += len(chunk)

        try:
            return self.cipher_suite.decrypt(encrypted_data)
        except:
            return None