from datetime import timedelta, datetime
from trading.utilities import is_sell_trigger


def test_is_sell_trigger():
    enter_day = datetime.now()
    assert is_sell_trigger(1.00, 1.00, enter_day - timedelta(days=10))
    assert not is_sell_trigger(1.00, 1.00, enter_day - timedelta(days=9))
    assert is_sell_trigger(1.00, 1.041, enter_day - timedelta(days=1))
    assert not is_sell_trigger(1.00, 1.04, enter_day - timedelta(days=1))
    assert is_sell_trigger(1.00, 0.996, enter_day - timedelta(days=1))
    assert not is_sell_trigger(1.00, 0.997, enter_day - timedelta(days=1))
