from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait


class CalculatorPage:
    _URL = "https://www.globalsqa.com/angularJs-protractor/SimpleCalculator/"
    _FIRST_NUMBER = (By.CSS_SELECTOR, 'input[ng-model="a"]')
    _SECOND_NUMBER = (By.CSS_SELECTOR, 'input[ng-model="b"]')
    _OPERATION = (By.CSS_SELECTOR, 'select[ng-model="operation"]')
    _RESULT = (By.CSS_SELECTOR, "b.result")
    _FIRST_PLUS = (By.CSS_SELECTOR, 'button[ng-click="inca()"]')
    _FIRST_MINUS = (By.CSS_SELECTOR, 'button[ng-click="deca()"]')
    _SECOND_PLUS = (By.CSS_SELECTOR, 'button[ng-click="incb()"]')
    _SECOND_MINUS = (By.CSS_SELECTOR, 'button[ng-click="decb()"]')

    def __init__(self, driver):
        self.driver = driver

    def open(self):
        for attempt in range(3):
            try:
                self.driver.get(self._URL)
                WebDriverWait(self.driver, 10).until(
                    lambda driver: driver.find_element(*self._RESULT).text == "0 + 0 = 0",
                    "Калькулятор не загрузил начальный результат",
                )
                return
            except TimeoutException:
                if attempt == 2:
                    raise

    def enter_first_number(self, number):
        field = self.driver.find_element(*self._FIRST_NUMBER)
        field.clear()
        field.send_keys(str(number))

    def enter_second_number(self, number):
        field = self.driver.find_element(*self._SECOND_NUMBER)
        field.clear()
        field.send_keys(str(number))

    def select_operation(self, operation):
        menu = Select(self.driver.find_element(*self._OPERATION))
        menu.select_by_value(operation)

    def increase_first_number(self):
        self.driver.find_element(*self._FIRST_PLUS).click()

    def decrease_first_number(self):
        self.driver.find_element(*self._FIRST_MINUS).click()

    def increase_second_number(self):
        self.driver.find_element(*self._SECOND_PLUS).click()

    def decrease_second_number(self):
        self.driver.find_element(*self._SECOND_MINUS).click()

    def result(self):
        expression = self.driver.find_element(*self._RESULT).text
        return expression.split(" = ", 1)[1]
