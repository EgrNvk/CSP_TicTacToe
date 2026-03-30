from Server.GameServer import GameServer
from Server.AdminServer import AdminServer
from Server.config import HOST, PORT
from Server.db.UserRepository import UserRepository

import threading

user_repo = UserRepository()
game_server = GameServer(host=HOST, port=PORT, user_repo=user_repo)
admin_server = AdminServer(game_server)

threading.Thread(target=game_server.start, daemon=True).start()
threading.Thread(target=admin_server.start, daemon=True).start()

while True:
    pass