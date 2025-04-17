from typing import Union
from ..abstract.request import Request


class OrderEditRequest(Request):
    transaction_id: Union[
        str, Request.Fields.CharField, None
    ] = Request.Fields.CharField(required=False, alias="txid")

    @classmethod
    def is_child(cls) -> bool:
        return False

    def get_method(self) -> str:
        return "POST"

    def get_path(self) -> str:
        return "/0/private/EditOrder"
