import json
import os
import hashlib


class GameClient:
    def __init__(self, conn, addr, users_file, images_dir, users_lock):
        self.conn = conn
        self.addr = addr

        self.users_file = users_file
        self.images_dir = images_dir
        self.users_lock = users_lock

        self.login = ""
        self.name = ""
        self.image = ""
        self.state = "connected"

    def prepare(self):
        try:
            self.state = "auth_pending"

            auth_data = self.recv_json()

            if auth_data is None:
                self.safe_close()
                return False

            action = auth_data.get("action")
            login = auth_data.get("login")
            password = auth_data.get("password")
            name = auth_data.get("name", "")

            if not action or not login or not password:
                self.send_line("ERROR BAD REQUEST")
                self.safe_close()
                return False

            success, response, stored_name, stored_image = self.process_auth(
                action,
                login,
                password,
                name
            )

            self.send_line(response)

            if not success:
                self.safe_close()
                return False

            self.login = login
            self.name = stored_name
            self.image = stored_image
            self.state = "authorized"

            if not self.image:
                self.send_line("AVATAR_REQUIRED")

                uploaded = self.handle_avatar_upload()

                if not uploaded:
                    self.safe_close()
                    return False

                self.send_line("AVATAR_OK")
            else:
                self.send_line("AVATAR_OK")

            self.state = "ready_for_match"
            return True

        except Exception as e:
            print(f"Помилка підготовки клієнта {self.addr}: {e}")
            self.safe_close()
            return False

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

    def handle_avatar_upload(self):
        try:
            command = self.recv_line()

            if command != "UPLOAD":
                self.send_line("ERROR UPLOAD REQUIRED")
                return False

            login = self.recv_line()
            name = self.recv_line()
            ext = self.recv_line()
            size_line = self.recv_line()

            if not login or not ext or not size_line:
                self.send_line("ERROR BAD UPLOAD HEADER")
                return False

            if login != self.login:
                self.send_line("ERROR LOGIN MISMATCH")
                return False

            file_size = int(size_line)

            os.makedirs(self.images_dir, exist_ok=True)

            filename = f"{login}_{name}{ext}"
            filepath = os.path.join(self.images_dir, filename)

            received = 0

            with open(filepath, "wb") as f:
                while received < file_size:
                    data = self.conn.recv(min(4096, file_size - received))

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
                    self.send_line("ERROR USER NOT FOUND")
                    return False

            self.image = filename
            self.send_line("OK FILE UPLOADED")

            return True

        except Exception as e:
            print(f"Upload error {self.addr}: {e}")
            self.send_line("ERROR UPLOAD FAILED")
            return False

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

    def recv_line(self):
        data = b""

        while True:
            b = self.conn.recv(1)

            if not b:
                return ""

            if b == b"\n":
                break

            data += b

        return data.decode("utf-8", errors="replace")

    def recv_json(self):
        line = self.recv_line()

        if not line:
            return None

        try:
            return json.loads(line)
        except:
            return None

    def send_line(self, text):
        self.conn.sendall((text + "\n").encode("utf-8"))

    def safe_close(self):
        try:
            self.conn.close()
        except:
            pass