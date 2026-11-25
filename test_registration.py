import io
import os
import runpy
import sqlite3
import unittest
from contextlib import closing, redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock, call, create_autospec, patch

from adapters import ConsoleInput, ResultSender, SimulatedServer, UserInput
from controller import Controller
from database import RegistrationDatabase
from registration import Credentials, RegistrationValidator, Result


SUCCESS = "Регистрация успешна"
PASSWORD = "Учебный7!"
VALID = Credentials("student_3", PASSWORD, PASSWORD)


class ControllerIntegrationTests(unittest.TestCase):
    def setUp(self):
        connection = sqlite3.connect(":memory:")
        self.addCleanup(connection.close)
        self.db = RegistrationDatabase(connection)
        self.user = create_autospec(UserInput, instance=True)
        self.user.read.return_value = VALID
        self.sender = create_autospec(ResultSender, instance=True)
        self.validator = Mock(wraps=RegistrationValidator())
        self.controller = Controller(self.user, self.db, self.validator, self.sender)

    def test_new_attempt_is_saved_before_result_is_sent(self):
        def check_saved(message):
            self.assertEqual(self.db.get(VALID), Result(True, ""))
            self.assertEqual(message, SUCCESS)

        self.sender.send.side_effect = check_saved
        self.assertEqual(self.controller.run(), SUCCESS)
        self.user.read.assert_called_once_with()
        self.validator.register.assert_called_once_with(VALID)
        self.sender.send.assert_called_once_with(SUCCESS)

    def test_cached_failure_is_sent_without_validation_or_insert(self):
        error = "Сохранённый отказ"
        self.db.add(VALID, Result(False, error))
        with patch.object(self.db, "add", wraps=self.db.add) as add:
            self.assertEqual(self.controller.run(), error)
        add.assert_not_called()
        self.validator.register.assert_not_called()
        self.sender.send.assert_called_once_with(error)

    def test_changing_each_input_creates_a_separate_attempt(self):
        other_password = "Учебный8!"
        attempts = [
            VALID,
            VALID._replace(login="student@example.org"),
            VALID._replace(confirmation=other_password),
            VALID._replace(password=other_password),
            VALID,
        ]
        mismatch = "Пароль и подтверждение не совпадают"
        expected = [SUCCESS, SUCCESS, mismatch, mismatch, SUCCESS]
        self.user.read.side_effect = attempts
        self.assertEqual([self.controller.run() for _ in attempts], expected)
        self.assertEqual(self.validator.register.call_args_list, [call(a) for a in attempts[:4]])
        self.assertEqual(self.sender.send.call_args_list, [call(m) for m in expected])

    def test_delete_only_removes_selected_attempt_and_forces_recalculation(self):
        other = VALID._replace(login="+7-901-111-2222")
        self.user.read.side_effect = [VALID, other, VALID]
        self.controller.run()
        self.controller.run()
        self.db.delete(VALID)
        self.assertIsNone(self.db.get(VALID))
        self.assertEqual(self.db.get(other), Result(True, ""))
        self.assertEqual(self.controller.run(), SUCCESS)
        self.assertEqual(self.validator.register.call_args_list, [call(VALID), call(other), call(VALID)])

    def test_rejections_reach_database_sender_and_caller(self):
        cases = [
            ("", PASSWORD, "Логин не может быть пустым"),
            ("Root", PASSWORD, "Логин в чс"),
            ("student@", PASSWORD, "формат не соответствует email или телефона не соответсвуют"),
            ("а б", PASSWORD, "Логин-строка: латиница,цифры,_  минимум 5 символов"),
            ("student_3", "", "Пароль не может быть пустым"),
            ("student_3", "Latin12!", "Пароль: только кириллица/цифры/спецсимволы, минимум 7 символов"),
            ("student_3", "учебный7!", "Нужна заглавная буква"),
            ("student_3", "УЧЕБНЫЙ7!", "Нужна строчная буква"),
            ("student_3", "Учебный!!", "Нужна цифра"),
            ("student_3", "Учебный77", "Нужен спецсимвол"),
        ]
        for login, password, error in cases:
            with self.subTest(login=login, error=error):
                data = Credentials(login, password, password)
                self.user.read.return_value = data
                self.assertEqual(self.controller.run(), error)
                self.assertEqual(self.db.get(data), Result(False, error))
                self.sender.send.assert_called_with(error)

    def test_retry_after_sender_failure_reuses_saved_result(self):
        self.sender.send.side_effect = [ConnectionError("Сервис недоступен"), None]
        with self.assertRaises(ConnectionError):
            self.controller.run()
        self.assertEqual(self.controller.run(), SUCCESS)
        self.validator.register.assert_called_once_with(VALID)
        self.assertEqual(self.sender.send.call_args_list, [call(SUCCESS), call(SUCCESS)])


class AdapterTests(unittest.TestCase):
    def test_console_reads_confirmation_separately(self):
        with patch("builtins.input", return_value="student_3"), \
             patch("adapters.getpass", side_effect=["первый", "второй"]):
            self.assertEqual(ConsoleInput().read(), Credentials("student_3", "первый", "второй"))

    def test_simulated_server_prints_only_result(self):
        with patch("builtins.print") as output:
            SimulatedServer().send(SUCCESS)
        output.assert_called_once_with("[Имитация сервера] Регистрация успешна")


class ApplicationIntegrationTests(unittest.TestCase):
    def test_console_entry_point_persists_result_after_exit(self):
        script = Path(__file__).with_name("main.py").resolve()
        with TemporaryDirectory() as folder:
            previous_dir = Path.cwd()
            try:
                os.chdir(folder)
                with patch("builtins.input", return_value=VALID.login), \
                     patch("adapters.getpass", side_effect=[PASSWORD, PASSWORD]), \
                     redirect_stdout(io.StringIO()) as output:
                    runpy.run_path(str(script), run_name="__main__")
                self.assertEqual(output.getvalue().strip(), "[Имитация сервера] " + SUCCESS)
                with closing(sqlite3.connect("registration.sqlite3")) as connection:
                    self.assertEqual(RegistrationDatabase(connection).get(VALID), Result(True, ""))
            finally:
                os.chdir(previous_dir)

    def test_import_does_not_start_registration(self):
        script = Path(__file__).with_name("main.py")
        with patch("sqlite3.connect") as connect, patch("builtins.input") as read:
            runpy.run_path(str(script), run_name="main")
        connect.assert_not_called()
        read.assert_not_called()
