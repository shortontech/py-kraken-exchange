from typing import Union
from ..abstract.request import Request


class OrderBatchItemCloseRequest(Request):
    order_type: Union[str, Request.Fields.CharField, None] = Request.Fields.CharField(
        required=False, alias="ordertype"
    )
    price: Union[str, Request.Fields.CharField, None] = Request.Fields.CharField(
        required=False
    )

    @classmethod
    def is_child(cls) -> bool:
        return True
