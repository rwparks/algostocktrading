import unittest
from datetime import datetime
from unittest import mock, TestCase
from unittest.mock import mock_open

from datautils.object_serialization import ObjectSerialization
from datautils.persistence_provider import PersistenceProvider
from trading.positions import Positions, PositionValues


class PositionsTestCase(TestCase):

    def test__one_position_available_one_set(self):
        persistence_provider: PersistenceProvider = ObjectSerialization(persist_dir='./data')
        positions = Positions(persistence_provider=persistence_provider)
        today = datetime(2022, 8, 8)
        assert positions.available == 1
        positions['A'] = PositionValues(quantity=1, enter_day=today, price=5, order_id='123')

        result = []
        for ticker, value in positions.items():
            result.append((ticker, value))

        assert len(positions) == 1
        assert positions.available == 0
        assert result == [('A', PositionValues(quantity=1, enter_day=today, price=5, order_id='123'))]

    def test__for_warning_trying_to_set_more_than_nax_positions(self):
        persistence_provider: PersistenceProvider = ObjectSerialization(persist_dir='./data')
        positions = Positions(persistence_provider=persistence_provider)
        today = datetime(2022, 8, 8)
        caught_exc = False
        assert positions.available == 1
        try:
            positions['A'] = PositionValues(quantity=1, enter_day=today, price=5, order_id='123')
            positions['B'] = PositionValues(quantity=2, enter_day=today, order_id='124')
        except RuntimeWarning:
            caught_exc = True

        result = []
        for ticker, value in positions.items():
            result.append((ticker, value))

        assert caught_exc
        assert len(positions) == 1
        assert positions.available == 0
        assert result == [('A', PositionValues(quantity=1, enter_day=today, price=5, order_id='123'))]

    def test__available_positions(self):
        persistence_provider: PersistenceProvider = ObjectSerialization(persist_dir='./data')
        positions = Positions(persistence_provider=persistence_provider, max_positions=3)
        today = datetime(2022, 8, 8)
        assert positions.available == 3
        positions['A'] = PositionValues(quantity=3, enter_day=today, price=5, order_id='123')
        assert positions.available == 2
        positions['B'] = PositionValues(quantity=2, enter_day=today, price=10, order_id='456')
        assert positions.available == 1
        positions['C'] = PositionValues(quantity=3, enter_day=today, price=15, order_id='789')
        assert positions.available == 0

    def test__save(self):
        persistence_provider: PersistenceProvider = ObjectSerialization(persist_dir='./data')
        #positions = Positions(max_positions=3, dir='../../tests/test')
        #positions = Positions(persistence_provider=persistence_provider, max_positions=3, dir='./data')
        positions = Positions(persistence_provider=persistence_provider, max_positions=3)
        # print(positions)
        today = datetime(2022, 8, 8)
        positions['A'] = PositionValues(quantity=3, enter_day=today, price=5, order_id='123')
        positions['B'] = PositionValues(quantity=2, enter_day=today, price=10, order_id='456')
        # positions['C'] = PositionValues(quantity=3, enter_day=today, price=15, order_id='789')
        positions.save()

    def test__load(self):
        persistence_provider: PersistenceProvider = ObjectSerialization(persist_dir='./data')
        #positions = Positions(dir='../../tests/test').load()
        #positions = Positions(dir='./data').load()
        positions = Positions(persistence_provider=persistence_provider).load()
        print(positions.available)
        today = datetime(2022, 8, 8)
        positions['C'] = PositionValues(quantity=3, enter_day=today, price=15, order_id='789')
        print(positions)

    @mock.patch('trading.positions.pickle')
    @mock.patch("builtins.open", new_callable=mock_open)
    @mock.patch('trading.positions.os.path')
    @mock.patch('trading.positions.os')
    def test__save2(self, mock_os, mock_path, mock_file, mock_pickle):
        positions = Positions(max_positions=1, dir='./xyz')

        mock_path.isdir.return_value = False
        positions.save()
        mock_os.mkdir.assert_called_with('./xyz')
        mock_pickle.dump.assert_called()

    @mock.patch('trading.positions.pickle')
    @mock.patch("builtins.open", new_callable=mock_open)
    @mock.patch('trading.positions.os.path')
    @mock.patch('trading.positions.os')
    def test__save2(self, mock_os, mock_path, mock_file, mock_pickle):
        positions = Positions(max_positions=1, dir='./xyz')

        mock_path.isdir.return_value = True
        positions.save()
        mock_os.mkdir.assert_not_called()
        mock_pickle.dump.assert_called()


if __name__ == '__main__':
    unittest.main()
