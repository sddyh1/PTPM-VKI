import sqlite3
from contextlib import closing

from src.adapters import ConsoleInput, SimulatedServer
from src.controller import Controller
from src.database import RegistrationDatabase
from src.registration import RegistrationValidator


def main():
    with closing(sqlite3.connect("registration.sqlite3")) as connection:
        database = RegistrationDatabase(connection)
        controller = Controller(ConsoleInput(), database, RegistrationValidator(), SimulatedServer())
        return controller.run()


if __name__ == "__main__":
    main()
