import logging
import urllib
from dataclasses import dataclass, field
#from datetime import time
import time
from datetime import datetime
from enum import Enum
from pprint import pprint
from typing import Dict, List

import requests
import urllib3
from pydantic import BaseModel, parse_obj_as
from requests import Session, HTTPError
#from requests_toolbelt.utils import dump
from .cancel_order_response import CancelOrderResponse
from .constants import IB_GATEWAY_PROTOCOL_DOMAIN, \
    API_VERSION, ORDER_STATUS_ENDPOINT, CONTRACTS_BY_SYMBOL_ENDPOINT, \
    BROKERAGE_ACCOUNTS_ENDPOINT, MARKET_DATA_HISTORY_ENDPOINT, MARKET_DATA_ENDPOINT, \
    PLACE_ORDERS_ENDPOINT, LIVE_ORDERS_ENDPOINT, ACCOUNT_TRADES_ENDPOINT, \
    SWITCH_ACCOUNT_ENDPOINT, ACCOUNT_SUMMARY_ENDPOINT, CANCEL_ORDER_ENDPOINT
from .contracts_by_symbol_response_item import *
from .brokerage_accounts_response import BrokerageAccountsResponse
from .order_status_response import OrderStatusResponse
from .account_trades_response import AccountTradesResponseItem
from .account_summary_property import AccountSummaryProperty
from .place_orders_response import PlaceOrdersResponseItem

#logger = logging.getLogger(__name__)


class RequestMethod(Enum):
    GET = 'GET'
    POST = 'POST'
    DELETE = 'DELETE'


#def logging_hook(response, *args, **kwargs):
#    data = dump.dump_all(response)
#    logger.debug(data.decode('utf-8'))


@dataclass
class IBClient:
    port: str = 5000
    #debugging_level: logging = logging.INFO
    _session: Session = field(init=False, default_factory=requests.Session)
    #logger: Optional[Logger] = field(init=False, default=get_logger(__name__))

    def __post_init__(self):
#        self._session.hooks["response"] = [logging_hook]
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        #logging.basicConfig()
        #logger.setLevel(self.debugging_level)

    @staticmethod
    def _headers(mode: str = 'json') -> Dict:
        if mode == 'json':
            headers = {
                'Content-Type': 'application/json'
            }
        elif mode == 'form':
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        elif mode == 'none':
            headers = None

        return headers

    @staticmethod
    def _build_url(endpoint: str, port: str) -> str:
        return urllib.parse.unquote(
            urllib.parse.urljoin(
                f'{IB_GATEWAY_PROTOCOL_DOMAIN}:{port}',
                f'{API_VERSION}api/{endpoint}'
            )
        )

    @staticmethod
    def _prepare_arguments_list(parameter_list: List[str]) -> str:
        return ','.join(parameter_list) if type(parameter_list) is list else parameter_list

    def _send_request(self, endpoint: str, method: RequestMethod, headers: str = 'json',
                      params: dict = None, json: dict = None) -> Dict:
        """Handles the request to the client.

        Handles all the requests made by the client and correctly organizes
        the information so it is sent correctly. Additionally it will also
        build the URL.

        Arguments:
        ----
        endpoint {str} -- The endpoint we wish to request.

        req_type {str} --  Defines the type of request to be made. Can be one of four
            possible values ['GET','POST','DELETE','PUT']

        params {dict} -- Any arguments that are to be sent along in the request. That
            could be parameters of a 'GET' request, or a data payload of a
            'POST' request.

        Returns:
        ----
        {Dict} -- A response dictionary.

        """
        url = self._build_url(endpoint=endpoint, port=self.port)
        #print(url)
        #print(params)

        headers = self._headers(mode=headers)

        REQUEST_METHOD = {
            'POST': self._session.post,
            'GET': self._session.get,
            'DELETE': self._session.delete
        }

        response = REQUEST_METHOD[method.value](url=url, headers=headers, params=params, json=json, verify=False)

        if response.ok:
            return response.json()
        elif not response.ok and url != 'https://localhost:5000/v1/api/iserver/account':
            #logger.error(f'HTTP Error: {url}')
            raise requests.HTTPError()

    def contracts_by_symbol(self, symbol: str) -> List[ContractsBySymbolResponseItem]:
        resp = self._send_request(
            endpoint=CONTRACTS_BY_SYMBOL_ENDPOINT,
            method=RequestMethod.GET,
            params={'symbols': symbol}
        )
        entity_list = [ContractsBySymbolResponseItem.construct(**i) for i in resp[symbol]]
        for entity in entity_list:
            entity.contracts = [ContractsBySymbolResponseItemContract.construct(**i) for i in entity.contracts]
        return entity_list

    def get_contract_id(self, symbol: str) -> int:
        contracts_list: List[ContractsBySymbolResponseItem] = self.contracts_by_symbol(symbol)
        return contracts_list[0].contracts[0].conid

    def brokerage_accounts(self) -> BrokerageAccountsResponse:
        resp = self._send_request(
            endpoint=BROKERAGE_ACCOUNTS_ENDPOINT,
            method=RequestMethod.GET
        )
        return BrokerageAccountsResponse.construct(accounts=resp['accounts'],
                                                   aliases=resp['aliases'],
                                                   selectedAccount=resp['selectedAccount'])

    def market_data_history(self, conid: str, period: str, bar: str) -> Dict:
        return self._send_request(
            endpoint=MARKET_DATA_HISTORY_ENDPOINT,
            method=RequestMethod.GET,
            params={
                'conid': conid,
                'period': period,
                'bar': bar
            }
        )

    def market_data(self, conids: List[str], since: str, fields: List[str] = None) -> Dict:
        conids_joined = self._prepare_arguments_list(parameter_list=conids)

        if fields is not None:
            fields_joined = ",".join(str(n) for n in fields)
        else:
            fields_joined = ""

        if since is None:
            params = {
                'conids': conids_joined,
                'fields': fields_joined
            }
        else:
            params = {
                'conids': conids_joined,
                'since': since,
                'fields': fields_joined
            }

        return self._send_request(
            endpoint=MARKET_DATA_ENDPOINT,
            method=RequestMethod.GET,
            params=params
        )

    def place_orders(self, account_id: str, orders: dict) -> List[PlaceOrdersResponseItem]:
        resp = self._send_request(
            endpoint=PLACE_ORDERS_ENDPOINT.format(account_id=account_id),
            method=RequestMethod.POST,
            json=orders
        )
        return [PlaceOrdersResponseItem.construct(**i) for i in resp]

    def cancel_order(self, account_id: str, order_id: int):
        resp = self._send_request(
            endpoint=CANCEL_ORDER_ENDPOINT.format(account_id=account_id, order_id=order_id),
            method=RequestMethod.DELETE
        )
        return CancelOrderResponse.construct(**resp)

    def live_orders(self) -> Dict:
        return self._send_request(
            endpoint=LIVE_ORDERS_ENDPOINT,
            method=RequestMethod.GET
        )

    def switch_account(self, account_id: str) -> Dict:
        return self._send_request(
            endpoint=SWITCH_ACCOUNT_ENDPOINT,
            method=RequestMethod.POST,
            json={'acctId': account_id}
        )

    def account_trades(self) -> List[AccountTradesResponseItem]:
        resp = self._send_request(
            endpoint=ACCOUNT_TRADES_ENDPOINT,
            method=RequestMethod.GET
        )
        return [AccountTradesResponseItem.construct(**i) for i in resp]

    def order_status(self, order_id: str) -> OrderStatusResponse:
        resp = self._send_request(
            endpoint=ORDER_STATUS_ENDPOINT.format(order_id=order_id),
            method=RequestMethod.GET
        )
        return OrderStatusResponse.construct(**resp)

    def account_summary(self, account_id: str, property: str) -> Optional[AccountSummaryProperty]:
        resp = self._send_request(
            endpoint=ACCOUNT_SUMMARY_ENDPOINT.format(account_id=account_id),
            method=RequestMethod.GET
        )
        return AccountSummaryProperty.construct(**resp[property]) if property in resp else None

