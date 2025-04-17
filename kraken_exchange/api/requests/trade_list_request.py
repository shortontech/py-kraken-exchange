from decimal import Decimal
from typing import Union
from ..abstract.request import Request
from datetime import datetime


class TradeListRequest(Request):
    pair: Union[str, Request.Fields.CharField, None] = Request.Fields.CharField(
        required=True, location="path"
    )
    since: Union[
        Decimal, int, str, datetime, Request.Fields.DecimalField, None
    ] = Request.Fields.DecimalField(required=False, location="path")
    count: Union[
        Decimal, int, str, datetime, Request.Fields.DecimalField, None
    ] = Request.Fields.DecimalField(required=False, min=1, max=1000, location="path")

    @classmethod
    def is_child(cls) -> bool:
        return False

    @classmethod
    def get_method(self) -> str:
        return "GET"

    def get_path(self) -> str:
        return "/0/private/TradesHistory"

    def get_factory_response(self, response: dict | None = None) -> dict:
        result = {
            "error": [],
            "result": {
                "XXBTZUSD": [
                    [
                        "30243.40000",
                        "0.34507674",
                        1688669597.8277369,
                        "b",
                        "m",
                        "",
                        61044952,
                    ],
                    [
                        "30243.30000",
                        "0.00376960",
                        1688669598.2804112,
                        "s",
                        "l",
                        "",
                        61044953,
                    ],
                    [
                        "30243.30000",
                        "0.01235716",
                        1688669602.698379,
                        "s",
                        "m",
                        "",
                        61044956,
                    ],
                ],
                "last": "1688671969993150842",
            },
        }
        return super().get_factory_response(result)
