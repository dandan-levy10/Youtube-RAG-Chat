# tests/conftest.py
import warnings

import pytest
from sqlmodel import Session, SQLModel, create_engine

# Silence the specific Pydantic v1 typing warning:
warnings.filterwarnings(
    "ignore",
    category=DeprecationWarning,
    module=r"pydantic\.v1\.typing"
)

import os
# tests/conftest.py
import sys

# Determine project root (one level up from tests/)
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Insert it at the front of sys.path so 'import app' works
sys.path.insert(0, ROOT)

@pytest.fixture
def in_memory_db():
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
