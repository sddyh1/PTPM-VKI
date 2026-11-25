from abc import ABC, abstractmethod
from getpass import getpass

from registration import Credentials


class UserInput(ABC):
    @abstractmethod
    def read(self) -> Credentials:
        """Получить данные одной попытки регистрации."""


class ConsoleInput(UserInput):
    def read(self) -> Credentials:
        return Credentials(input("Логин: "), getpass("Пароль: "), getpass("Подтверждение: "))


class ResultSender(ABC):
    @abstractmethod
    def send(self, message: str) -> None:
        """Передать строку результата внешнему сервису."""


class SimulatedServer(ResultSender):
    def send(self, message: str) -> None:
        print(f"[Имитация сервера] {message}")
