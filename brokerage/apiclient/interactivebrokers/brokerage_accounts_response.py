from typing import List
from pydantic import BaseModel


class BrokerageAccountsResponse(BaseModel):
    accounts: List[str] = None
    aliases: object = None
    selectedAccount: str = None
