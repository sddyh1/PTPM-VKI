import runpy
import sqlite3
import unittest
from unittest.mock import patch

from src.adapters import ConsoleInput, SimulatedServer


class ConsoleTests(unittest.TestCase):
    def test_console_input(self):
        with patch("builtins.input", side_effect=["student", "пароль", "повтор"]):
            data = ConsoleInput().read()
        self.assertEqual(data, ("student", "пароль", "повтор"))

    def test_server_message(self):
        with patch("builtins.print") as output:
            SimulatedServer().send("Готово")
        output.assert_called_once_with("[Имитация сервера] Готово")

    def test_import(self):
        with patch("sqlite3.connect") as connect:
            runpy.run_module("main")
        connect.assert_not_called()

    def test_program_start(self):
        connection = sqlite3.connect(":memory:")
        with (
            patch("sqlite3.connect", return_value=connection),
            patch("builtins.input", side_effect=["student@example.org", "Учебный7!", "Учебный7!"]),
            patch("builtins.print") as output,
        ):
            runpy.run_module("main", run_name="__main__")
        output.assert_called_once_with("[Имитация сервера] Регистрация успешна")
