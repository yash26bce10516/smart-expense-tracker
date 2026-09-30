"""Plain data classes shared by all layers."""
from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    id: int
    username: str


@dataclass
class Expense:
    id: int
    user_id: int
    amount: float
    category: str
    description: str
    date: str  # ISO format YYYY-MM-DD


@dataclass
class Budget:
    id: int
    user_id: int
    category: str
    monthly_limit: float


@dataclass
class BudgetStatus:
    category: str
    limit: float
    spent: float
    percent: float
    level: str  # "OK" | "WARNING" | "EXCEEDED"
