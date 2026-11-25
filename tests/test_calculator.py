import unittest

from selenium import webdriver

from pages.calculator_page import CalculatorPage


class CalculatorTests(unittest.TestCase):
    def setUp(self):
        options = webdriver.EdgeOptions()
        options.add_argument("--headless=new")
        options.page_load_strategy = "eager"
        self.driver = webdriver.Edge(options=options)
        self.driver.set_page_load_timeout(25)
        self.page = CalculatorPage(self.driver)

    def tearDown(self):
        self.driver.quit()

    def calculate(self, first, operation, second):
        self.page.enter_first_number(first)
        self.page.enter_second_number(second)
        self.page.select_operation(operation)
        return self.page.result()

    def test_addition(self):
        self.page.open()
        self.assertEqual(self.calculate(7, "+", 5), "12")

    def test_subtraction(self):
        self.page.open()
        self.assertEqual(self.calculate(5, "-", 7), "-2")

    def test_multiplication(self):
        self.page.open()
        self.assertEqual(self.calculate(-4, "*", 5), "-20")

    def test_division(self):
        self.page.open()
        self.assertEqual(self.calculate(7, "/", 2), "3.5")

    def test_multiplication_by_zero(self):
        self.page.open()
        self.assertEqual(self.calculate(12, "*", 0), "0")

    def test_division_by_zero(self):
        self.page.open()
        self.assertEqual(self.calculate(7, "/", 0), "null")

    def test_zero_divided_by_zero(self):
        self.page.open()
        self.assertEqual(self.calculate(0, "/", 0), "null")

    def test_large_integer(self):
        self.page.open()
        self.assertEqual(self.calculate(9007199254740990, "+", 1), "9007199254740991")

    def test_increment_and_decrement_buttons(self):
        self.page.open()
        self.page.increase_first_number()
        self.assertEqual(self.page.result(), "1")
        self.page.increase_second_number()
        self.assertEqual(self.page.result(), "2")
        self.page.decrease_first_number()
        self.assertEqual(self.page.result(), "1")
        self.page.decrease_second_number()
        self.assertEqual(self.page.result(), "0")
