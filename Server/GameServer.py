import socket
import threading
from Server.GameSession import GameSession


class GameServer:
    def __init__(self, host="127.0.0.1", port=4000):
        self.host = host
        self.port = port

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen()

        self.waiting_player = None
        self.sessions = []
        self.next_session_id = 1

    def start(self):
        print(f"Сервер запущено на {self.host}:{self.port}")

        while True:
            client, addr = self.server.accept()
            print(f"Підключився клієнт: {addr}")

            self.new_client(client, addr)

    def new_client(self, client, addr):
        if self.waiting_player is None:
            self.waiting_player = client
            print(f"Гравець {addr} очікує пару")
        else:
            player_x = self.waiting_player
            player_o = client

            session = GameSession(
                session_id=self.next_session_id,
                player_x=player_x,
                player_o=player_o
            )

            self.sessions.append(session)

            print(f"Створено сесію #{self.next_session_id}")

            self.next_session_id += 1
            self.waiting_player = None

            session.start()