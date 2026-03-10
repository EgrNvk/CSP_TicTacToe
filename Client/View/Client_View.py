import tkinter as tk


class GameClientView:
    def __init__(self, root):
        self.root = root
        self.root.title("TicTacToe")
        self.root.geometry("360x360")
        self.root.resizable(False, False)

        self.label_status = tk.Label(self.root, text="Очікування...", font=("Arial", 14))
        self.label_status.pack(pady=10)

        self.frame_board = tk.Frame(self.root)
        self.frame_board.pack()

        self.buttons = []

        for row in range(3):
            button_row = []

            for col in range(3):
                button = tk.Button(
                    self.frame_board,
                    text="",
                    font=("Arial", 24),
                    width=5,
                    height=2
                )
                button.grid(row=row, column=col, padx=2, pady=2)
                button_row.append(button)

            self.buttons.append(button_row)

    def set_status(self, text):
        self.label_status.config(text=text)

    def draw_board(self, board):
        for row in range(3):
            for col in range(3):
                self.buttons[row][col].config(text=board[row][col])

    def set_buttons_state(self, state):
        for row in range(3):
            for col in range(3):
                self.buttons[row][col].config(state=state)

    def bind_buttons(self, callback):
        for row in range(3):
            for col in range(3):
                self.buttons[row][col].config(
                    command=lambda r=row, c=col: callback(r, c)
                )

    def update_view(self, board, your_turn, winner):
        for row in range(3):
            for col in range(3):
                value = board[row][col]

                if value == "" and your_turn and winner is None:
                    state = "normal"
                else:
                    state = "disabled"

                self.buttons[row][col].config(text=value, state=state)

        if winner == "X" or winner == "O":
            self.label_status.config(text=f"Переміг {winner}")
        else:
            if your_turn:
                self.label_status.config(text="Ваш хід")
            else:
                self.label_status.config(text="Хід суперника")