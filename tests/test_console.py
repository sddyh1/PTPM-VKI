import runpy
import unittest
from sqlite3 import connect
from unittest.mock import patch

from src.adapters import ConsoleInput, SimulatedServer
from src.database import RegistrationDatabase


class ConsoleTests(unittest.TestCase):
    @patch("builtins.input")
    def test_console_input(self, keyboard):
        keyboard.side_effect = ["student", "пароль", "повтор"]
        data = ConsoleInput().read()
        self.assertEqual(data, ("student", "пароль", "повтор"))

    @patch("builtins.print")
    def test_server_message(self, output):
        SimulatedServer().send("Готово")
        output.assert_called_once_with("[Имитация сервера] Готово")

    @patch("sqlite3.connect")
    def test_import(self, open_database):
        runpy.run_module("main")
        open_database.assert_not_called()

    @patch("sqlite3.connect")
    @patch("builtins.input")
    @patch("builtins.print")
    def test_program_start(self, output, keyboard, open_database):
        data = ("student@example.org", "Учебный7!", "Учебный7!")
        keyboard.side_effect = data
        connection = connect("test_registration.sqlite3")
        self.addCleanup(connection.close)
        RegistrationDatabase(connection).delete(data)
        open_database.return_value = connection
        runpy.run_module("main", run_name="__main__")
        output.assert_called_once_with("[Имитация сервера] Регистрация успешна")
