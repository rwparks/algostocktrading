from enum import Enum
from typing import List, Protocol, Dict


class OrderSide(Enum):
    BUY: str = 'BUY'
    SELL: str = 'SELL'


class BrokerageService(Protocol):

    def place_order(self, side: str, ticker: str, quantity: int):
        """ place an order """

#    def place_orders(self, orders: Dict[str, List[Dict]]):
#        """ place orders """

    def get_quote(self, ticker: str):
        """ get a quote """

    def get_cash_value(self):
        """ get cash value """

    def get_order_status(self, order_id: str):
        """ get order status """


#class BrokerageServiceConcrete:
#    #def place_order(self, side: OrderSide, ticker: str, quantity: int):
#    def place_order(self, side: str, ticker: str, quantity: int):
#        pass
#
#    def get_quote(self, ticker: str):
#        pass
#
#    def get_cash_value(self):
#        pass
#
#    def get_order_status(self, order_id: str):
#        pass

# Quote = namedtuple('Quote', ['ask', 'bid', 'last'])
