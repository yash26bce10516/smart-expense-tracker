"""End-to-end test: drives the real menu loop with scripted keyboard input."""
import os
import tempfile
import unittest

from expense_tracker.cli import App


class CLITests(unittest.TestCase):
    def run_script(self, inputs):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        feed = iter(inputs)
        out = []
        app = App(db_path=os.path.join(tmp.name, "cli.db"),
                  input_fn=lambda prompt="": next(feed),
                  output_fn=out.append,
                  password_fn=lambda prompt="": next(feed))
        app.run()
        return "\n".join(out)

    def test_full_workflow(self):
        text = self.run_script([
            "2", "carol", "pass1234",                       # register
            "5", "Food", "1000",                            # set budget
            "1", "900", "Food", "groceries", "2026-09-10",  # add expense (90% -> alert)
            "2", "", "", "",                                # view all
            "7", "2026-09",                                 # report
            "0", "0",                                       # logout, exit
        ])
        self.assertIn("Account created", text)
        self.assertIn("Budget WARNING", text)
        self.assertIn("groceries", text)
        self.assertIn("Report for 2026-09", text)
        self.assertIn("Bye!", text)

    def test_errors_are_friendly_not_crashes(self):
        text = self.run_script([
            "1", "ghost", "whatever",        # login as unknown user
            "2", "dave", "pass1234",         # register
            "1", "abc", "Food", "", "",      # invalid amount
            "4", "notanumber",               # invalid id
            "99",                            # invalid menu option
            "0", "0",
        ])
        self.assertIn("Invalid username or password", text)
        self.assertIn("Amount must be a number", text)
        self.assertIn("valid number", text)
        self.assertIn("Invalid option", text)


if __name__ == "__main__":
    unittest.main()
