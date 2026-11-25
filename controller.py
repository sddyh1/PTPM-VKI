from adapters import ResultSender, UserInput
from database import RegistrationDatabase
from registration import RegistrationValidator


class Controller:
    def __init__(self, user_input: UserInput, database: RegistrationDatabase,
                 validator: RegistrationValidator, sender: ResultSender):
        self.user_input = user_input
        self.database = database
        self.validator = validator
        self.sender = sender

    def run(self) -> str:
        data = self.user_input.read()
        result = self.database.get(data)
        if result is None:
            result = self.validator.register(data)
            self.database.add(data, result)

        message = "Регистрация успешна" if result.success else result.error
        self.sender.send(message)
        return message
