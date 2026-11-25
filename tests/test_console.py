import runpy
import unittest
from sqlite3 import connect
from unittest.mock import Mock, patch

from src.adapters import ConsoleInput, SimulatedServer


class ConsoleTests(unittest.TestCase):
    @patch("builtins.input", new_callable=Mock)
    def test_console_input(self, mock_input):
        mock_input.side_effect = ["student", "пароль", "повтор"]
        data = ConsoleInput().read()
        self.assertEqual(data, ("student", "пароль", "повтор"))

    @patch("builtins.print", new_callable=Mock)
    def test_server_message(self, mock_print):
        SimulatedServer().send("Готово")
        mock_print.assert_called_once_with("[Имитация сервера] Готово")

    @patch("sqlite3.connect", new_callable=Mock)
    def test_import(self, mock_connect):
        runpy.run_module("main")
        mock_connect.assert_not_called()

    @patch("sqlite3.connect", new_callable=Mock)
    @patch("builtins.input", new_callable=Mock)
    @patch("builtins.print", new_callable=Mock)
    def test_program_start(self, mock_print, mock_input, mock_connect):
        mock_input.side_effect = ["student@example.org", "Учебный7!", "Учебный7!"]
        mock_connect.return_value = connect(":memory:")
        self.addCleanup(mock_connect.return_value.close)
        runpy.run_module("main", run_name="__main__")
        mock_print.assert_called_once_with("[Имитация сервера] Регистрация успешна")
