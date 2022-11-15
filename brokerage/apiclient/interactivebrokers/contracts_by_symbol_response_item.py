from typing import List, Optional
from pydantic import BaseModel


class ContractsBySymbolResponseItemContract(BaseModel):
    conid: int
    exchange:str
    isUS: bool


class ContractsBySymbolResponseItem(BaseModel):
    name: str
    chineseName: Optional[str]
    assetClass: str
    contracts: List[ContractsBySymbolResponseItemContract]
