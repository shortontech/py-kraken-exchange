from typing import Union
from ..abstract.request import Request


class DepositMethodListRequest(Request):
    txid: Union[str, Request.Fields.CharField, None] = Request.Fields.CharField(
        required=False, location="body"
    )

    def get_path(self):
        return "/0/private/DepositMethods"

    @classmethod
    def is_child(cls) -> bool:
        return False

    @classmethod
    def get_method(self) -> str:
        return "GET"
