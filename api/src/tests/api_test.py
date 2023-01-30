from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from api import (ADDRESSES_TO_MONITOR_KEY, FILTER_TRANSFERS_DATA_PATH,
                 MONITOR_DATA_PATH, SERVICE_STATUS_PATH, TRANSFERS_DATA_PATH,
                 TRANSFERS_KEY)
from main import app

# TODO: test remaing enpoints

TRANSACTIONS1 = [
    {
        'from_address': (
            'rdx1qsp258zf47f288g4y47hm3plsp03370safcjg5x98e6j2h66p5we8ds8m7g33'
        ),
        'to_address': (
            'rdx1qspacch6qjqy7awspx304sev3n4em302en25jd87yrh4hp47grr692cm0kv88'
        ),
        'rri': 'xrd_rr1qy5wfsfh',
        'transfer_amount': 24000000000000000000000000, 'state_version': 40898
    },
    {
        'from_address': (
            'rdx1qsp8g2ds6pa9ntv3alvvqa6try6quxq00fwfkcgys0rvz7k5rcsh40q9s7q3g'
        ),
        'to_address': (
            'rdx1qspv65sdsnm3pqckup4garggpxhd4mt6p7ps94apgv79t9qu2g0ly2g45lljc'
        ),
        'rri': 'gnrd_rr1qv0jw6lf83d5q55plnkfcyj8yr3n2epns0zdveudwzyqtm749w',
        'transfer_amount': 1000000000000000000, 'state_version': 38138606
    }
]


def test_get_status_api():
    with TestClient(app) as client:
        response = client.get(SERVICE_STATUS_PATH)
    assert response.status_code == 200
    assert response.json() == {"message": "Backend service is available"}


@pytest.mark.parametrize('query_param, transactions, expected_result', [
    ("", [], []),
    ("1", None, []),
    ("1", TRANSACTIONS1, []),
    (
        "rdx1qsp8g2ds6pa9ntv3alvvqa6try6quxq00fwfkcgys0rvz7k5rcsh40q9s7q3g",
        TRANSACTIONS1, []
    ),
    (
        TRANSACTIONS1[1]["to_address"], TRANSACTIONS1,
        [TRANSACTIONS1[1]]
    ),
    (
        TRANSACTIONS1[1]["rri"], TRANSACTIONS1,
        [TRANSACTIONS1[1]]
    ),
])
@patch("api.cache_transfers", new_callable=AsyncMock)
def test_get_filtered_transfers(
    mocked_cache_transfers, query_param, transactions, expected_result
):
    mocked_cache_transfers.get.return_value = transactions
    with TestClient(app) as client:
        response = client.get(FILTER_TRANSFERS_DATA_PATH.format(
            item_id=query_param)
        )
    mocked_cache_transfers.get.assert_called_with(TRANSFERS_KEY)
    assert response.status_code == 200
    assert response.json() == expected_result


@pytest.mark.parametrize('transactions, expected_result', [
    (None, []),
    ([], []),
    (TRANSACTIONS1, TRANSACTIONS1),
])
@patch("api.cache_transfers", new_callable=AsyncMock)
def test_get_transfers(mocked_cache_transfers, transactions, expected_result):
    mocked_cache_transfers.get.return_value = transactions
    with TestClient(app) as client:
        response = client.get(TRANSFERS_DATA_PATH)
    mocked_cache_transfers.get.assert_called_with(TRANSFERS_KEY)
    assert response.status_code == 200
    assert response.json() == expected_result


@pytest.mark.parametrize(
    'req_data, already_stored_addresses, expected_write',
    [
        ({"addresses": []}, [], []),
        ({"addresses": ["1"]}, [], ["1"]),
        ({"addresses": ["1"]}, ["1"], ["1"]),
        ({"addresses": ["1", "2"]}, ["1"], ["1", "2"]),
    ]
)
@patch("api.cache_main", new_callable=AsyncMock)
def test_post_monitor(
    mocked_cache_main, req_data, already_stored_addresses, expected_write
):
    mocked_cache_main.get.side_effect = [
        already_stored_addresses, expected_write
    ]
    with TestClient(app) as client:
        response = client.post(
            MONITOR_DATA_PATH,
            json=req_data
            )
    call_args = mocked_cache_main.set.call_args_list
    assert len(call_args) == 1
    call_args = call_args[0][0]
    assert ADDRESSES_TO_MONITOR_KEY == call_args[0]
    assert len(call_args[1]) == len(expected_write)
    for address in expected_write:
        assert address in expected_write
    assert response.status_code == 200


@patch("api.cache_main", new_callable=AsyncMock)
def test_delete_monitor(mocked_cache_main):
    mocked_cache_main.get.return_value = None
    with TestClient(app) as client:
        response = client.delete(MONITOR_DATA_PATH)
    mocked_cache_main.delete.assert_called_with(ADDRESSES_TO_MONITOR_KEY)
    assert response.status_code == 200
