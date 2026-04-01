import pyodbc
from Server.config import DB_SERVER, DB_DATABASE


def _get_connection():
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={DB_SERVER};"
        f"DATABASE={DB_DATABASE};"
        f"Trusted_Connection=yes;"
    )
    return pyodbc.connect(conn_str)


class UserRepository:
    def find_by_login(self, login: str) -> dict | None:
        with _get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT Login, Password_hash, Name, Image FROM users WHERE Login = ?",
                (login,)
            )
            row = cursor.fetchone()

        if row is None:
            return None

        return {
            "login": row.Login,
            "password_hash": row.Password_hash,
            "name": row.Name or "",
            "image": row.Image or ""
        }

    def create_user(self, login: str, password_hash: str, name: str) -> bool:
        try:
            with _get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO users (Login, Password_hash, Name, Image) VALUES (?, ?, ?, ?)",
                    (login, password_hash, name, "")
                )
                conn.commit()
            return True
        except pyodbc.IntegrityError:
            return False

    def get_all_users(self) -> list:
        with _get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT Login FROM users ORDER BY Login")
            rows = cursor.fetchall()

        return [{"login": row.Login} for row in rows]

    def save_game(self, game_id: int, login: str, opponent_login: str, result: str) -> None:
        with _get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO game_history (game_id, login, opponent_login, result) VALUES (?, ?, ?, ?)",
                (game_id, login, opponent_login, result)
            )
            conn.commit()

    def get_user_history(self, login: str) -> list:
        with _get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT game_id, opponent_login, result, played_at
                FROM game_history
                WHERE login = ?
                ORDER BY played_at DESC
                """,
                (login,)
            )
            rows = cursor.fetchall()

        return [
            {
                "game_id": row.game_id,
                "opponent_login": row.opponent_login,
                "result": row.result,
                "played_at": row.played_at.strftime("%Y-%m-%d %H:%M")
            }
            for row in rows
        ]

    def save_move(self, game_id, move_number, login, player_symbol, row_num, col_num):
        with _get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO game_moves (game_id, move_number, login, player_symbol, row_num, col_num)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (game_id, move_number, login, player_symbol, row_num, col_num)
            )
            conn.commit()

    def get_game_moves(self, game_id):
        with _get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT move_number, login, player_symbol, row_num, col_num, played_at
                FROM game_moves
                WHERE game_id = ?
                ORDER BY move_number ASC
                """,
                (game_id,)
            )
            rows = cursor.fetchall()

        return [
            {
                "move_number": row.move_number,
                "login": row.login,
                "player": row.player_symbol,
                "row": row.row_num,
                "col": row.col_num,
                "position": f"({row.row_num}, {row.col_num})",
                "played_at": row.played_at.strftime("%Y-%m-%d %H:%M:%S")
            }
            for row in rows
        ]

    def update_image(self, login: str, filename: str) -> bool:
        with _get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET Image = ? WHERE Login = ?",
                (filename, login)
            )
            conn.commit()
            return cursor.rowcount > 0