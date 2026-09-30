import hashlib, logging, os, re, sys

LOG_FILE = "logs/file_txt.log"
FORBIDDEN_LOGINS = {"admin", "root", "administrator", "test", "user", "guest", "support"}

PHONE_RE = re.compile(r"^\+\d-\d{3}-\d{3}-\d{4}$")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[a-zA-Z]{2,}$")
PLAIN_LOGIN_RE = re.compile(r"^[A-Za-z0-9_]{5,}$")

SPECIAL = r"!@#$%^&*()_+\-=\[\]{};:'\",.<>/?\\|`~"
PASSWORD_RE = re.compile(rf"^[А-ЯЁа-яё\d{SPECIAL}]{{7,}}$")


def setup_logging():
    
    os.makedirs("logs", exist_ok=True)
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s | [%(levelname)-7s] | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler(LOG_FILE, encoding="utf-8")],
    )


def mask(password):
    return  hashlib.sha256(password.encode()).hexdigest()[:8] 


def validate_login(login):
    if not login:
        return False, "Логин не может быть пустым"
    
    if login.lower() in FORBIDDEN_LOGINS:
        return False, "Логин в чс"
    
    if PHONE_RE.fullmatch(login) or EMAIL_RE.fullmatch(login):
        return True, ""
    
    if "@" in login or login.count("-") >= 2:
        return False, "формат не соответствует email или телефона не соответсвуют"
    
    if not PLAIN_LOGIN_RE.fullmatch(login):
        return False, "Логин-строка: латиница,цифры,_  минимум 5 символов"
    
    return True, ""


def validate_password(password, confirm):
    if not password:
        return False, "Пароль не может быть пустым"
    
    if not PASSWORD_RE.fullmatch(password):
        return False, "Пароль: только кириллица/цифры/спецсимволы, минимум 7 символов"
    
    if not re.search(r"[А-ЯЁ]", password):
        return False, "Нужна заглавная буква"
    
    if not re.search(r"[а-яё]", password):
        return False, "Нужна строчная буква"
    
    if not re.search(r"\d", password):
        return False, "Нужна цифра"
    
    if not re.search(f"[{SPECIAL}]", password):
        return False, "Нужен спецсимвол"
    
    if password != confirm:
        return False, "Пароль и подтверждение не совпадают"
    return True, ""


def register(login, password, confirm):
    logging.info(f"Запрос: login={login!r}, password={mask(password)}, confirm={mask(confirm)}")

    for ok, error in (validate_login(login), validate_password(password, confirm)):
        if not ok:
            logging.error(f"Отклонено: {error}")
            return False, error
        
    logging.info(f"Регистрация успешна: login={login!r}")
    return True, ""


def main():
    setup_logging()
    logging.info("Приложение запущено")

    try:
        login, password, confirm = input("Логин: "), input("Пароль: "), input("Подтверждение: ")

        success, message = register(login, password, confirm)
        print(f"Результат: {success!r}\nСообщение: {message!r}")

    except Exception:
        logging.exception("Непредвиденная ошибка:")
        raise


if __name__ == "__main__":
    main()