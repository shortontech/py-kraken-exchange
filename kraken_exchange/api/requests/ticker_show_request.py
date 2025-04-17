from typing import Union
from ..abstract.request import Request


class TickerShowRequest(Request):
    pair: Union[str, Request.Fields.CharField, None] = Request.Fields.CharField(
        required=False, location="body"
    )

    @classmethod
    def is_child(cls) -> bool:
        return False

    def get_method(self) -> str:
        return "POST"

    def get_path(self) -> str:
        return "/0/public/Ticker"

    def get_factory_response(self, response: dict | None = None) -> dict:
        return {
            "error": [],
            "result": {
                "XXBTZUSD": {
                    "a": ["30300.10000", "1", "1.000"],
                    "b": ["30300.00000", "1", "1.000"],
                    "c": ["30303.20000", "0.00067643"],
                    "v": ["4083.67001100", "4412.73601799"],
                    "p": ["30706.77771", "30689.13205"],
                    "t": [34619, 38907],
                    "l": ["29868.30000", "29868.30000"],
                    "h": ["31631.00000", "31631.00000"],
                    "o": "30502.80000",
                }
            },
        }
