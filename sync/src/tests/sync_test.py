import pytest

from tests.example_token_transactions.example_1 import TRANSACTIONS1
from tests.example_token_transactions.example_2 import TRANSACTIONS2
from tests.example_token_transactions.example_3 import TRANSACTIONS3
from sync import get_token_transfers

TRANSACTIONS1_RESULT = [{
    'from_address': (
        'rdx1qsp8g2ds6pa9ntv3alvvqa6try6quxq00fwfkcgys0rvz7k5rcsh40q9s7q3g'
    ),
    'to_address': (
        'rdx1qspv65sdsnm3pqckup4garggpxhd4mt6p7ps94apgv79t9qu2g0ly2g45lljc'
    ),
    'rri': 'gnrd_rr1qv0jw6lf83d5q55plnkfcyj8yr3n2epns0zdveudwzyqtm749w',
    'transfer_amount': '1000000000000000000', 'state_version': 38138606
}]

TRANSACTIONS2_RESULT = [{
    'from_address': (
        'rdx1qsp258zf47f288g4y47hm3plsp03370safcjg5x98e6j2h66p5we8ds8m7g33'
    ),
    'to_address': (
        'rdx1qspacch6qjqy7awspx304sev3n4em302en25jd87yrh4hp47grr692cm0kv88'
    ),
    'rri': 'xrd_rr1qy5wfsfh',
    'transfer_amount': '24000000000000000000000000', 'state_version': 40898
}]

TRANSACTIONS3_RESULT = []


@pytest.mark.parametrize('transaction, expected_result', [
    ("", []),
    (TRANSACTIONS1["transactions"][0], TRANSACTIONS1_RESULT),
    (TRANSACTIONS2["transactions"][0], TRANSACTIONS2_RESULT),
    (TRANSACTIONS3["transactions"][0], TRANSACTIONS3_RESULT)
])
def test_get_token_transfers(transaction, expected_result):
    assert get_token_transfers(transaction) == expected_result
