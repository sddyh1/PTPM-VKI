import sqlite3
import unittest
from unittest.mock import Mock

from src.controller import Controller
from src.database import RegistrationDatabase
from src.registration import RegistrationValidator


PASSWORD = "Учебный7!"
VALID = ("student_3", PASSWORD, PASSWORD)


class RegistrationTests(unittest.TestCase):
    def setUp(self):
        connection = sqlite3.connect(":memory:")
        self.addCleanup(connection.close)
        self.db = RegistrationDatabase(connection)
        self.user = Mock()
        self.sender = Mock()
        self.user.read.return_value = VALID
        self.controller = Controller(self.user, self.db, RegistrationValidator(), self.sender)

    def test_new_registration(self):
        message = self.controller.run()

        self.assertEqual(message, "Регистрация успешна")
        self.assertEqual(self.db.get(VALID), (True, ""))
        self.sender.send.assert_called_once_with(message)

    def test_saved_result(self):
        self.db.add(VALID, (False, "Сохранённый отказ"))
        message = self.controller.run()

        self.assertEqual(message, "Сохранённый отказ")
        self.sender.send.assert_called_once_with(message)

    def test_different_confirmation(self):
        self.controller.run()
        data = ("student_3", PASSWORD, "Другой пароль")
        self.user.read.return_value = data
        message = self.controller.run()

        self.assertEqual(message, "Пароль и подтверждение не совпадают")
        self.assertEqual(self.db.get(data), (False, message))
        self.assertEqual(self.db.get(VALID), (True, ""))

    def test_delete_registration(self):
        self.controller.run()
        self.db.delete(VALID)

        self.assertIsNone(self.db.get(VALID))

    def test_registration_errors(self):
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
            data = (login, password, password)
            self.user.read.return_value = data
            self.assertEqual(self.controller.run(), error)
            self.assertEqual(self.db.get(data), (False, error))
            self.sender.send.assert_called_with(error)
