import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from my_project import validate_login, validate_password

VALID_PASSWORD = "Пароль1!"


class TestValidateLogin(unittest.TestCase):

    def test_empty_login_is_rejected(self):
        self.assertEqual(validate_login(""), (False, "Логин не может быть пустым"))

    def test_forbidden_login_in_uppercase_is_rejected(self):
        self.assertEqual(validate_login("ADMIN"), (False, "Логин в чс"))

    def test_valid_phone_is_accepted(self):
        self.assertEqual(validate_login("+7-913-123-4567"), (True, ""))

    def test_valid_email_is_accepted(self):
        self.assertEqual(validate_login("student@mail.ru"), (True, ""))

    def test_plain_login_with_four_chars_is_rejected(self):
        ok, error = validate_login("abc1")
        self.assertFalse(ok)
        self.assertIn("минимум 5 символов", error)

    def test_login_with_trailing_newline_is_rejected(self):
        self.assertFalse(validate_login("student\n")[0])


class TestValidatePassword(unittest.TestCase):

    def test_valid_password_is_accepted(self):
        self.assertEqual(validate_password(VALID_PASSWORD, VALID_PASSWORD), (True, ""))

    def test_password_without_uppercase_is_rejected(self):
        self.assertEqual(validate_password("пароль1!", "пароль1!"), (False, "Нужна заглавная буква"))

    def test_password_mismatch_with_confirm_is_rejected(self):
        self.assertEqual(
            validate_password(VALID_PASSWORD, "Пароль2!"),
            (False, "Пароль и подтверждение не совпадают"),
        )

    def test_password_with_trailing_newline_is_rejected(self):
        self.assertFalse(validate_password("Пароль1!\n", "Пароль1!\n")[0])


if __name__ == "__main__":
    unittest.main()
