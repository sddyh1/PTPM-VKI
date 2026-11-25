import re


FORBIDDEN_LOGINS = {"admin", "root", "administrator", "test", "user", "guest", "support"}
PHONE = re.compile(r"\+\d-\d{3}-\d{3}-\d{4}")
EMAIL = re.compile(r"[^@\s]+@[^@\s]+\.[a-zA-Z]{2,}")
PLAIN_LOGIN = re.compile(r"[A-Za-z0-9_]{5,}")
SPECIAL = r"""!@#$%^&*()_+-=[]{};:'",.<>/?\|`~"""
PASSWORD = re.compile(rf"[А-ЯЁа-яё\d{re.escape(SPECIAL)}]{{7,}}")


def login_error(login):
    if not login:
        return "Логин не может быть пустым"
    if login.lower() in FORBIDDEN_LOGINS:
        return "Логин в чс"
    if PHONE.fullmatch(login) or EMAIL.fullmatch(login):
        return ""
    if "@" in login or login.count("-") >= 2:
        return "формат не соответствует email или телефона не соответсвуют"
    if not PLAIN_LOGIN.fullmatch(login):
        return "Логин-строка: латиница,цифры,_  минимум 5 символов"
    return ""


def password_error(password, confirmation):
    if not password:
        return "Пароль не может быть пустым"
    if not PASSWORD.fullmatch(password):
        return "Пароль: только кириллица/цифры/спецсимволы, минимум 7 символов"
    if not re.search(r"[А-ЯЁ]", password):
        return "Нужна заглавная буква"
    if not re.search(r"[а-яё]", password):
        return "Нужна строчная буква"
    if not re.search(r"\d", password):
        return "Нужна цифра"
    if not any(char in SPECIAL for char in password):
        return "Нужен спецсимвол"
    if password != confirmation:
        return "Пароль и подтверждение не совпадают"
    return ""


class RegistrationValidator:
    def register(self, data):
        login, password, confirmation = data
        error = login_error(login)
        if error != "":
            return False, error

        error = password_error(password, confirmation)
        if error != "":
            return False, error

        return True, ""
