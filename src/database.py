import sqlite3


class RegistrationDatabase:
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS registrations (
                login TEXT NOT NULL,
                password TEXT NOT NULL,
                confirmation TEXT NOT NULL,
                success INTEGER NOT NULL CHECK (success IN (0, 1)),
                error TEXT NOT NULL,
                PRIMARY KEY (login, password, confirmation)
            )
        """)

    def get(self, data):
        
        row = self.connection.execute("""
            SELECT success, error FROM registrations
            WHERE login = ? AND password = ? AND confirmation = ?
        """, data).fetchone()

        if row is None:
            return None
        
        success, error = row
        return bool(success), error

    def add(self, data, result) -> None:
        self.connection.execute("""
            INSERT INTO registrations (login, password, confirmation, success, error)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT (login, password, confirmation) DO NOTHING
        """, data + result)
        self.connection.commit()

    def delete(self, data) -> None:
        self.connection.execute("""
            DELETE FROM registrations
            WHERE login = ? AND password = ? AND confirmation = ?
        """, data)
        self.connection.commit()
