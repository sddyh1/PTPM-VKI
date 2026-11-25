from abc import ABC, abstractmethod


class UserInput(ABC):
    @abstractmethod
    def read(self):
        ...


class ConsoleInput(UserInput):
    def read(self):
        login = input("Логин: ")
        password = input("Пароль: ")
        confirmation = input("Подтверждение: ")
        return login, password, confirmation


class ResultSender(ABC):
    @abstractmethod
    def send(self, message: str) -> None:
        ...


class SimulatedServer(ResultSender):
    def send(self, message: str) -> None:
        print(f"[Имитация сервера] {message}")
