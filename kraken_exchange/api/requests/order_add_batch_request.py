from typing import List, overload
from ..abstract.request import Request
from .order_add_batch_item_request import OrderAddBatchItemRequest


class OrderAddBatchRequest(Request):
    def __init__(self, items: List[OrderAddBatchItemRequest] | None = None):
        super().__init__()
        self.items: List[OrderAddBatchItemRequest] = items if items else list()

    @classmethod
    def is_child(cls) -> bool:
        return False

    @classmethod
    def get_method(self) -> str:
        return "POST"

    def get_path(self) -> str:
        return "/0/private/AddOrderBatch"
