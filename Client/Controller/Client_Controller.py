import threading


class GameClientController:
    def __init__(self, model, view):
        self.model = model
        self.view = view

        self.view.bind_buttons(self.click_cell)

        self.view.btn_choose_login.config(command=self.view.show_login)
        self.view.btn_choose_register.config(command=self.view.show_register)

        self.view.btn_back_login.config(command=self.back_to_start)
        self.view.btn_back_register.config(command=self.back_to_start)
        self.view.btn_back_upload.config(command=self.back_to_start)

        self.view.btn_login.config(command=self.login)
        self.view.btn_register.config(command=self.register)
        self.view.btn_upload.config(command=self.upload_avatar)
        self.view.btn_continue.config(command=self.play_again)

    def back_to_start(self):
        self.view.show_start()
        self.view.show_message("")

    def login(self):
        login = self.view.get_login()
        password = self.view.get_password()

        if not login or not password:
            self.view.show_message("Введи login і password")
            return

        try:
            self.model.connect()
        except Exception as e:
            self.view.show_message(f"Помилка підключення: {e}")
            return

        response = self.model.send_form("login", login, password)

        if response != "OK LOGIN":
            self.view.show_message(response)
            self.model.close()
            return

        self.view.show_message(response)

        avatar_status = self.model.receive_avatar_status()

        if avatar_status == "AVATAR_REQUIRED":
            self.view.show_avatar_upload()
            self.view.show_message("Потрібно завантажити аватар")
            return

        if avatar_status == "AVATAR_OK":
            self.start_waiting()
            return

        self.view.show_message(avatar_status)
        self.model.close()

    def register(self):
        name = self.view.get_reg_name()
        login = self.view.get_reg_login()
        password = self.view.get_reg_password()

        if not name or not login or not password:
            self.view.show_message("Заповни всі поля")
            return

        try:
            self.model.connect()
        except Exception as e:
            self.view.show_message(f"Помилка підключення: {e}")
            return

        response = self.model.send_form("register", login, password, name)

        if response != "OK REGISTER":
            self.view.show_message(response)
            self.model.close()
            return

        self.view.show_message(response)

        avatar_status = self.model.receive_avatar_status()

        if avatar_status == "AVATAR_REQUIRED":
            self.view.show_avatar_upload()
            self.view.show_message("Реєстрація успішна. Завантаж аватар")
            return

        if avatar_status == "AVATAR_OK":
            self.start_waiting()
            return

        self.view.show_message(avatar_status)
        self.model.close()

    def upload_avatar(self):
        path = self.view.get_upload_path()

        if not path:
            self.view.show_message("Вкажи шлях до файлу")
            return

        response = self.model.send_file(self.model.current_login, path)

        if response != "OK FILE UPLOADED":
            self.view.show_message(response)
            self.model.close()
            return

        avatar_status = self.model.receive_avatar_status()

        if avatar_status != "AVATAR_OK":
            self.view.show_message(avatar_status)
            self.model.close()
            return

        self.start_waiting()

    def start_waiting(self):
        self.view.show_waiting()
        self.view.show_message("")

        thread = threading.Thread(target=self.wait_for_game_start, daemon=True)
        thread.start()

    def wait_for_game_start(self):
        while True:
            status = self.model.receive_match_status()

            if not status:
                self.view.root.after(0, self.view.show_message, "З'єднання втрачено")
                return

            if status == "WAITING_FOR_OPPONENT":
                self.view.root.after(0, self.view.show_waiting)
                continue

            if status == "OPPONENT_FOUND":
                break

            self.view.root.after(0, self.view.show_message, status)
            return

        start_info = self.model.receive_start_info()

        if not start_info:
            self.view.root.after(0, self.view.show_message, "Помилка старту гри")
            return

        self.model.receive_avatars()

        first_state = self.model.receive()

        if not first_state:
            self.view.root.after(0, self.view.show_message, "Не отримано стан гри")
            return

        self.view.root.after(0, self.start_game)

        thread = threading.Thread(target=self.receive_loop, daemon=True)
        thread.start()

    def start_game(self):
        self.view.show_game()
        self.view.set_players_info(
            self.model.your_symbol,
            self.model.your_name,
            self.model.opponent_name
        )

        self.view.set_avatars(
            self.model.your_avatar_path,
            self.model.opponent_avatar_path
        )

        self.view.update_view(
            self.model.board,
            self.model.your_turn,
            self.model.winner,
            self.model.your_symbol
        )

    def click_cell(self, row, col):
        if self.model.your_turn and self.model.winner is None:
            self.model.send_move(row, col)

    def receive_loop(self):
        while True:
            message = self.model.receive()

            if not message:
                self.view.root.after(0, self.view.show_message, "З'єднання втрачено")
                break

            self.view.root.after(
                0,
                self.view.update_view,
                self.model.board,
                self.model.your_turn,
                self.model.winner,
                self.model.your_symbol
            )

            if self.model.winner is not None:
                self.view.root.after(0, self.view.show_continue_button)
                break

    def play_again(self):
        self.view.hide_continue_button()
        self.model.send_play_again()
        self.model.reset_game_state()
        self.start_waiting()