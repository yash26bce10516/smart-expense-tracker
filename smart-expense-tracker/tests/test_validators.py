import unittest

from expense_tracker import validators as v
from expense_tracker.exceptions import ValidationError


class ValidatorTests(unittest.TestCase):
    def test_amount_valid_and_rounded(self):
        self.assertEqual(v.validate_amount("12.345"), round(12.345, 2))
        self.assertEqual(v.validate_amount(100), 100.0)

    def test_amount_invalid(self):
        for bad in ("abc", "", "-5", "0", "nan", "inf", "99999999999", None):
            with self.assertRaises(ValidationError, msg=repr(bad)):
                v.validate_amount(bad)

    def test_category_case_insensitive(self):
        self.assertEqual(v.validate_category("  food "), "Food")
        with self.assertRaises(ValidationError):
            v.validate_category("Gambling")

    def test_date_and_month(self):
        self.assertEqual(v.validate_date("2026-09-30"), "2026-09-30")
        self.assertEqual(v.validate_month("2026-09"), "2026-09")
        for bad in ("30-09-2026", "2026-13-01", "2026-02-30", ""):
            with self.assertRaises(ValidationError, msg=bad):
                v.validate_date(bad)
        with self.assertRaises(ValidationError):
            v.validate_month("2026/09")

    def test_username_password(self):
        self.assertEqual(v.validate_username("Bob_1"), "bob_1")
        for bad in ("ab", "has space", "x" * 21, ""):
            with self.assertRaises(ValidationError):
                v.validate_username(bad)
        with self.assertRaises(ValidationError):
            v.validate_password("123")

    def test_description_length(self):
        with self.assertRaises(ValidationError):
            v.validate_description("x" * 101)


if __name__ == "__main__":
    unittest.main()
