from Client.Model.Client_Model import GameClientModel
from Client.View.Client_View import GameClientView
from Client.Controller.Client_Controller import GameClientController
from Client.config import SERVER_HOST, SERVER_PORT


model = GameClientModel(host=SERVER_HOST, port=SERVER_PORT)
view = GameClientView()
controller = GameClientController(model, view)

view.start()