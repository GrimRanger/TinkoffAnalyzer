"""
    Хранилище данных о валютах
"""

import enum


class Currency(enum.Enum):

    RUB = 'RUB'
    USD = 'USD'
    EUR = 'EUR'


currencies_data = {
    'RUB': {
        'name': 'Российский рубль',
        'num_format': '## ### ##0.00   [$₽-ru-RU]',
    },
    'USD': {
        'name': 'Доллар США',
        'num_format': '## ### ##0.00   [$$-409]',
        'figi': 'BBG0013HGFT4',
    },
    'EUR': {
        'name': 'Евро',
        'num_format': '## ### ##0.00   [$€-x-euro1]',
        'figi': 'BBG0013HJJ31',
    }
}
