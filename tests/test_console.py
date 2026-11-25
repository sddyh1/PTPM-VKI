import runpy
import sqlite3
import unittest
from contextlib import closing
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from src.adapters import ConsoleInput, SimulatedServer
from src.database import RegistrationDatabase


class ConsoleTests(unittest.TestCase):
    def test_input_reads_password_and_confirmation_separately(self):
        with patch("builtins.input", side_effect=["student_3", "первый", "второй"]):
            data = ConsoleInput().read()
        self.assertEqual(data, ("student_3", "первый", "второй"))

    def test_server_prints_message(self):
        with patch("builtins.print") as output:
            SimulatedServer().send("Регистрация успешна")
        output.assert_called_once_with("[Имитация сервера] Регистрация успешна")

    def test_import_does_not_start_registration(self):
        with patch("sqlite3.connect") as connect, patch("builtins.input") as read:
            runpy.run_module("main", run_name="main")
        connect.assert_not_called()
        read.assert_not_called()

    def test_starting_program_saves_registration(self):
        password = "Учебный7!"
        login = "student_3"
        data = (login, password, password)
        with TemporaryDirectory() as folder:
            path = Path(folder) / "registration.sqlite3"
            connection = sqlite3.connect(path)
            with (
                patch("sqlite3.connect", return_value=connection),
                patch("builtins.input", side_effect=[login, password, password]),
                patch("builtins.print") as output,
            ):
                runpy.run_module("main", run_name="__main__")

            output.assert_called_once_with("[Имитация сервера] Регистрация успешна")
            with closing(sqlite3.connect(path)) as saved:
                self.assertEqual(RegistrationDatabase(saved).get(data), (True, ""))
