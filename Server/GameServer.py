import socket
import threading

from Server.GameClient import GameClient
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

            thread = threading.Thread(
                target=self.handle_new_connection,
                args=(conn, addr),
                daemon=True
            )
            thread.start()

    def handle_new_connection(self, conn, addr):
        client = GameClient(
            conn=conn,
            addr=addr,
            users_file=self.users_file,
            images_dir=self.images_dir,
            users_lock=self.users_lock
        )

        ready = client.prepare()

        if not ready:
            return

        self.add_to_matchmaking(client)

    def add_to_matchmaking(self, client):
        with self.match_lock:
            if self.waiting_player is None:
                self.waiting_player = client
                client.state = "waiting_opponent"

                client.send_line("WAITING_FOR_OPPONENT")
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

            player_x.send_line("OPPONENT_FOUND")
            player_o.send_line("OPPONENT_FOUND")

            session.start()