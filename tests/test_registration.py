import sqlite3
import unittest
from unittest.mock import Mock, call, patch

from src.adapters import ResultSender, UserInput
from src.controller import Controller
from src.database import RegistrationDatabase
from src.registration import RegistrationValidator


SUCCESS = "Регистрация успешна"
PASSWORD = "Учебный7!"
LOGIN = "student_3"
VALID = (LOGIN, PASSWORD, PASSWORD)


class ControllerIntegrationTests(unittest.TestCase):
    def setUp(self):
        connection = sqlite3.connect(":memory:")
        self.addCleanup(connection.close)
        self.db = RegistrationDatabase(connection)
        self.user = Mock(spec=UserInput)
        self.user.read.return_value = VALID
        self.sender = Mock(spec=ResultSender)
        self.validator = Mock(wraps=RegistrationValidator())
        self.controller = Controller(self.user, self.db, self.validator, self.sender)

    def test_new_attempt_is_saved_before_result_is_sent(self):
        def check_saved(message):
            self.assertEqual(self.db.get(VALID), (True, ""))
            self.assertEqual(message, SUCCESS)

        self.sender.send.side_effect = check_saved
        self.assertEqual(self.controller.run(), SUCCESS)
        self.user.read.assert_called_once_with()
        self.validator.register.assert_called_once_with(VALID)
        self.sender.send.assert_called_once_with(SUCCESS)

    def test_cached_failure_is_sent_without_validation_or_insert(self):
        error = "Сохранённый отказ"
        self.db.add(VALID, (False, error))
        with patch.object(self.db, "add", wraps=self.db.add) as add:
            self.assertEqual(self.controller.run(), error)
        add.assert_not_called()
        self.validator.register.assert_not_called()
        self.sender.send.assert_called_once_with(error)

    def test_changing_each_input_creates_a_separate_attempt(self):
        changed_login = ("student@example.org", PASSWORD, PASSWORD)
        changed_password = (LOGIN, "Учебный8!", PASSWORD)
        changed_confirmation = (LOGIN, PASSWORD, "Учебный8!")
        mismatch = "Пароль и подтверждение не совпадают"

        for attempt, expected in [
            (VALID, SUCCESS),
            (changed_login, SUCCESS),
            (changed_password, mismatch),
            (changed_confirmation, mismatch),
        ]:
            with self.subTest(attempt=attempt):
                self.user.read.return_value = attempt
                self.assertEqual(self.controller.run(), expected)
                self.validator.register.assert_called_with(attempt)
                self.sender.send.assert_called_with(expected)

        self.user.read.return_value = VALID
        self.assertEqual(self.controller.run(), SUCCESS)
        self.assertEqual(self.validator.register.call_count, 4)

    def test_delete_only_removes_selected_attempt_and_forces_recalculation(self):
        other = ("+7-901-111-2222", PASSWORD, PASSWORD)
        self.user.read.side_effect = [VALID, other, VALID]
        self.controller.run()
        self.controller.run()
        self.db.delete(VALID)
        self.assertIsNone(self.db.get(VALID))
        self.assertEqual(self.db.get(other), (True, ""))
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
                data = (login, password, password)
                self.user.read.return_value = data
                self.assertEqual(self.controller.run(), error)
                self.assertEqual(self.db.get(data), (False, error))
                self.sender.send.assert_called_with(error)

    def test_retry_after_sender_failure_reuses_saved_result(self):
        self.sender.send.side_effect = [ConnectionError("Сервис недоступен"), None]
        with self.assertRaises(ConnectionError):
            self.controller.run()
        self.assertEqual(self.controller.run(), SUCCESS)
        self.validator.register.assert_called_once_with(VALID)
        self.assertEqual(self.sender.send.call_args_list, [call(SUCCESS), call(SUCCESS)])
