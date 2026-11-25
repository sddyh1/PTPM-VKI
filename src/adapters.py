from abc import ABC, abstractmethod
from getpass import getpass

from src.registration import Credentials


class UserInput(ABC):
    @abstractmethod
    def read(self) -> Credentials:
        ...


class ConsoleInput(UserInput):
    def read(self) -> Credentials:
        login = input("Логин: ")
        password = getpass("Пароль: ")
        confirmation = getpass("Подтверждение: ")
        return Credentials(login, password, confirmation)


class ResultSender(ABC):
    @abstractmethod
    def send(self, message: str) -> None:
        ...


class SimulatedServer(ResultSender):
    def send(self, message: str) -> None:
        print(f"[Имитация сервера] {message}")
