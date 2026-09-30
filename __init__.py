"""Test package: redirect log output to a temp dir so tests never touch real data."""
import os
import tempfile

os.environ.setdefault("EXPENSE_PBKDF2_ITERS", "1000")   # fast hashing in tests only
os.environ.setdefault("EXPENSE_LOG", os.path.join(tempfile.mkdtemp(), "test.log"))
