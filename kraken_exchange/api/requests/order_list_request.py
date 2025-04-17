import datetime
from decimal import Decimal
from typing import Union
from ..abstract.request import Request


class OrderListRequest(Request):

    include_trades = Request.Fields.BoolField(
        required=True, location="body", default=False, alias="trades"
    )
    """Whether or not to include trades related to position in output"""

    userref: Union[
        Decimal, int, str, datetime.datetime, Request.Fields.DecimalField, None
    ] = Request.Fields.DecimalField(
        required=False, location="body", default=None, alias="userref"
    )
    """Restrict results to given user reference id"""

    start: Union[
        Decimal, int, str, datetime.datetime, Request.Fields.DecimalField, None
    ] = Request.Fields.DecimalField(
        required=False, location="body", default=None, alias="start"
    )
    """Starting unix timestamp or order tx ID of results (exclusive)"""

    end: Union[
        Decimal, int, str, datetime.datetime, Request.Fields.DecimalField, None
    ] = Request.Fields.DecimalField(
        required=False, location="body", default=None, alias="end"
    )
    """Ending unix timestamp or order tx ID of results (inclusive)"""

    ofs: Union[
        Decimal, int, str, datetime.datetime, Request.Fields.DecimalField, None
    ] = Request.Fields.DecimalField(
        required=False, location="body", default=None, alias="ofs"
    )
    """Result offset for pagination"""

    close_time: Union[str, Request.Fields.CharField, None] = Request.Fields.CharField(
        required=False,
        location="body",
        default=None,
        alias="closetime",
        values=["open", "close", "both"],
    )
    """
    Default: "both"
    Enum: "open" "close" "both"
    Which time to use to search
    """

    consolidate_taker = Request.Fields.BoolField(
        required=False, location="body", default=True
    )
    """
    Default: true
    Whether or not to consolidate trades by individual taker trades
    """

    pair: Union[str, Request.Fields.CharField, None] = Request.Fields.CharField(
        required=True, location="body"
    )

    @classmethod
    def is_child(cls) -> bool:
        return False

    def get_method(self) -> str:
        return "POST"

    def get_path(self) -> str:
        return "/0/private/ClosedOrders"

    def get_factory_response(self, response: dict | None = None) -> dict:
        result = {
            "error": [],
            "result": {
                "closed": {
                    "O37652-RJWRT-IMO74O": {
                        "refid": "None",
                        "userref": 1,
                        "status": "canceled",
                        "reason": "User requested",
                        "opentm": 1688148493.7708,
                        "closetm": 1688148610.0482,
                        "starttm": 0,
                        "expiretm": 0,
                        "descr": {
                            "pair": "XBTGBP",
                            "type": "buy",
                            "ordertype": "stop-loss-limit",
                            "price": "23667.0",
                            "price2": "0",
                            "leverage": "none",
                            "order": "buy 0.00100000 XBTGBP @ limit 23667.0",
                            "close": "",
                        },
                        "vol": "0.00100000",
                        "vol_exec": "0.00000000",
                        "cost": "0.00000",
                        "fee": "0.00000",
                        "price": "0.00000",
                        "stopprice": "0.00000",
                        "limitprice": "0.00000",
                        "misc": "",
                        "oflags": "fciq",
                        "trigger": "index",
                    },
                    "O6YDQ5-LOMWU-37YKEE": {
                        "refid": "None",
                        "userref": 36493663,
                        "status": "canceled",
                        "reason": "User requested",
                        "opentm": 1688148493.7708,
                        "closetm": 1688148610.0477,
                        "starttm": 0,
                        "expiretm": 0,
                        "descr": {
                            "pair": "XBTEUR",
                            "type": "buy",
                            "ordertype": "take-profit-limit",
                            "price": "27743.0",
                            "price2": "0",
                            "leverage": "none",
                            "order": "buy 0.00100000 XBTEUR @ limit 27743.0",
                            "close": "",
                        },
                        "vol": "0.00100000",
                        "vol_exec": "0.00000000",
                        "cost": "0.00000",
                        "fee": "0.00000",
                        "price": "0.00000",
                        "stopprice": "0.00000",
                        "limitprice": "0.00000",
                        "misc": "",
                        "oflags": "fciq",
                        "trigger": "index",
                    },
                },
                "count": 2,
            },
        }
        return super().get_factory_response(result)
