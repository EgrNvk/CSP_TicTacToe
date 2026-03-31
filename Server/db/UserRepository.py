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

    def update_image(self, login: str, filename: str) -> bool:
        with _get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET Image = ? WHERE Login = ?",
                (filename, login)
            )
            conn.commit()
            return cursor.rowcount > 0