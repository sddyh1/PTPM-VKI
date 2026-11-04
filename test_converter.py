import unittest

from converter import Converter


class TestConverter(unittest.TestCase):
    def test_positive_numbers_below_threshold(self):
        cases = [(0.1, 0), (0.9, 0), (1.0, 1), (65.7, 65), (100.6, 100)]
        for x, expected in cases:
            with self.subTest(x=x):
                self.assertEqual(Converter.do(x), expected)

    def test_positive_threshold_and_above(self):
        cases = [(100.7, 1000), (100.8, 1000), (1000.0, 1000), (1000000.0, 1000)]
        for x, expected in cases:
            with self.subTest(x=x):
                self.assertEqual(Converter.do(x), expected)

    def test_zero_raises_value_error(self):
        for x in (0.0, -0.0):
            with self.subTest(x=x):
                with self.assertRaises(ValueError):
                    Converter.do(x)

    def test_negative_numbers_near_zero(self):
        cases = [(-30.4, -35), (-30.3, -35), (-15.7, -20),
                 (-1.0, -6), (-0.9, -5), (-0.1, -5)]
        for x, expected in cases:
            with self.subTest(x=x):
                self.assertEqual(Converter.do(x), expected)

    def test_negative_threshold_and_below(self):
        cases = [(-30.5, -2000), (-30.6, -2000), (-94.5, -2000),
                 (-1000000.0, -2000)]
        for x, expected in cases:
            with self.subTest(x=x):
                self.assertEqual(Converter.do(x), expected)

    def test_result_is_int_in_every_range(self):
        for x in (-94.5, -15.7, -0.1, 0.1, 65.7, 100.7):
            with self.subTest(x=x):
                self.assertIs(type(Converter.do(x)), int)


if __name__ == "__main__":
    unittest.main()
