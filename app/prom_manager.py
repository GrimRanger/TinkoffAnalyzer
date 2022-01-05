from prometheus_client import Gauge
from prometheus_client import start_http_server

from currencies import Currency


class PrometheusManager:

    def __init__(self, port: int):
        start_http_server(port)
        self._items = Gauge('tcs_item', 'Tinkoff portfolio items with total price',
                            ['account', 'name', 'ticker', 'currency', 'type', 'balance_currency'])
        self._yields = Gauge('tcs_yield', 'Tinkoff portfolio items with expected yield',
                             ['account', 'name', 'ticker', 'currency', 'type', 'balance_currency'])
        self._rates = Gauge('tcs_rate', 'USD/EUR rate', ['currency'])

    def set_rates(self, rates: dict[str, float]) -> None:
        eur_usd = rates['EUR'] / rates['USD']
        self._rates.labels('USDRUB').set(rates['USD'])
        self._rates.labels('EURRUB').set(rates['EUR'])
        self._rates.labels('EURUSD').set(eur_usd)

    def clear(self) -> None:
        self._items._metrics.clear()
        self._yields._metrics.clear()

    def set_position_labels(self, broker_account_type: str, position, cost_info, yield_info):
        for currency in Currency:
            cur = str(position.average_position_price.currency).upper()
            if '.' in cur:
                cur = cur.split('.')[-1]
            account = broker_account_type.capitalize()
            if 'iis' in account.lower():
                account = 'TinkoffIis'
            self._items.labels(account=account,
                               name=position.name,
                               ticker=position.ticker,
                               currency=cur,
                               type=position.instrument_type.value,
                               balance_currency=currency.value).set(cost_info[currency])

            self._yields.labels(account=account,
                                name=position.name,
                                ticker=position.ticker,
                                currency=cur,
                                type=position.instrument_type.value,
                                balance_currency=currency.value).set(yield_info[currency])

    def set_currencies_labels(self, broker_account_type: str, cost_info):

        position_name = "Рубль"
        position_ticker = "RUBRUB"
        instrument_type = "Currency"
        position_currency = "RUB"
        account = broker_account_type.capitalize()
        if 'iis' in account.lower():
            account = 'TinkoffIis'

        self._items.labels(account=account,
                           name=position_name,
                           ticker=position_ticker,
                           currency=position_currency,
                           type=instrument_type,
                           balance_currency="RUB").set(cost_info[Currency.RUB])
        self._items.labels(account=account,
                           name=position_name,
                           ticker=position_ticker,
                           currency=position_currency,
                           type=instrument_type,
                           balance_currency="USD").set(cost_info[Currency.USD])
        self._items.labels(account=account,
                           name=position_name,
                           ticker=position_ticker,
                           currency=position_currency,
                           type=instrument_type,
                           balance_currency="EUR").set(cost_info[Currency.EUR])

        self._yields.labels(account=account,
                            name=position_name,
                            ticker=position_ticker,
                            currency=position_currency,
                            type=instrument_type,
                            balance_currency="RUB").set(0)
        self._yields.labels(account=account, name=position_name, ticker=position_ticker,
                            currency=position_currency, type=instrument_type, balance_currency="USD").set(0)
        self._yields.labels(account=account, name=position_name, ticker=position_ticker,
                            currency=position_currency, type=instrument_type, balance_currency="EUR").set(0)

    def set_total_labels(self, total_info: dict):
        account_total = "_Total_"
        for currency in Currency:
            self._items.labels(account=account_total,
                               name=account_total,
                               ticker=account_total,
                               currency='Multi',
                               type=account_total,
                               balance_currency=currency.value).set(total_info['sum'][currency])
            self._yields.labels(account=account_total,
                                name=account_total,
                                ticker=account_total,
                                currency='Multi',
                                type=account_total,
                                balance_currency=currency.value).set(total_info['yield'][currency])
