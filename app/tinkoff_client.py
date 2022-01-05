#!/usr/bin/env python3

import time
import logging

import tinvest
from database import Database
from currencies import currencies_data

logger = logging.getLogger('Parser')
logger.setLevel(logging.INFO)


class TinkoffClient:

    def __init__(self, token: str):
        self._database = Database()
        self._client = tinvest.SyncClient(token)

    def get_current_market_price(self, figi: str, depth: int = 0, max_age: int = 10 * 60):
        price = self._database.get_market_price_by_figi(figi, max_age)
        if price:
            return price
        try:
            book = self._client.get_market_orderbook(figi=figi, depth=depth)
            price = book.payload.last_price
        except tinvest.exceptions.TooManyRequestsError:
            logger.warning('Превышена частота запросов API. Пауза выполнения.')
            time.sleep(0.5)
            return self.get_current_market_price(figi, depth, max_age)
        self._database.put_market_price(figi, price)
        return price

    def get_market_rates(self) -> dict[str, int]:

        market_rate_today = {}
        for currency, data in currencies_data.items():
            if 'figi' in data.keys():
                market_rate_today[currency] = self.get_current_market_price(figi=data['figi'], depth=0)
            else:
                market_rate_today[currency] = 1

        return market_rate_today

    def get_accounts(self):

        accounts = self._client.get_accounts()
        logging.debug(accounts)
        logger.info('accounts received')

        return accounts.payload.accounts

    def get_portfolio(self, broker_account_id: str):

        return self._client.get_portfolio(broker_account_id=broker_account_id)

    def get_currencies(self, broker_account_id):

        return self._client.get_portfolio_currencies(broker_account_id=broker_account_id)
