from pydantic import BaseModel


class CancelOrderResponse(BaseModel):
    order_id: str
    msg: str
    conid: int
    account: str
