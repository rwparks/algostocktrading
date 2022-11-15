import unittest
from unittest import TestCase

from brokerage.backtesting_brokerage_service import BackTestingBrokerageService
from brokerage.brokerage_service import BrokerageService


class BackTestingBrokerageServiceTestCase(TestCase):


    def test_place_order(self):
        closing_prices = {'A': 100, 'B': 200}
        #initial_account_balance = 10000
        #brokerage_service: BrokerageService = BackTestingBrokerageService(closing_prices=closing_prices,
        #                                                                  initial_account_balance=initial_account_balance)
        brokerage_service: BrokerageService = BackTestingBrokerageService(closing_prices=closing_prices)
        resp = brokerage_service.place_order(side='BUY', ticker='A', quantity=10)
        print(resp)
        print(brokerage_service.get_cash_value())
        closing_prices['A'] = 150
        resp = brokerage_service.place_order(side='SELL', ticker='A', quantity=10)
        print(resp)
        print(brokerage_service.get_cash_value())



if __name__ == '__main__':
    unittest.main()
