"""Entry point: python main.py"""
from expense_tracker.cli import run

if __name__ == "__main__":
    try:
        run()
    except (KeyboardInterrupt, EOFError):
        print("\nExiting. Bye!")
