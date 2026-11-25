import sqlite3

from src.adapters import ConsoleInput, SimulatedServer
from src.controller import Controller
from src.database import RegistrationDatabase
from src.registration import RegistrationValidator


def main():
    connection = sqlite3.connect("registration.sqlite3")
    database = RegistrationDatabase(connection)
    controller = Controller(ConsoleInput(), database, RegistrationValidator(), SimulatedServer())

    result = controller.run()
    connection.close()
    return result


if __name__ == "__main__":
    main()
