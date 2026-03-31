import json
import socket
import threading
from cryptography.fernet import Fernet

from Server.config import FERNET_KEY, ADMIN_HOST, ADMIN_PORT, ADMIN_LOGIN, ADMIN_PASSWORD_HASH


class AdminServer:
    def __init__(self, game_server):
        self.game_server = game_server
        self.host = ADMIN_HOST
        self.port = ADMIN_PORT
        self.server_socket = None
        self.cipher_suite = Fernet(FERNET_KEY)

    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)

        print(f"Адмін-сервер запущено на {self.host}:{self.port}")

        while True:
            conn, addr = self.server_socket.accept()
            print(f"Адмін підключився: {addr}")

            threading.Thread(
                target=self.handle_admin,
                args=(conn, addr),
                daemon=True
            ).start()

    def handle_admin(self, conn, addr):
        authenticated = False

        while True:
            data = self.recv_json(conn)

            if data is None:
                break

            msg_type = data.get("type")

            if not authenticated:
                if msg_type == "admin_auth":
                    login = data.get("login")
                    password_hash = data.get("password_hash")

                    if login == ADMIN_LOGIN and password_hash == ADMIN_PASSWORD_HASH:
                        authenticated = True
                        self.send_json(conn, {
                            "type": "auth_ok"
                        })
                    else:
                        self.send_json(conn, {
                            "type": "auth_error"
                        })
                        break

                continue

            if msg_type == "get_sessions":
                sessions = self.get_sessions()
                self.send_json(conn, {
                    "type": "sessions_list",
                    "sessions": sessions
                })

            elif msg_type == "kick_player":
                session_id = data.get("session_id")
                symbol = data.get("symbol")

                self.kick_player(session_id, symbol)

                self.send_json(conn, {
                    "type": "kick_ok"
                })

            elif msg_type == "close_session":
                session_id = data.get("session_id")

                self.close_session(session_id)

                self.send_json(conn, {
                    "type": "close_ok"
                })

            elif msg_type == "get_users":
                users = self.get_users()
                self.send_json(conn, {
                    "type": "users_list",
                    "users": users
                })

            elif msg_type == "get_user_history":
                login = data.get("login")
                history = self.get_user_history(login)
                self.send_json(conn, {
                    "type": "user_history",
                    "history": history
                })

        try:
            conn.close()
        except:
            pass

        print(f"Адмін відключився: {addr}")

    def get_sessions(self):
        result = []

        for session in self.game_server.sessions:
            try:
                result.append(session.get_info())
            except:
                pass

        return result

    def get_users(self):
        try:
            return self.game_server.user_repo.get_all_users()
        except:
            return []

    def get_user_history(self, login):
        try:
            return self.game_server.user_repo.get_user_history(login)
        except:
            return []

    def kick_player(self, session_id, symbol):
        for session in self.game_server.sessions:
            try:
                if session.session_id == session_id:
                    session.kick_player(symbol)
                    break
            except:
                pass

    def close_session(self, session_id):
        for session in self.game_server.sessions:
            try:
                if session.session_id == session_id:
                    session.close_session()
                    break
            except:
                pass

    def recv_line(self, conn):
        token = b""

        while True:
            try:
                b = conn.recv(1)
            except:
                return ""

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

    def recv_json(self, conn):
        line = self.recv_line(conn)

        if not line:
            return None

        try:
            return json.loads(line)
        except:
            return None

    def send_line(self, conn, text):
        try:
            token = self.cipher_suite.encrypt(text.encode("utf-8"))
            conn.sendall(token + b"\n")
        except:
            pass

    def send_json(self, conn, data):
        try:
            text = json.dumps(data)
            self.send_line(conn, text)
        except:
            pass