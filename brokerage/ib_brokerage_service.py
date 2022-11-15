import logging
from logging import Logger
from dataclasses import dataclass
from datetime import datetime, timedelta
import time
from typing import List, Dict
from attr import define, field, Factory, asdict
from brokerage.apiclient.interactivebrokers.account_summary_property import AccountSummaryProperty
from brokerage.apiclient.interactivebrokers.cancel_order_response import CancelOrderResponse
from brokerage.apiclient.interactivebrokers.ibclient import IBClient
from brokerage.apiclient.interactivebrokers.order_status_response import OrderStatusResponse
from brokerage.apiclient.interactivebrokers.place_orders_response import PlaceOrdersResponseItem

@define
class Quote:
    ask: float
    bid: float
    last: float


@define
class IBOrder:
    conid: int
    side: str
    quantity: float
    #cashQty: float
    #tif: str = 'IOC'
    tif: str = 'GTC'
    orderType: str = 'MKT'
    secType: str = field()

    @secType.default
    def _set_sectype(self):
        return f'{self.conid}:STK'

    cOID: str = field()

    @cOID.default
    def _set_coid(self):
        return f'{int(time.time() * 1000)}'


@define
class IBOrders:
    order_list: List[Dict] = Factory(list)

    @property
    def orders(self) -> Dict:
        return {'orders': self.order_list}

    def add(self, order: IBOrder):
        #conid = self.client.get_contract_id(symbol)
        self.order_list.append(asdict(order))


class AccountSummaryPropertyError(Exception):

    def __init__(self, account_summary_property, message='Account summary property is invalid'):
        self.account_summary_property = account_summary_property
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.account_summary_property} -> {self.message}'


@dataclass
class IBBrokerageService:
    client: IBClient
    logger: Logger = field(init=False)

    def __post_init__(self):
        self.logger = logging.getLogger(__name__)

    def place_order(self, side: str, ticker: str, quantity: int) -> OrderStatusResponse:

        ib_orders = IBOrders()
        ib_orders.add(order=IBOrder(conid=self.client.get_contract_id(ticker),
                                    side=side, quantity=quantity))

        self.logger.info(f'Placing order: {ib_orders}')
        resp: List[PlaceOrdersResponseItem] =\
            self.client.place_orders(account_id=self.client.brokerage_accounts().accounts[0],
                                     orders=ib_orders.orders)
        order_id = resp[0].order_id

        status: OrderStatusResponse = self.client.order_status(order_id=order_id)
        self.logger.debug(f'Order status: {status}')
        loop_cnt = 0
        while status.order_status != 'Filled' and loop_cnt < 6:
            self.logger.debug('Sleeping 30 seconds')
            time.sleep(30)
            status: OrderStatusResponse = self.client.order_status(order_id=order_id)
            self.logger.debug(f'Order status: {status}')
            # print(status)
            loop_cnt = loop_cnt + 1

        return status

    def cancel_order(self, order_id: int) -> CancelOrderResponse:
        return self.client.cancel_order(account_id=self.client.brokerage_accounts().accounts[0],
                                        order_id=order_id)

    def get_quote(self, ticker: str) -> Quote:
        self.logger.debug(f'getting quote for {ticker}')
        conid = self.client.get_contract_id(symbol=ticker)
        self.client.brokerage_accounts()

        since = self._timestamp(datetime.now() - timedelta(days=7))
        data = self.client.market_data(conids=[f'{conid}'], since=f'{since}', fields=['84', '86', '31'])
        while '84' not in data[0] or '86' not in data[0] or '31' not in data[0]:
            time.sleep(1)
            data = self.client.market_data(conids=[f'{conid}'], since=f'{since}', fields=['84', '86', '31'])
        return Quote(ask=float(data[0]['86']), bid=float(data[0]['84']), last=float(data[0]['31']))

    def get_cash_value(self) -> float:
        account_summary_property = 'totalcashvalue'
        account_summary: AccountSummaryProperty = self.client.account_summary(
            account_id=self.client.brokerage_accounts().accounts[0],
            property=account_summary_property)
        if account_summary:
            return account_summary.amount
        else:
            raise AccountSummaryPropertyError(account_summary_property=account_summary_property)

    def get_order_status(self, order_id: str) -> str:
        resp: OrderStatusResponse = self.client.order_status(order_id=order_id)
        return resp.order_status

    @staticmethod
    def _timestamp(dt):
        return (dt - datetime.utcfromtimestamp(0)).total_seconds() * 1000
