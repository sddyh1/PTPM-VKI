import re
from typing import NamedTuple


class Credentials(NamedTuple):
    login: str
    password: str
    confirmation: str


class Result(NamedTuple):
    success: bool
    error: str


FORBIDDEN_LOGINS = {"admin", "root", "administrator", "test", "user", "guest", "support"}
PHONE = re.compile(r"\+\d-\d{3}-\d{3}-\d{4}")
EMAIL = re.compile(r"[^@\s]+@[^@\s]+\.[a-zA-Z]{2,}")
PLAIN_LOGIN = re.compile(r"[A-Za-z0-9_]{5,}")
SPECIAL = r"""!@#$%^&*()_+-=[]{};:'",.<>/?\|~`"""
PASSWORD = re.compile(rf"[А-ЯЁа-яё\d{re.escape(SPECIAL)}]{{7,}}")


class RegistrationValidator:
    def register(self, data: Credentials) -> Result:
        login, password, confirmation = data
        if not login:
            return Result(False, "Логин не может быть пустым")
        if login.lower() in FORBIDDEN_LOGINS:
            return Result(False, "Логин в чс")
        if not (PHONE.fullmatch(login) or EMAIL.fullmatch(login)):
            if "@" in login or login.count("-") >= 2:
                return Result(False, "формат не соответствует email или телефона не соответсвуют")
            if not PLAIN_LOGIN.fullmatch(login):
                return Result(False, "Логин-строка: латиница,цифры,_  минимум 5 символов")

        if not password:
            return Result(False, "Пароль не может быть пустым")
        if not PASSWORD.fullmatch(password):
            return Result(False, "Пароль: только кириллица/цифры/спецсимволы, минимум 7 символов")
        if not re.search(r"[А-ЯЁ]", password):
            return Result(False, "Нужна заглавная буква")
        if not re.search(r"[а-яё]", password):
            return Result(False, "Нужна строчная буква")
        if not re.search(r"\d", password):
            return Result(False, "Нужна цифра")
        if not any(char in SPECIAL for char in password):
            return Result(False, "Нужен спецсимвол")
        if password != confirmation:
            return Result(False, "Пароль и подтверждение не совпадают")
        return Result(True, "")
