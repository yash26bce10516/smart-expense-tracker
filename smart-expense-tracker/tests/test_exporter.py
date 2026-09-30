import os
import unittest

from expense_tracker.exceptions import TrackerError
from expense_tracker.exporter import export_csv, import_csv
from tests.base import DBTestCase


class ExporterTests(DBTestCase):
    def test_round_trip(self):
        self.expenses.add(self.user.id, 120.5, "Food", "lunch, with comma", "2026-09-01")
        self.expenses.add(self.user.id, 40, "Transport", "bus", "2026-09-02")
        path = os.path.join(self.tmp.name, "out.csv")
        self.assertEqual(export_csv(self.expenses.list(self.user.id), path), 2)
        bob = self.auth.register("bob", "bobpass1")
        imported, errors = import_csv(path, self.expenses, bob.id)
        self.assertEqual((imported, errors), (2, []))
        descs = {e.description for e in self.expenses.list(bob.id)}
        self.assertIn("lunch, with comma", descs)

    def test_bad_rows_are_skipped_and_reported(self):
        path = os.path.join(self.tmp.name, "bad.csv")
        with open(path, "w") as fh:
            fh.write("date,amount,category,description\n"
                     "2026-09-01,100,Food,ok\n"
                     "2026-09-02,-5,Food,negative\n"
                     "not-a-date,10,Food,bad date\n")
        imported, errors = import_csv(path, self.expenses, self.user.id)
        self.assertEqual(imported, 1)
        self.assertEqual(len(errors), 2)
        self.assertIn("Line 3", errors[0])

    def test_missing_file_and_bad_header(self):
        with self.assertRaises(TrackerError):
            import_csv(os.path.join(self.tmp.name, "nope.csv"), self.expenses, self.user.id)
        path = os.path.join(self.tmp.name, "hdr.csv")
        with open(path, "w") as fh:
            fh.write("a,b\n1,2\n")
        with self.assertRaises(TrackerError):
            import_csv(path, self.expenses, self.user.id)


if __name__ == "__main__":
    unittest.main()
