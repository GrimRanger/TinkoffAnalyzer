import os
import time
from tinkoff_client import TinkoffClient
from prom_manager import PrometheusManager
from currencies import Currency
from utils import calc_in_currencies

TOKEN = os.getenv('TINVEST_TOKEN', '')
UPDATE_PERIOD = os.getenv('PROMTI_UPDATE', 600)
LISTEN_PORT = os.getenv('PROMETHEUS_PORT', 40010)

DEBUG_LEVEL = os.getenv('DEBUG_LEVEL', 0)


def main():
    print('Starting http server')
    prom_manager = PrometheusManager(LISTEN_PORT)

    while True:
        tinkoff_client = TinkoffClient(TOKEN)
        total_info = {
            'sum':
                {
                    Currency.RUB: 0,
                    Currency.EUR: 0,
                    Currency.USD: 0
                },
            'yield':
                {
                    Currency.RUB: 0,
                    Currency.EUR: 0,
                    Currency.USD: 0
                },
        }

        rates = tinkoff_client.get_market_rates()
        prom_manager.set_rates(rates)
        prom_manager.clear()
        accounts = tinkoff_client.get_accounts()

        for account in accounts:
            print(f'account={account.broker_account_type.name}')
            portfolio = tinkoff_client.get_portfolio(broker_account_id=account.broker_account_id)

            for position in portfolio.payload.positions:
                cost_info = calc_in_currencies(position.average_position_price.currency,
                                               position.average_position_price.value,
                                               position.balance,
                                               rates)
                yield_info = calc_in_currencies(position.expected_yield.currency,
                                                position.expected_yield.value,
                                                1,
                                                rates)
                total_info['sum'][Currency.RUB] += cost_info[Currency.RUB]
                total_info['sum'][Currency.USD] += cost_info[Currency.USD]
                total_info['sum'][Currency.EUR] += cost_info[Currency.EUR]
                total_info['yield'][Currency.RUB] += yield_info[Currency.RUB]
                total_info['yield'][Currency.USD] += yield_info[Currency.USD]
                total_info['yield'][Currency.EUR] += yield_info[Currency.EUR]

                # for better portfolio diversification visibility
                if position.ticker == 'USD000UTSTOM':
                    position.average_position_price.currency = 'USD'
                elif position.ticker == 'EUR_RUB__TOM':
                    position.average_position_price.currency = 'EUR'

                prom_manager.set_position_labels(account.broker_account_type.name, position, cost_info, yield_info)

            pf = tinkoff_client.get_currencies(broker_account_id=account.broker_account_id)
            for position in pf.payload.currencies:
                if position.currency != 'RUB':
                    continue
                cost_info = calc_in_currencies(position.currency, 1, position.balance, rates)
                total_info['sum'][Currency.RUB] += cost_info[Currency.RUB]
                total_info['sum'][Currency.USD] += cost_info[Currency.USD]
                total_info['sum'][Currency.EUR] += cost_info[Currency.EUR]

                prom_manager.set_currencies_labels(account.broker_account_type.name, cost_info)

        prom_manager.set_total_labels(total_info)

        time.sleep(UPDATE_PERIOD)


if __name__ == '__main__':
    main()
    print('Exiting')
    exit(0)
