from typing import Union
from ..abstract.request import Request
from .order_batch_item_close_request import OrderBatchItemCloseRequest


class OrderAddBatchItemRequest(Request):
    userref: Union[str, Request.Fields.CharField, None] = Request.Fields.CharField(
        required=False, location="body"
    )
    ordertype: Union[str, Request.Fields.CharField, None] = Request.Fields.CharField(
        required=False, location="body"
    )
    type: Union[str, Request.Fields.CharField, None] = Request.Fields.CharField(
        required=False, location="body"
    )
    volume: Union[str, Request.Fields.CharField, None] = Request.Fields.CharField(
        required=False, location="body"
    )
    displayvol: Union[str, Request.Fields.CharField, None] = Request.Fields.CharField(
        required=False, location="body"
    )
    pair: Union[str, Request.Fields.CharField, None] = Request.Fields.CharField(
        required=False, location="body"
    )
    price: Union[str, Request.Fields.CharField, None] = Request.Fields.CharField(
        required=False, location="body"
    )
    price2 = Request.Fields.CharField(required=False, location="body")
    trigger: Union[str, Request.Fields.CharField, None] = Request.Fields.CharField(
        required=False, location="body"
    )
    reduce_only: Union[str, Request.Fields.CharField, None] = Request.Fields.CharField(
        required=False, location="body"
    )
    stptype: Union[str, Request.Fields.CharField, None] = Request.Fields.CharField(
        required=False, location="body"
    )
    oflags: Union[str, Request.Fields.CharField, None] = Request.Fields.CharField(
        required=False, location="body"
    )
    timeinforce: Union[str, Request.Fields.CharField, None] = Request.Fields.CharField(
        required=False, location="body"
    )
    starttm: Union[str, Request.Fields.CharField, None] = Request.Fields.CharField(
        required=False, location="body"
    )
    expiretm: Union[str, Request.Fields.CharField, None] = Request.Fields.CharField(
        required=False, location="body"
    )
    deadline: Union[str, Request.Fields.CharField, None] = Request.Fields.CharField(
        required=False, location="body"
    )
    validate: Union[str, Request.Fields.CharField, None] = Request.Fields.CharField(
        required=False, location="body"
    )
    close = Request.Fields.ChildModelField(OrderBatchItemCloseRequest, location="body")

    @classmethod
    def is_child(cls) -> bool:
        return True
