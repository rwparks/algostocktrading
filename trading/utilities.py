from datetime import datetime, timedelta


def is_sell_trigger(price: float, quote: float, enter_day: datetime) -> bool:
    gain_target_met = quote > (price + (price * 0.04))
    loss_target_met = quote < (price - (price * 0.003))
    held_time_exceeded = enter_day + timedelta(days=10) <= datetime.now()
    return gain_target_met or loss_target_met or held_time_exceeded
