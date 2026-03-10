import tkinter as tk

from Client.Model.Client_Model import GameClientModel
from Client.View.Client_View import GameClientView
from Client.Controller.Client_Controller import GameClientController


root = tk.Tk()

model = GameClientModel()
view = GameClientView(root)
controller = GameClientController(model, view)

root.mainloop()