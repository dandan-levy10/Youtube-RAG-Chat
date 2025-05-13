# tests/conftest.py
import warnings

# Silence the specific Pydantic v1 typing warning:
warnings.filterwarnings(
    "ignore",
    category=DeprecationWarning,
    module=r"pydantic\.v1\.typing"
)

# tests/conftest.py
import sys
import os

# Determine project root (one level up from tests/)
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Insert it at the front of sys.path so 'import app' works
sys.path.insert(0, ROOT)