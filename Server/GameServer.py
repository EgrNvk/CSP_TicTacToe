import socket
import threading
import json
import os
import hashlib


from Server.GameSession import GameSession


class GameServer:

    def __init__(self, host="127.0.0.1", port=4000):

        self.host = host
        self.port = port

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen()

        self.users_file = "users.json"
        self.images_dir = "images"

        self.users_lock = threading.Lock()
        self.match_lock = threading.Lock()

        self.waiting_player = None
        self.sessions = []
        self.next_session_id = 1


    def start(self):

        print(f"Сервер запущено на {self.host}:{self.port}")

        while True:

            conn, addr = self.server.accept()
            print(f"Підключився клієнт: {addr}")

            client = GameSession(conn, addr)

            thread = threading.Thread(
                target=self.handle_client,
                args=(client,),
                daemon=True
            )

            thread.start()


    def handle_client(self, client):

        try:

            client.state = "auth_pending"

            auth_data = self.recv_json(client.conn)

            if auth_data is None:
                self.safe_close(client)
                return

            action = auth_data.get("action")
            login = auth_data.get("login")
            password = auth_data.get("password")
            name = auth_data.get("name", "")

            if not action or not login or not password:
                self.send_line(client.conn, "ERROR BAD REQUEST")
                self.safe_close(client)
                return

            success, response, stored_name, stored_image = self.process_auth(
                action,
                login,
                password,
                name
            )

            self.send_line(client.conn, response)

            if not success:
                self.safe_close(client)
                return

            client.login = login
            client.name = stored_name
            client.image = stored_image

            client.state = "authorized"

            if not client.image:

                self.send_line(client.conn, "AVATAR_REQUIRED")

                uploaded = self.handle_avatar_upload(client)

                if not uploaded:
                    self.safe_close(client)
                    return

                self.send_line(client.conn, "AVATAR_OK")

            else:

                self.send_line(client.conn, "AVATAR_OK")

            client.state = "ready_for_match"

            self.add_to_matchmaking(client)

        except Exception as e:

            print("Помилка:", e)
            self.safe_close(client)


    def process_auth(self, action, login, password, name):

        with self.users_lock:

            users = self.load_users()

            if action == "register":

                if login in users:
                    return False, "ERROR USER EXISTS", "", ""

                users[login] = {
                    "password": self.hash_password(password),
                    "name": name,
                    "image": ""
                }

                self.save_users(users)

                return True, "OK REGISTER", name, ""

            elif action == "login":

                if login not in users:
                    return False, "ERROR USER NOT FOUND", "", ""

                if users[login]["password"] != self.hash_password(password):
                    return False, "ERROR WRONG PASSWORD", "", ""

                stored_name = users[login].get("name", "")
                stored_image = users[login].get("image", "")

                return True, "OK LOGIN", stored_name, stored_image

            else:
                return False, "ERROR UNKNOWN ACTION", "", ""


    def handle_avatar_upload(self, client):

        try:

            command = self.recv_line(client.conn)

            if command != "UPLOAD":
                self.send_line(client.conn, "ERROR UPLOAD REQUIRED")
                return False

            login = self.recv_line(client.conn)
            name = self.recv_line(client.conn)
            ext = self.recv_line(client.conn)
            size_line = self.recv_line(client.conn)

            file_size = int(size_line)

            os.makedirs(self.images_dir, exist_ok=True)

            filename = f"{login}_{name}{ext}"
            filepath = os.path.join(self.images_dir, filename)

            received = 0

            with open(filepath, "wb") as f:

                while received < file_size:

                    data = client.conn.recv(min(4096, file_size - received))

                    if not data:
                        return False

                    f.write(data)
                    received += len(data)

            with self.users_lock:

                users = self.load_users()

                if login in users:

                    users[login]["image"] = filename
                    self.save_users(users)

                else:

                    self.send_line(client.conn, "ERROR USER NOT FOUND")
                    return False

            client.image = filename

            self.send_line(client.conn, "OK FILE UPLOADED")

            return True

        except Exception as e:

            print("Upload error:", e)
            self.send_line(client.conn, "ERROR UPLOAD FAILED")
            return False


    def add_to_matchmaking(self, client):

        with self.match_lock:

            if self.waiting_player is None:

                self.waiting_player = client
                client.state = "waiting_opponent"

                self.send_line(client.conn, "WAITING_FOR_OPPONENT")

                print(f"Гравець {client.login} очікує пару")

                return

            player_x = self.waiting_player
            player_o = client

            self.waiting_player = None

            session = GameSession(
                session_id=self.next_session_id,
                player_x=player_x,
                player_o=player_o
            )

            self.sessions.append(session)

            print(
                f"Створено сесію #{self.next_session_id}: "
                f"{player_x.login} vs {player_o.login}"
            )

            self.next_session_id += 1

            player_x.state = "in_game"
            player_o.state = "in_game"

            self.send_line(player_x.conn, "OPPONENT_FOUND")
            self.send_line(player_o.conn, "OPPONENT_FOUND")

            session.start()


    def hash_password(self, password):

        return hashlib.sha256(password.encode()).hexdigest()


    def load_users(self):

        if not os.path.exists(self.users_file):
            return {}

        with open(self.users_file, "r", encoding="utf-8") as f:
            return json.load(f)


    def save_users(self, users):

        with open(self.users_file, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=4, ensure_ascii=False)


    def recv_line(self, conn):

        data = b""

        while True:

            b = conn.recv(1)

            if not b:
                break

            if b == b"\n":
                break

            data += b

        return data.decode("utf-8", errors="replace")


    def recv_json(self, conn):

        line = self.recv_line(conn)

        if not line:
            return None

        try:
            return json.loads(line)
        except:
            return None


    def send_line(self, conn, text):

        conn.sendall((text + "\n").encode())


    def safe_close(self, client):

        try:
            client.conn.close()
        except:
            pass


