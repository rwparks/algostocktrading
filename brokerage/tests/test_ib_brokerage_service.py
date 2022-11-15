import unittest
from datetime import datetime
from typing import List
from unittest import TestCase, skip
from unittest.mock import Mock, patch
from attr import define, Factory

from brokerage.apiclient.interactivebrokers.account_summary_property import AccountSummaryProperty
from brokerage.apiclient.interactivebrokers.cancel_order_response import CancelOrderResponse
from brokerage.apiclient.interactivebrokers.ibclient import IBClient
from brokerage.apiclient.interactivebrokers.order_status_response import OrderStatusResponse
from brokerage.apiclient.interactivebrokers.place_orders_response import PlaceOrdersResponseItem
from brokerage.brokerage_service import BrokerageService
from brokerage.ib_brokerage_service import IBBrokerageService, AccountSummaryPropertyError


@define
class Accounts:
    accounts: List[str] = Factory(list)


class BrokerageServiceTestCase(TestCase):

    def setUp(self):
        ib_client = IBClient(port=5100)
        ib_client.get_contract_id = Mock()
        ib_client.brokerage_accounts = Mock()
        ib_client.market_data = Mock()
        ib_client.place_orders = Mock()
        ib_client.order_status = Mock()
        ib_client.account_summary = Mock()
        ib_client.cancel_order = Mock()
        self.ib_brokerage_service = IBBrokerageService(client=ib_client)

    def test_place_order__filled_immediately(self):
        self.ib_brokerage_service.client.get_contract_id.return_value = 123
        acnts = Accounts()
        acnts.accounts.append('123456')
        self.ib_brokerage_service.client.brokerage_accounts.return_value = acnts
        self.ib_brokerage_service.client.place_orders.return_value = [
            PlaceOrdersResponseItem.construct(order_id=123, order_status='Submitted')]
        expected_return_value = OrderStatusResponse.construct(order_status='Filled', average_price='1.00', symbol='A')
        self.ib_brokerage_service.client.order_status.return_value = expected_return_value

        assert self.ib_brokerage_service.place_order('BUY', 'A', 2) == expected_return_value

    @patch('time.sleep', return_value=None)
    def test_place_order__filled_after_sleeping_3_times(self, patched_time_sleep):
        self.ib_brokerage_service.client.get_contract_id.return_value = 123
        acnts = Accounts()
        acnts.accounts.append('123456')
        self.ib_brokerage_service.client.brokerage_accounts.return_value = acnts
        self.ib_brokerage_service.client.place_orders.return_value = [
            PlaceOrdersResponseItem.construct(order_id=123, order_status='Submitted')]
        order_status_side_effect = [
            OrderStatusResponse.construct(order_status='Submitted', average_price='', symbol='A'),
            OrderStatusResponse.construct(order_status='Submitted', average_price='', symbol='A'),
            OrderStatusResponse.construct(order_status='Submitted', average_price='', symbol='A'),
            OrderStatusResponse.construct(order_status='Filled', average_price='1.00', symbol='A')]
        self.ib_brokerage_service.client.order_status.side_effect = order_status_side_effect

        resp = self.ib_brokerage_service.place_order('BUY', 'A', 2)
        assert resp == order_status_side_effect[3]
        assert patched_time_sleep.call_count == 3

    @skip("this is not a real test")
    def test_real_place_order(self):
        ib_brokerage_service = IBBrokerageService(client=IBClient(port='5100'))
        print(ib_brokerage_service.place_order(side='A', ticker='AAPL', quantity=1))

    @skip("this is not a real test")
    def test_real_get_cash_value(self):
        brokerage_service: BrokerageService = IBBrokerageService(client=IBClient(port='5100'))
        cash = round(brokerage_service.get_cash_value(), 2)
        print(cash)

    def test_get_cash_value(self):
        acnts = Accounts()
        acnts.accounts.append('123456')
        self.ib_brokerage_service.client.brokerage_accounts.return_value = acnts
        account_summary_property: AccountSummaryProperty = AccountSummaryProperty.construct(amount=1000.00)
        self.ib_brokerage_service.client.account_summary.return_value = account_summary_property

        cash_value = self.ib_brokerage_service.get_cash_value()

        self.assertEqual(cash_value, 1000)

    def test_get_cash_value_none_return_value(self):
        acnts = Accounts()
        acnts.accounts.append('123456')
        self.ib_brokerage_service.client.brokerage_accounts.return_value = acnts
        self.ib_brokerage_service.client.account_summary.return_value = None

        self.failUnlessRaises(AccountSummaryPropertyError, self.ib_brokerage_service.get_cash_value)

    @patch('time.sleep', return_value=None)
    @patch('brokerage.ib_brokerage_service.datetime')
    def test_get_quote__get_quote_immediately(self, patched_time_sleep, mock_datetime):
        self.ib_brokerage_service.client.get_contract_id.return_value = 123
        acnts = Accounts()
        acnts.accounts.append('123456')
        self.ib_brokerage_service.client.brokerage_accounts.return_value = acnts
        mock_datetime.now = Mock(return_value=datetime(2022, 8, 10))
        self.ib_brokerage_service.client.market_data.return_value = [{'84': '1.00', '86': '1.01', '31': '1.02'}]

        quote = self.ib_brokerage_service.get_quote('A')

        self.assertEqual(quote.__str__(), 'Quote(ask=1.01, bid=1.0, last=1.02)')
        self.assertEqual(patched_time_sleep.call_count, 0)
        self.assertEqual(self.ib_brokerage_service.client.market_data.call_count, 1)

    @patch('time.sleep', return_value=None)
    @patch('brokerage.ib_brokerage_service.datetime')
    def test_get_quote__get_quote_delayed(self, mock_datetime, mock_time_sleep):
        self.ib_brokerage_service.client.get_contract_id.return_value = 123
        acnts = Accounts()
        acnts.accounts.append('123456')
        self.ib_brokerage_service.client.brokerage_accounts.return_value = acnts
        mock_datetime.now = Mock(return_value=datetime(2022, 8, 10))
        self.ib_brokerage_service.client.market_data.side_effect = [[{'84': '1.00', '86': '1.01'}],
                                                                    [{'84': '1.00', '86': '1.01', '31': '1.02'}]]

        quote = self.ib_brokerage_service.get_quote('A')

        self.assertEqual(quote.__str__(), 'Quote(ask=1.01, bid=1.0, last=1.02)')
        self.assertEqual(mock_time_sleep.call_count, 1)
        self.assertEqual(self.ib_brokerage_service.client.market_data.call_count, 2)

    def test_cancel_order(self):
        acnts = Accounts()
        acnts.accounts.append('123456')
        self.ib_brokerage_service.client.brokerage_accounts.return_value = acnts
        self.ib_brokerage_service.client.cancel_order.return_value = CancelOrderResponse.construct(order_id='321',
                                                                                                   msg='a message',
                                                                                                   conid=123,
                                                                                                   account='123456')

        self.assertEquals(self.ib_brokerage_service.cancel_order(order_id=321),
                          self.ib_brokerage_service.client.cancel_order.return_value)

    def test_order_status(self):
        self.ib_brokerage_service.client.order_status.return_value =\
            OrderStatusResponse.construct(order_status='Filled', average_price='1.00', symbol='A')

        self.assertEqual(self.ib_brokerage_service.get_order_status(order_id='123'), 'Filled')


if __name__ == '__main__':
    unittest.main()
