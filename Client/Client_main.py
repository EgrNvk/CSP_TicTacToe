from Client.Model.Client_Model import GameClientModel
from Client.View.Client_View import GameClientView
from Client.Controller.Client_Controller import GameClientController


model = GameClientModel()
view = GameClientView()
controller = GameClientController(model, view)

view.start()