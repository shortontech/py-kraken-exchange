from decimal import Decimal
from typing import Union
from ..abstract.request import Request


class WithdrawalListRequest(Request):
    nonce: Union[
        Decimal, str, None, Request.Fields.DecimalField
    ] = Request.Fields.DecimalField(required=True, location="header")
    """Nonce used in construction of API-Sign header"""

    asset: Union[
        Decimal, str, None, Request.Fields.DecimalField
    ] = Request.Fields.DecimalField(required=False, location="query")
    """Filter for specific asset being withdrawn"""

    aclass: Union[str, None, Request.Fields.CharField] = Request.Fields.CharField(
        required=False, default="currency", location="query"
    )
    """Filter for specific asset class being withdrawn"""

    method: Union[str, None, Request.Fields.CharField] = Request.Fields.CharField(
        required=False, location="query"
    )
    """Filter for specific name of withdrawal method"""

    start: Union[str, None, Request.Fields.CharField] = Request.Fields.CharField(
        required=False, location="query"
    )
    """Start timestamp, withdrawals created strictly before will not be included in the response"""

    end: Union[str, Request.Fields.CharField, None] = Request.Fields.CharField(
        required=False, location="query"
    )
    """End timestamp, withdrawals created strictly after will be not be included in the response"""

    cursor: Union[bool, Request.Fields.BoolField, None] = Request.Fields.BoolField(
        required=False, location="query"
    )
    """true/false to enable/disable paginated response (boolean) or cursor for next page of results (string), default false"""

    limit: Union[bool, Request.Fields.BoolField, None] = Request.Fields.BoolField(
        required=False, default=500, location="query"
    )
    """Number of results to include per page"""

    @classmethod
    def is_child(cls) -> bool:
        return False

    def get_method(self) -> str:
        return "POST"

    def get_path(self) -> str:
        return "/private/Withdraw"

    def get_factory_response(self, response: dict | None = None) -> dict:
        result = {
            "error": [],
            "result": [
                {
                    "method": "Bitcoin",
                    "aclass": "currency",
                    "asset": "XXBT",
                    "refid": "FTQcuak-V6Za8qrWnhzTx67yYHz8Tg",
                    "txid": "29323ce235cee8dae22503caba7....8ad3a506879a03b1e87992923d80428",
                    "info": "bc1qm32pq....3ewt0j37s2g",
                    "amount": "0.72485000",
                    "fee": "0.00020000",
                    "time": 1688014586,
                    "status": "Pending",
                    "key": "btc-wallet-1",
                },
                {
                    "method": "Bitcoin",
                    "aclass": "currency",
                    "asset": "XXBT",
                    "refid": "FTQcuak-V6Za8qrPnhsTx47yYLz8Tg",
                    "txid": "29323ce212ceb2daf81255cbea8a5...ad7a626471e05e1f82929501e82934",
                    "info": "bc1qa35ls....3egf0872h3w",
                    "amount": "0.72485000",
                    "fee": "0.00020000",
                    "time": 1688015423,
                    "status": "Failure",
                    "status-prop": "canceled",
                    "key": "btc-wallet-2",
                },
            ],
        }
        return super().get_factory_response(result)
