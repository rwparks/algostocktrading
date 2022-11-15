from pydantic import BaseModel


class AccountSummaryProperty(BaseModel):
    amount: float
    currency: str
    isNull: bool
    timestamp: int
    value: str