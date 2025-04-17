from typing import Union
from ..abstract.request import Request


class OrderCancelRequest(Request):
    method = "POST"
    transaction_id: Union[
        str, Request.Fields.CharField, None
    ] = Request.Fields.CharField(required=False, alias="txid")

    @classmethod
    def is_child(cls) -> bool:
        return False

    @classmethod
    def get_method(self) -> str:
        return "POST"

    def get_path(self) -> str:
        return "/0/private/CancelOrder"
