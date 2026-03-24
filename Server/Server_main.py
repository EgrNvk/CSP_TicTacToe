from Server.GameServer import GameServer
from Server.config import HOST, PORT

server = GameServer(host=HOST, port=PORT)
server.start()