# client = IBClient(debugging_level=logging.DEBUG, port='5100')

#client = IBClient(port='5100')

#contracts_list: List[ContractsBySymbolResponseItem] = client.contracts_by_symbol('AAPL')
#conid = contracts_list[0].contracts[0].conid

# conid = r['AAPL'][0]['contracts'][0]['conid']
##print(conid)

#r = client.market_data_history(conid, '1w', '1d')
#print(r)

#r = client.brokerage_accounts()
#account_id = r.accounts[0]


#account_summary = client.account_summary(account_id=client.brokerage_accounts().accounts[0],
#                                         property='totalcashvalue-s')
#if account_summary:
#    print(account_summary.amount)
#else:
#    print('invalid account summary property name')

#account_id = client.brokerage_accounts().accounts[0]
#orders = {
#   'orders': [
#                 {
#                   'conid': conid,
#                   'secType': f'{conid}:STK',
#                   'cOID': 'my_order9',
#                   'orderType': 'MKT',
#                   'side': 'BUY',
#                   'tif': 'GTC',
#                   'quantity': 1
#                 }
#              ]
#         }
#
#resp1 = client.place_orders(account_id=account_id, orders=orders)
#pprint(resp1)
#resp2: OrderStatusResponse = client.order_status(order_id=resp1[0].order_id)
#print(resp2)
#l = 3
#i = 0
#while resp2.order_status != 'Filled' and i < 3:
#    time.sleep(3)
#    resp2: OrderStatusResponse = client.order_status(order_id=resp1[0].order_id)
#    print(resp2)
#    i = i + 1

# r = client.live_orders()

#r1 = client.brokerage_accounts()
#try:
#   r2 = client.switch_account(r1.accounts[0])
#except Exception as e:
#   pass

#data = client.market_data(conids=[f'{conid}'], since='1658485223000', fields=['87', '31', '7741'])
#print(data)

# r1 = client.brokerage_accounts()
# try:
#    r2 = client.switch_account(r1.accounts[0])
# except Exception as e:
#    pass

# aa: List[AccountTradesResponseItem]
# aa = client.account_trades()
# print(len(aa))
# print(aa[0].symbol)
