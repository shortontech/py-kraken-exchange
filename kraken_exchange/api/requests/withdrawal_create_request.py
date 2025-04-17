from decimal import Decimal
from typing import Union
from ..abstract.request import Request


class WithdrawalCreateRequest(Request):
    nonce: Union[
        Decimal, str, None, Request.Fields.DecimalField
    ] = Request.Fields.DecimalField(required=True)
    """Nonce used in construction of API-Sign header"""

    asset: Union[str, None, Request.Fields.CharField] = Request.Fields.CharField(
        required=True
    )
    """Asset being withdrawn"""

    key: Union[str, None, Request.Fields.CharField] = Request.Fields.CharField(
        required=True
    )
    """Withdrawal key name, as set up on your account"""

    address: Union[str, None, Request.Fields.CharField] = Request.Fields.CharField(
        required=False
    )
    """Optional, crypto address that can be used to confirm address matches key (will return Invalid withdrawal address error if different)"""

    amount: Union[str, None, Request.Fields.CharField] = Request.Fields.CharField(
        required=True
    )
    """Amount to be withdrawn"""

    max_fee: Union[str, None, Request.Fields.CharField] = Request.Fields.CharField(
        required=True
    )
    """Optional, if the processed withdrawal fee is higher than max_fee, withdrawal will fail with EFunding:Max fee exceeded"""

    @classmethod
    def is_child(cls) -> bool:
        return False

    def get_method(self) -> str:
        return "GET"

    def get_path(self) -> str:
        return "/private/Withdraw"

    def get_factory_response(self, response: dict | None = None) -> dict:
        result = {"error": [], "result": {"refid": "FTQcuak-V6Za8qrWnhzTx67yYHz8Tg"}}
        return super().get_factory_response(result)
