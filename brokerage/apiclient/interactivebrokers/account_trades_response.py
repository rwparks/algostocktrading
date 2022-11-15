from typing import List

from pydantic import BaseModel


class AccountTradesResponseItem(BaseModel):
    execution_id: str
    symbol: str
    side: str
    order_description: str
    trade_time: str
    trade_time_r: int
    size: str
    price: str
    order_ref: str
    submitter: str
    exchange: str
    commission: float
    net_amount: float
    account: str
    accountCode: str
    company_name: str
    contract_description_1: str
    sec_type: str
    conid: str
    conidex: str
    position: str
    clearing_id: str
    clearing_name: str
    liquidation_trade: float


#class AccountTradesResponse(BaseModel):
#    data: List[AccountTradesResponseItem]
