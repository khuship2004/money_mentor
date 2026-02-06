"""
Lightweight stubs for data fetching to avoid heavy dependencies.

In this simplified mode we do not fetch real market data; we simply return
success flags so the API remains functional without external services.
"""
from sqlalchemy.orm import Session


class DataFetcher:
    def __init__(self, db: Session):
        self.db = db

    def fetch_all(self):
        """Return stubbed fetch results."""
        return {"nifty50": False, "gold": False, "bonds": False, "cash": False}


def calculate_returns(db: Session):
    """Stub: no-op return calculation."""
    return False
