from unittest import TestCase, mock

from brokerage.ib_orders import IBOrders, IBOrder
from brokerage.orders import OrdersBuilder


class IBOrdersTestCase(TestCase):

    @mock.patch('brokerage.ib_orders.time')
    def test_orders_asdict(self, mock_time):
        mock_time.time.return_value = 1660000000
        test_orders = IBOrders()
        test_orders.orders.append(IBOrder(conid=123, side='BUY', quantity=1.0))
        test_orders.orders.append(IBOrder(conid=124, side='SELL', quantity=2.0))
        # orders: Orders = test_orders
        assert test_orders.orders_asdict == {'orders':
                                                 [{'conid': 123, 'side': 'BUY', 'quantity': 1.0, 'secType': '123:STK',
                                                   'cOID': '1660000000000', 'orderType': 'MKT', 'tif': 'IOC'},
                                                  {'conid': 124, 'side': 'SELL', 'quantity': 2.0, 'secType': '124:STK',
                                                   'cOID': '1660000000000', 'orderType': 'MKT', 'tif': 'IOC'}]}

    @mock.patch('brokerage.ib_orders.time')
    def test_orders_factory(self, mock_time):
        mock_time.time.return_value = 1660000000
        builder: OrdersBuilder = IBOrders()
        builder.add(symbol='A', side='BUY', quantity=1.0)
        builder.add(symbol='B', side='SELL', quantity=2.0)
        print(builder.orders)
        #assert builder.orders == {'orders':
        #                              [{'conid': 123, 'side': 'BUY', 'quantity': 1.0, 'secType': '123:STK',
        #                                'cOID': '1660000000000', 'orderType': 'MKT', 'tif': 'IOC'},
        #                               {'conid': 124, 'side': 'SELL', 'quantity': 2.0, 'secType': '124:STK',
        #                                'cOID': '1660000000000', 'orderType': 'MKT', 'tif': 'IOC'}]}
