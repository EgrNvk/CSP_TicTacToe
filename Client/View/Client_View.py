import tkinter as tk


class GameClientView:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TicTacToe")
        self.root.geometry("420x520")
        self.root.resizable(False, False)

        self.avatar_path = ""

        self.start_frame = tk.Frame(self.root)
        self.login_frame = tk.Frame(self.root)
        self.register_frame = tk.Frame(self.root)
        self.upload_frame = tk.Frame(self.root)
        self.waiting_frame = tk.Frame(self.root)
        self.game_frame = tk.Frame(self.root)

        self.label_response = tk.Label(self.root, text="", fg="blue")
        self.label_response.pack(pady=5)

        self.build_start_frame()
        self.build_login_frame()
        self.build_register_frame()
        self.build_upload_frame()
        self.build_waiting_frame()
        self.build_game_frame()

        self.show_start()

    def build_start_frame(self):
        tk.Label(self.start_frame, text="Choose action", font=("Arial", 14)).pack(pady=10)

        self.btn_choose_login = tk.Button(self.start_frame, text="Login")
        self.btn_choose_login.pack(pady=5)

        self.btn_choose_register = tk.Button(self.start_frame, text="Register")
        self.btn_choose_register.pack(pady=5)

    def build_login_frame(self):
        tk.Label(self.login_frame, text="Login").grid(row=0, column=0, padx=5, pady=5)
        self.login_entry = tk.Entry(self.login_frame)
        self.login_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self.login_frame, text="Password").grid(row=1, column=0, padx=5, pady=5)
        self.password_entry = tk.Entry(self.login_frame, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)

        self.btn_login = tk.Button(self.login_frame, text="Login")
        self.btn_login.grid(row=2, column=0, columnspan=2, pady=10)

        self.btn_back_login = tk.Button(self.login_frame, text="Back")
        self.btn_back_login.grid(row=3, column=0, columnspan=2, pady=5)

    def build_register_frame(self):
        tk.Label(self.register_frame, text="ПІБ").grid(row=0, column=0, padx=5, pady=5)
        self.reg_name = tk.Entry(self.register_frame)
        self.reg_name.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self.register_frame, text="Login").grid(row=1, column=0, padx=5, pady=5)
        self.reg_login = tk.Entry(self.register_frame)
        self.reg_login.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(self.register_frame, text="Password").grid(row=2, column=0, padx=5, pady=5)
        self.reg_password = tk.Entry(self.register_frame, show="*")
        self.reg_password.grid(row=2, column=1, padx=5, pady=5)

        self.btn_register = tk.Button(self.register_frame, text="Register")
        self.btn_register.grid(row=3, column=0, columnspan=2, pady=10)

        self.btn_back_register = tk.Button(self.register_frame, text="Back")
        self.btn_back_register.grid(row=4, column=0, columnspan=2, pady=5)

    def build_upload_frame(self):
        tk.Label(self.upload_frame, text="Завантаж аватар", font=("Arial", 14)).pack(pady=10)

        self.label_upload_path = tk.Label(self.upload_frame, text="Файл не вибрано")
        self.label_upload_path.pack(pady=5)

        self.upload_path_entry = tk.Entry(self.upload_frame, width=35)
        self.upload_path_entry.pack(pady=5)

        self.btn_upload = tk.Button(self.upload_frame, text="Upload")
        self.btn_upload.pack(pady=5)

        self.btn_back_upload = tk.Button(self.upload_frame, text="Back")
        self.btn_back_upload.pack(pady=5)

    def build_waiting_frame(self):
        self.label_waiting = tk.Label(
            self.waiting_frame,
            text="Очікування суперника...",
            font=("Arial", 14)
        )
        self.label_waiting.pack(pady=30)

    def build_game_frame(self):
        self.label_players = tk.Label(self.game_frame, text="", font=("Arial", 12))
        self.label_players.pack(pady=5)

        self.label_status = tk.Label(self.game_frame, text="Очікування...", font=("Arial", 14))
        self.label_status.pack(pady=10)

        self.frame_board = tk.Frame(self.game_frame)
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

    def show_frame(self, frame):
        self.start_frame.pack_forget()
        self.login_frame.pack_forget()
        self.register_frame.pack_forget()
        self.upload_frame.pack_forget()
        self.waiting_frame.pack_forget()
        self.game_frame.pack_forget()

        frame.pack(padx=10, pady=10)

    def show_start(self):
        self.show_frame(self.start_frame)

    def show_login(self):
        self.show_frame(self.login_frame)

    def show_register(self):
        self.show_frame(self.register_frame)

    def show_avatar_upload(self):
        self.show_frame(self.upload_frame)

    def show_waiting(self):
        self.show_frame(self.waiting_frame)

    def show_game(self):
        self.show_frame(self.game_frame)

    def get_login(self):
        return self.login_entry.get()

    def get_password(self):
        return self.password_entry.get()

    def get_reg_login(self):
        return self.reg_login.get()

    def get_reg_password(self):
        return self.reg_password.get()

    def get_reg_name(self):
        return self.reg_name.get()

    def get_upload_path(self):
        return self.upload_path_entry.get()

    def set_response(self, text):
        self.label_response.config(text=text)

    def show_message(self, text):
        self.label_response.config(text=text)

    def set_status(self, text):
        self.label_status.config(text=text)

    def set_players_info(self, your_symbol, your_name, opponent_name):
        self.label_players.config(
            text=f"Ви: {your_name} ({your_symbol})   |   Суперник: {opponent_name}"
        )

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

    def start(self):
        self.root.mainloop()