import threading


class GameClientController:
    def __init__(self, model, view):
        self.model = model
        self.view = view

        self.view.bind_buttons(self.click_cell)

        thread = threading.Thread(target=self.receive_loop, daemon=True)
        thread.start()

    def click_cell(self, row, col):
        if self.model.your_turn and self.model.winner is None:
            self.model.send_move(row, col)

    def receive_loop(self):
        while True:
            message = self.model.receive()

            if message:
                self.view.root.after(
                    0,
                    self.view.update_view,
                    self.model.board,
                    self.model.your_turn,
                    self.model.winner
                )