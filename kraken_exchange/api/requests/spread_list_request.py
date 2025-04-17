from typing import Union
from ..abstract.request import Request
from decimal import Decimal
from datetime import datetime


class SpreadListRequest(Request):
    pair: Union[str, Request.Fields.CharField, None] = Request.Fields.CharField(
        required=True, location="path"
    )
    since: Union[
        Decimal, int, str, datetime, Request.Fields.DecimalField, None
    ] = Request.Fields.DecimalField(required=False, location="path")

    @classmethod
    def is_child(cls) -> bool:
        return False

    def get_method(self) -> str:
        return "GET"

    def get_path(self) -> str:
        return "/0/public/Trades"

    def get_factory_response(self, response: dict | None = None) -> dict:
        result = {
            "error": [],
            "result": {
                "error": [],
                "result": {
                    "XXBTZUSD": [
                        [1688671834, "30292.10000", "30297.50000"],
                        [1688671834, "30292.10000", "30296.70000"],
                        [1688671834, "30292.70000", "30296.70000"],
                    ],
                    "last": 1688672106,
                },
            },
        }
        return super().get_factory_response(result)
