import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from delivery_service import calculate_delivery_cost

ERROR = (-1, "0000-00-00")


class TestDeliveryInputValidation(unittest.TestCase):

    def test_weight_below_minimum_returns_error(self):
        self.assertEqual(calculate_delivery_cost(0.09, 100, "обычный"), ERROR)

    def test_weight_at_minimum_is_accepted(self):
        self.assertNotEqual(calculate_delivery_cost(0.1, 100, "обычный"), ERROR)

    def test_weight_at_maximum_is_accepted(self):
        self.assertNotEqual(calculate_delivery_cost(50.0, 100, "обычный"), ERROR)

    def test_weight_above_maximum_returns_error(self):
        self.assertEqual(calculate_delivery_cost(50.1, 100, "обычный"), ERROR)

    def test_negative_weight_returns_error(self):
        self.assertEqual(calculate_delivery_cost(-5, 100, "обычный"), ERROR)

    def test_zero_distance_returns_error(self):
        self.assertEqual(calculate_delivery_cost(1.0, 0, "обычный"), ERROR)

    def test_distance_at_minimum_is_accepted(self):
        self.assertNotEqual(calculate_delivery_cost(1.0, 1, "обычный"), ERROR)

    def test_distance_at_maximum_is_accepted(self):
        self.assertNotEqual(calculate_delivery_cost(1.0, 5000, "обычный"), ERROR)

    def test_distance_above_maximum_returns_error(self):
        self.assertEqual(calculate_delivery_cost(1.0, 5001, "обычный"), ERROR)

    def test_unknown_package_type_returns_error(self):
        self.assertEqual(calculate_delivery_cost(1.0, 100, "стеклянный"), ERROR)


class TestDeliveryCost(unittest.TestCase):

    def test_regular_light_package_cost(self):
        self.assertEqual(calculate_delivery_cost(1.0, 100, "обычный")[0], 700)

    def test_weight_exactly_5kg_has_no_weight_coefficient(self):
        self.assertEqual(calculate_delivery_cost(5.0, 100, "обычный")[0], 700)

    def test_medium_weight_applies_coefficient_1_2(self):
        self.assertEqual(calculate_delivery_cost(10.0, 100, "обычный")[0], 840)

    def test_weight_exactly_20kg_applies_coefficient_1_5(self):
        self.assertEqual(calculate_delivery_cost(20.0, 100, "обычный")[0], 1050)

    def test_fragile_package_adds_300(self):
        self.assertEqual(calculate_delivery_cost(1.0, 100, "хрупкий")[0], 1000)

    def test_dangerous_package_adds_1000(self):
        self.assertEqual(calculate_delivery_cost(1.0, 100, "опасный")[0], 1700)

    # Падает:строка 36; экспресс умножает цену на 0.5 (350 вместо >700)
    # Исправление: total_cost *= 1.5
    def test_express_delivery_costs_more_than_regular(self):
        regular = calculate_delivery_cost(1.0, 100, "обычный")[0]
        express = calculate_delivery_cost(1.0, 100, "обычный", is_express=True)[0]
        self.assertGreater(express, regular)


class TestDeliveryDate(unittest.TestCase):

    def test_short_distance_takes_one_day(self):
        self.assertEqual(calculate_delivery_cost(1.0, 100, "обычный")[1], "2026-09-04")

    def test_exactly_500km_takes_one_day(self):
        self.assertEqual(calculate_delivery_cost(1.0, 500, "обычный")[1], "2026-09-04")

    # Падает:строка 41; 500 округляет вниз, 750 км = 1 день вместо 2
    # Исправление:days_needed = max(1, (distance + 499) // 500)
    def test_750km_takes_two_days(self):
        self.assertEqual(calculate_delivery_cost(1.0, 750, "обычный")[1], "2026-09-05")

    def test_5000km_takes_ten_days(self):
        self.assertEqual(calculate_delivery_cost(1.0, 5000, "обычный")[1], "2026-09-13")

    # Падает:строка 44; 2 = 0, посылка приходит в день отправки
    # Исправление:days_needed = max(1, days_needed // 2)
    def test_express_short_distance_is_not_delivered_same_day(self):
        self.assertEqual(calculate_delivery_cost(1.0, 100, "обычный", is_express=True)[1], "2026-09-04")

    def test_express_halves_delivery_time(self):
        self.assertEqual(calculate_delivery_cost(1.0, 5000, "обычный", is_express=True)[1], "2026-09-08")


if __name__ == "__main__":
    unittest.main()