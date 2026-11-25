import sqlite3
from contextlib import closing

from adapters import ConsoleInput, SimulatedServer
from controller import Controller
from database import RegistrationDatabase
from registration import RegistrationValidator


def main():
    with closing(sqlite3.connect("registration.sqlite3")) as connection:
        controller = Controller(ConsoleInput(), RegistrationDatabase(connection),
                                RegistrationValidator(), SimulatedServer())
        return controller.run()


if __name__ == "__main__":
    main()
