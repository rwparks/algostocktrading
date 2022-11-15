from typing import List

from pydantic import BaseModel


class PlaceOrdersResponseItem(BaseModel):
    encrypt_message: str
    local_order_id: str
    order_id: str
    order_status: str
    text: str
    warning_message: str



#class PlaceOrdersResponse(BaseModel):
#    orders: List[PlaceOrdersResponseItem]
