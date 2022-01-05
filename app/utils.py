from typing import Any

from currencies import Currency


def calc_in_currencies(currency: str, value: int, balance: int, rate: dict) -> dict[Currency, int | Any]:

    match currency:
        case Currency.RUB.value:
            return {
                Currency.RUB: value * balance,
                Currency.EUR: value * balance / rate['EUR'],
                Currency.USD: value * balance / rate['USD']
            }
        case Currency.USD.value:
            return {
                Currency.RUB: value * balance * rate['USD'],
                Currency.EUR: value * balance * rate['EUR'] / rate['USD'],
                Currency.USD: value * balance
            }
        case Currency.EUR.value:
            return {
                Currency.RUB: value * balance * rate['EUR'],
                Currency.EUR: value * balance,
                Currency.USD: value * balance * rate['USD'] / rate['EUR']
            }
        case _:
            return {
                Currency.RUB: 0,
                Currency.EUR: 0,
                Currency.USD: 0
            }
