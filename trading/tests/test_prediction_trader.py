import unittest
from datetime import datetime, timedelta
from unittest import mock, TestCase
from unittest.mock import Mock

from brokerage.apiclient.interactivebrokers.order_status_response import OrderStatusResponse
from brokerage.brokerage_service import BrokerageService, OrderSide
from brokerage.ib_brokerage_service import Quote
from prediction.prediction_provider import PredictionProvider, Prediction
from trading.positions import Positions, PositionValues
from trading.prediction_bucket import PredictionBucket
from trading.prediction_trader import PredictionTrader
from trading.trader import Trader


class BrokerageServiceConcrete:

    def place_order(self, side: str, ticker: str, quantity: int):
        pass

    def get_quote(self, ticker: str):
        pass

    def get_cash_value(self):
        pass

    def get_order_status(self, order_id: str):
        pass


class PredictionProviderConcrete:

    def predict(self, ticker) -> Prediction:
        pass


class TraderTestCase(TestCase):

    def setUp(self):
        broker: BrokerageService = BrokerageServiceConcrete()
        broker.get_quote = Mock()
        broker.get_quote = Mock()
        broker.place_order = Mock()
        broker.get_cash_value = Mock()
        broker.get_order_status = Mock()
        predictor: PredictionProvider = PredictionProviderConcrete()
        predictor.predict = Mock()
        positions = Positions()
        #self.trader: Trader = PredictionTrader(tickers=[], broker=broker, predictor=predictor, positions=positions)
        self.trader: Trader = PredictionTrader(tickers=[], broker=broker, predictor=predictor)
        self.trader.build_prediction_buckets(end_date=datetime(2022, 11, 11))

    def test_check_sell_prediction__ticker_not_in_sell_bucket(self):
        #self.trader.positions = Positions()
        positions = Positions()
        enter_day = datetime.now() - timedelta(days=5)
        #self.trader.positions['A'] = PositionValues(price=5.0, quantity=10, enter_day=enter_day, order_id='123')
        positions['A'] = PositionValues(price=5.0, quantity=10, enter_day=enter_day, order_id='123')

        #self.trader.check_sell(sell_trigger=Mock(return_value=False))
        self.trader.check_sell(positions=positions, sell_trigger=Mock(return_value=False))

        self.trader.broker.place_order.assert_not_called()
        #assert 'A' in self.trader.positions
        assert 'A' in positions
        #values: PositionValues = self.trader.positions['A']
        values: PositionValues = positions['A']
        assert values.order_id == '123'
        assert values.enter_day == enter_day
        assert values.quantity == 10

    def test_check_sell_prediction__ticker_in_sell_bucket(self):
        #self.trader.positions = Positions()
        positions = Positions()
        enter_day = datetime.now() - timedelta(days=5)
        #self.trader.positions['A'] = PositionValues(price=5.0, quantity=10, enter_day=enter_day, order_id='123')
        positions['A'] = PositionValues(price=5.0, quantity=10, enter_day=enter_day, order_id='123')
        self.trader.sell_prediction_bucket['A'] = Prediction(label=1, probability=45.0)
        order_status_response = OrderStatusResponse.construct(**{'order_status': 'Filled'})
        self.trader.broker.place_order = Mock(return_value=order_status_response)

        self.trader.check_sell(positions=positions, sell_trigger=Mock(return_value=False))

        self.trader.broker.place_order.assert_called_once_with(side=OrderSide.SELL, ticker='A', quantity=10)
        #assert len(self.trader.positions) == 0
        assert len(positions) == 0

    def test_check_sell_prediction__ticker_in_sell_bucket_sell_order_not_filled(self):
        #self.trader.positions = Positions()
        positions = Positions()
        enter_day = datetime.now() - timedelta(days=5)
        #self.trader.positions['A'] = PositionValues(price=5.0, quantity=10, enter_day=enter_day, order_id='123')
        positions['A'] = PositionValues(price=5.0, quantity=10, enter_day=enter_day, order_id='123')
        self.trader.sell_prediction_bucket['A'] = Prediction(label=1, probability=45.0)
        order_status_response = OrderStatusResponse.construct(**{'order_status': 'Submitted'})
        self.trader.broker.place_order = Mock(return_value=order_status_response)

        #self.trader.check_sell(sell_trigger=Mock(return_value=False))
        self.trader.check_sell(positions=positions, sell_trigger=Mock(return_value=False))

        self.trader.broker.place_order.assert_called_once_with(side=OrderSide.SELL, ticker='A', quantity=10)
        #assert len(self.trader.positions) == 1
        assert len(positions) == 1

    def test_check_sell__is_sell_trigger_true(self):
        #self.trader.positions = Positions()
        positions = Positions()
        enter_day = datetime.now() - timedelta(days=5)
        #self.trader.positions['A'] = PositionValues(price=5.0, quantity=10, enter_day=enter_day, order_id='123')
        positions['A'] = PositionValues(price=5.0, quantity=10, enter_day=enter_day, order_id='123')
        order_status_response = OrderStatusResponse.construct(**{'order_status': 'Filled'})
        self.trader.broker.place_order = Mock(return_value=order_status_response)

        #self.trader.check_sell(sell_trigger=Mock(return_value=True))
        self.trader.check_sell(positions=positions, sell_trigger=Mock(return_value=True))

        self.trader.broker.place_order.assert_called_once_with(side=OrderSide.SELL, ticker='A', quantity=10)
        #assert len(self.trader.positions) == 0
        assert len(positions) == 0

    def test_check_sell__is_sell_trigger_true_2_out_of_3(self):
        #self.trader.positions = Positions(3)
        positions = Positions(3)
        enter_day = datetime.now() - timedelta(days=5)
        #self.trader.positions['A'] = PositionValues(price=5.0, quantity=10, enter_day=enter_day, order_id='1')
        #self.trader.positions['B'] = PositionValues(price=4.0, quantity=15, enter_day=enter_day, order_id='2')
        #self.trader.positions['C'] = PositionValues(price=3.0, quantity=20, enter_day=enter_day, order_id='3')
        positions['A'] = PositionValues(price=5.0, quantity=10, enter_day=enter_day, order_id='1')
        positions['B'] = PositionValues(price=4.0, quantity=15, enter_day=enter_day, order_id='2')
        positions['C'] = PositionValues(price=3.0, quantity=20, enter_day=enter_day, order_id='3')
        order_status_response1 = OrderStatusResponse.construct(**{'order_status': 'Filled'})
        order_status_response2 = OrderStatusResponse.construct(**{'order_status': 'Filled'})
        self.trader.broker.place_order = Mock(side_effect=[order_status_response1, order_status_response2])

        #self.trader.check_sell(sell_trigger=Mock(side_effect=[True, False, True]))
        self.trader.check_sell(positions=positions, sell_trigger=Mock(side_effect=[True, False, True]))

        self.trader.broker.place_order.assert_any_call(side=OrderSide.SELL, ticker='A', quantity=10)
        self.trader.broker.place_order.assert_any_call(side=OrderSide.SELL, ticker='C', quantity=20)
        #assert len(self.trader.positions) == 1
        #assert 'B' in self.trader.positions
        assert len(positions) == 1
        assert 'B' in positions

    def test_check_sell_prediction__ticker_in_sell_bucket_2_in_sell_bucket_out_of_3(self):
        self.trader.positions = Positions(3)
        enter_day = datetime.now() - timedelta(days=5)
        self.trader.positions['A'] = PositionValues(price=5.0, quantity=10, enter_day=enter_day, order_id='1')
        self.trader.positions['B'] = PositionValues(price=4.0, quantity=15, enter_day=enter_day, order_id='2')
        self.trader.positions['C'] = PositionValues(price=3.0, quantity=20, enter_day=enter_day, order_id='3')
        self.trader.sell_prediction_bucket['A'] = Prediction(label=1, probability=45.0)
        self.trader.sell_prediction_bucket['C'] = Prediction(label=1, probability=44.0)
        order_status_response1 = OrderStatusResponse.construct(**{'order_status': 'Filled'})
        order_status_response2 = OrderStatusResponse.construct(**{'order_status': 'Filled'})
        self.trader.broker.place_order = Mock(side_effect=[order_status_response1, order_status_response2])

        self.trader.check_sell(sell_trigger=Mock(side_effect=[False, False, False]))

        self.trader.broker.place_order.assert_any_call(side=OrderSide.SELL, ticker='A', quantity=10)
        self.trader.broker.place_order.assert_any_call(side=OrderSide.SELL, ticker='C', quantity=20)
        assert len(self.trader.positions) == 1
        assert 'B' in self.trader.positions

    def test_check_sell_prediction__ticker_1_sell_trigger_2_in_sell_bucket(self):
        positions = Positions(3)
        enter_day = datetime.now() - timedelta(days=5)
        positions['A'] = PositionValues(price=5.0, quantity=10, enter_day=enter_day, order_id='1')
        positions['B'] = PositionValues(price=4.0, quantity=15, enter_day=enter_day, order_id='2')
        positions['C'] = PositionValues(price=3.0, quantity=20, enter_day=enter_day, order_id='3')
        self.trader.sell_prediction_bucket['A'] = Prediction(label=1, probability=45.0)
        self.trader.sell_prediction_bucket['C'] = Prediction(label=1, probability=44.0)
        order_status_response1 = OrderStatusResponse.construct(**{'order_status': 'Filled'})
        order_status_response2 = OrderStatusResponse.construct(**{'order_status': 'Filled'})
        order_status_response3 = OrderStatusResponse.construct(**{'order_status': 'Filled'})
        self.trader.broker.place_order = Mock(side_effect=[order_status_response1,
                                                           order_status_response2,
                                                           order_status_response3])

        self.trader.check_sell(positions=positions, sell_trigger=Mock(side_effect=[False, True, False]))

        self.trader.broker.place_order.assert_any_call(side=OrderSide.SELL, ticker='A', quantity=10)
        self.trader.broker.place_order.assert_any_call(side=OrderSide.SELL, ticker='B', quantity=15)
        self.trader.broker.place_order.assert_any_call(side=OrderSide.SELL, ticker='C', quantity=20)
        assert len(positions) == 0

    @mock.patch('trading.prediction_trader.datetime')
    def test_check_buy_prediction__one_position_and_one_buy_prediction(self, mocker_datetime):
        self.trader.broker.get_quote = Mock(return_value=Quote(ask=5.0, bid=5.0, last=5.0))
        self.trader.broker.place_order = Mock(return_value='123')
        self.trader.positions = Positions()
        self.trader.buy_prediction_bucket = PredictionBucket()
        # just to get the buy_bucket to have len of 1
        self.trader.buy_prediction_bucket['A'] = 1
        self.trader.buy_prediction_bucket.sorted_get = Mock(return_value='A')
        mocker_datetime.now = mock.Mock(return_value=datetime(2022, 8, 10))
        assert len(self.trader.positions) == 0
        order_status_response = OrderStatusResponse.construct(**{'order_status': 'Filled',
                                                                 'order_id': '123',
                                                                 'average_price': '5.0'})
        self.trader.broker.place_order = Mock(return_value=order_status_response)

        self.trader.check_buy(cash=1000)

        self.trader.broker.place_order.assert_called_once_with(side='BUY', ticker='A', quantity=200)
        assert len(self.trader.positions) == 1
        assert 'A' in self.trader.positions
        values: PositionValues = self.trader.positions['A']
        assert values.order_id == '123'
        assert values.enter_day == datetime(2022, 8, 10)
        assert values.quantity == 200

    @mock.patch('trading.prediction_trader.datetime')
    def test_check_buy_prediction__one_position_and_one_buy_prediction_buy_order_not_filled(self, mocker_datetime):
        self.trader.broker.get_quote = Mock(return_value=Quote(ask=5.0, bid=5.0, last=5.0))
        self.trader.broker.place_order = Mock(return_value='123')
        #self.trader.positions = Positions()
        positions = Positions()
        self.trader.buy_prediction_bucket = PredictionBucket()
        # just to get the buy_bucket to have len of 1
        self.trader.buy_prediction_bucket['A'] = 1
        self.trader.buy_prediction_bucket.sorted_get = Mock(return_value='A')
        mocker_datetime.now = mock.Mock(return_value=datetime(2022, 8, 10))
        #assert len(self.trader.positions) == 0
        assert len(positions) == 0
        order_status_response = OrderStatusResponse.construct(**{'order_status': 'Submitted', 'order_id': '123'})
        self.trader.broker.place_order = Mock(return_value=order_status_response)

        self.trader.check_buy(positions=positions, cash=1000)

        self.trader.broker.place_order.assert_called_once_with(side='BUY', ticker='A', quantity=200)
        #assert len(self.trader.positions) == 0
        assert len(positions) == 0

    def test_check_buy_prediction__one_position_and_no_buy_prediction(self):
        positions = Positions()
        self.trader.buy_prediction_bucket = PredictionBucket()
        assert len(positions) == 0

        self.trader.check_buy(positions=positions, cash=1000)

        self.trader.broker.place_order.assert_not_called()
        assert len(positions) == 0

    @mock.patch('trading.prediction_trader.datetime')
    def test_check_buy_prediction__two_positions_and_one_buy_prediction(self, mocker_datetime):
        self.trader.broker.get_quote = Mock(return_value=Quote(ask=5.0, bid=5.0, last=5.0))
        self.trader.broker.place_order = Mock(return_value='123')
        positions = Positions(max_positions=2)
        self.trader.buy_prediction_bucket = PredictionBucket()
        # just to get the buy_bucket to have len of 1
        self.trader.buy_prediction_bucket['A'] = 1
        self.trader.buy_prediction_bucket.sorted_get = Mock(return_value='A')
        mocker_datetime.now = mock.Mock(return_value=datetime(2022, 8, 10))
        assert len(positions) == 0
        order_status_response = OrderStatusResponse.construct(**{'order_status': 'Filled',
                                                                 'order_id': '123',
                                                                 'average_price': '5.0'})
        self.trader.broker.place_order = Mock(return_value=order_status_response)

        self.trader.check_buy(positions=positions, cash=1000)

        self.trader.broker.place_order.assert_called_once_with(side='BUY', ticker='A', quantity=200)
        assert len(positions) == 1
        assert 'A' in positions
        values: PositionValues = positions['A']
        assert values.order_id == '123'
        assert values.enter_day == datetime(2022, 8, 10)
        assert values.quantity == 200

    @mock.patch('trading.prediction_trader.datetime')
    def test_check_buy_prediction__two_positions_and_two_buy_predictions(self, mocker_datetime):
        self.trader.broker.get_quote = Mock(side_effect=[Quote(ask=5.0, bid=5.0, last=5.0),
                                                         Quote(ask=10.0, bid=10.0, last=10.0)])
        self.trader.broker.place_order = Mock(side_effect=['123', '456'])
        positions = Positions(max_positions=2)
        self.trader.buy_prediction_bucket = PredictionBucket()
        self.trader.buy_prediction_bucket.sorted_get = Mock(side_effect=['A', 'B'])
        # just to get the buy_bucket to have len of 2
        self.trader.buy_prediction_bucket['A'] = 1
        self.trader.buy_prediction_bucket['B'] = 2
        self.trader.buy_prediction_bucket.size = Mock(return_value=2)
        mocker_datetime.now = mock.Mock(return_value=datetime(2022, 8, 10))
        assert len(positions) == 0
        order_status_response1 = OrderStatusResponse.construct(**{'order_status': 'Filled',
                                                                  'order_id': '123',
                                                                  'average_price': '5.0'})
        order_status_response2 = OrderStatusResponse.construct(**{'order_status': 'Filled',
                                                                  'order_id': '456',
                                                                  'average_price': '10.0'})
        self.trader.broker.place_order = Mock(side_effect=[order_status_response1, order_status_response2])

        self.trader.check_buy(positions=positions, cash=1000)
        self.trader.broker.place_order.assert_any_call(side='BUY', ticker='A', quantity=100)
        self.trader.broker.place_order.assert_any_call(side='BUY', ticker='B', quantity=50)

        assert len(positions) == 2

        assert 'A' in positions
        values1: PositionValues = positions['A']
        assert values1.order_id == '123'
        assert values1.enter_day == datetime(2022, 8, 10)
        assert values1.quantity == 100

        assert 'B' in positions
        values2: PositionValues = positions['B']
        assert values2.order_id == '456'
        assert values2.enter_day == datetime(2022, 8, 10)
        assert values2.quantity == 50


if __name__ == '__main__':
    unittest.main()
