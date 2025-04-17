from typing import List
import json

from requests import request
import requests


class NotImplemented(Exception):
    pass


class GetPathNotImplemented(Exception):
    pass


class NonceMissing(Exception):
    pass


class RequestFailedException(Exception):
    def __init__(
        self,
        response: requests.models.Response,
        method: str,
        path: str,
        post_data: dict,
        query: dict,
        headers: dict,
    ):
        super().__init__(self)
        self.response = response
        self.method = method
        self.path = path
        self.post_data = post_data
        self.query = query
        self.headers = headers


class InvalidValue(Exception):
    pass


class AuthenticationFailed(Exception):
    pass


class GetResponseNotImplemented(Exception):
    pass


class GetFactoryResponseNotImplemented(Exception):
    pass


class ToDictNotImplemented(Exception):
    pass


class RequestMethodUnknown(Exception):
    pass


class GetMethodNotImplemented(Exception):
    pass


class IsChildNotImplemented(Exception):
    pass


class InvalidToken(Exception):
    pass


# Kraken specific exceptions
class ApiExceptionBase(Exception):
    """Kraken specific error messages"""

    class Severities:
        SEVERITY_WARNING: str = "W"
        """Indicates that this exception is not an error, but a warning."""
        error: str = "E"
        """Indicates that this exception is not an error."""

    class Categories:
        general: str = "General"
        bm: str = "BM"
        auth: str = "Auth"
        api: str = "API"
        query: str = "Query"
        order: str = "Order"
        trade: str = "Trade"
        funding: str = "Funding"
        service = "Service"
        session: str = "Session"

    def __init__(
        self,
        severity: str | None = None,
        category: str | None = None,
        error_message: str | None = None,
        additional_text: str | None = None,
        exception_message: str | None = None,
    ):
        super().__init__(self, exception_message)
        self.severity: str | None = severity
        self.category: str | None = category
        self.error_message: str | None = error_message
        self.additional_text: str | None = additional_text

    @property
    def is_error(self) -> bool:
        return self.severity == self.Severities.error

    @classmethod
    def matches(cls, error_str: str) -> bool:
        """Checks the string to see if it matches."""
        error_arr = error_str[1::].split(":")
        severity: str = error_str[0]
        category: str = error_arr[0]
        error_message: str | None = (
            ":".join(error_arr[1::]) if len(error_arr) > 1 else None
        )
        instance = cls()
        return (
            severity == instance.severity
            and category == instance.category
            and error_message == instance.error_message
        )


class ApiException(ApiExceptionBase):
    KNOWN_EXCEPTIONS: List[type[ApiExceptionBase]] = list()
    """
    This list is filled at the bottom of this module, and contains all kraken specific errors.
    """

    @classmethod
    def get_exception_class(cls, error_str: str):
        for child_class in ApiException.KNOWN_EXCEPTIONS:
            if child_class.matches(error_str):
                return child_class

        error_arr = error_str[1::].split(":")

        class ApiErrorUnknownException(ApiException):
            """A completely unknown exception. Handle it anyway."""

            def __init__(self):
                nonlocal error_str
                self.severity = error_str[0]
                self.category = error_arr[0]
                self.additional_text = (
                    ":".join(error_arr[1::]) if len(error_arr) > 1 else None
                )
                self.category = error_arr[0]
                self.error_message = f"Unknown exception: {error_str}"

        return ApiErrorUnknownException


class ApiInvalidArgumentsException(ApiException):
    def __init__(self):
        super().__init__(
            severity=self.Severities.error,
            category=self.Categories.general,
            error_message="Invalid arguments",
            additional_text=None,
            exception_message="The request payload is malformed, incorrect or ambiguous",
        )


class InvalidIndexException(ApiException):
    def __init__(self):
        super().__init__(
            severity=self.Severities.error,
            category=self.Categories.general,
            error_message="Index unavailable",
            additional_text=None,
            exception_message="Index pricing is unavailable for stop/profit orders on this pair",
        )


class InvalidPairException(ApiException):
    def __init__(self):
        super().__init__(
            severity=self.Severities.error,
            category=self.Categories.general,
            error_message="Invalid arguments",
            additional_text="Index unavailable",
            exception_message="Index pricing is unavailable for stop/profit orders on this pair",
        )


class ServiceUnavailableException(ApiException):
    """The matching engine or API is offline"""

    def __init__(self):
        super().__init__(
            severity=self.Severities.error,
            category=self.Categories.service,
            error_message="Unavailable",
            additional_text=None,
            exception_message="The matching engine or API is offline",
        )


class CancelOnlyModeException(ApiException):
    """Direct from kraken. Request can't be made at this time (See SystemStatus endpoint)"""

    def __init__(self):
        super().__init__(
            severity=self.Severities.error,
            category=self.Categories.service,
            error_message="Market in cancel_only mode",
            additional_text=None,
            exception_message="Request can't be made at this time (See SystemStatus endpoint)",
        )


class PostOnlyModeException(ApiException):
    def __init__(self):
        super().__init__(
            severity=self.Severities.error,
            category=self.Categories.service,
            error_message="Market in post_only mode",
            additional_text=None,
            exception_message="Request can't be made at this time (See SystemStatus endpoint)",
        )


class DeadlineElapsedException(ApiException):
    def __init__(self):
        super().__init__(
            severity=self.Severities.error,
            category=self.Categories.service,
            error_message="Deadline elapsed",
            additional_text=None,
            exception_message="The request timed out according to the default or specified deadline",
        )


class InvalidKeyException(ApiException):
    def __init__(self):
        super().__init__(
            severity=self.Severities.error,
            category=self.Categories.api,
            error_message="Invalid key",
            additional_text=None,
            exception_message="An invalid API-Key header was supplied (see Authentication section)",
        )


class InvalidSignatureException(ApiException):
    def __init__(self):
        super().__init__(
            severity=self.Severities.error,
            category=self.Categories.api,
            error_message="Invalid signature",
            additional_text=None,
            exception_message="An invalid API-Sign header was supplied (see Authentication section)",
        )


class InvalidNonceException(ApiException):
    def __init__(self):
        super().__init__(
            severity=self.Severities.error,
            category=self.Categories.api,
            error_message="Invalid nonce",
            additional_text=None,
            exception_message="An invalid nonce was supplied",
        )


class PermissionException(ApiException):
    def __init__(self):
        super().__init__(
            severity=self.Severities.error,
            category=self.Categories.general,
            error_message="Permission denied",
            additional_text=None,
            exception_message="API key doesn't have permission to make this request",
        )


class IneligibleMarginTradingException(ApiException):
    def __init__(self):
        super().__init__(
            severity=self.Severities.error,
            category=self.Categories.order,
            error_message="Cannot open position",
            additional_text=None,
            exception_message="User/tier is ineligible for margin trading",
        )


class MarginAllowanceExceededException(ApiException):
    def __init__(self):
        super().__init__(
            severity=self.Severities.error,
            category=self.Categories.order,
            error_message="Margin allowance exceeded",
            additional_text=None,
            exception_message="User has exceeded their margin allowance",
        )


class InsufficientEquityException(ApiException):
    def __init__(self):
        super().__init__(
            severity=self.Severities.error,
            category=self.Categories.order,
            error_message="Margin level too low",
            additional_text=None,
            exception_message="Client has insufficient equity or collateral",
        )


class ExceedsMaximumPositionException(ApiException):
    def __init__(self):
        super().__init__(
            severity=self.Severities.error,
            category=self.Categories.order,
            error_message="Margin position size exceeded",
            additional_text=None,
            exception_message="Client would exceed the maximum position size for this pair",
        )


class ExchangeMarginException(ApiException):
    def __init__(self):
        super().__init__(
            severity=self.Severities.error,
            category=self.Categories.order,
            error_message="Insufficient margin",
            additional_text=None,
            exception_message="Exchange does not have available funds for this margin trade",
        )


class AccountBalanceLowException(ApiException):
    def __init__(self):
        super().__init__(
            severity=self.Severities.error,
            category=self.Categories.order,
            error_message="Insufficient funds",
            additional_text=None,
            exception_message="Client does not have the necessary funds",
        )


class OrderMinumumException(ApiException):
    def __init__(self):
        super().__init__(
            severity=self.Severities.error,
            category=self.Categories.order,
            error_message="Order minimum not met",
            additional_text=None,
            exception_message="Order size does not meet order minimum",
        )


class CostMinimumException(ApiException):
    def __init__(self):
        super().__init__(
            severity=self.Severities.error,
            category=self.Categories.order,
            error_message="Cost minimum not met",
            additional_text=None,
            exception_message="Cost (price * volume) does not meet costmin (See AssetPairs endpoint)",
        )


class PriceTickSizeDissonanceException(ApiException):
    def __init__(self):
        super().__init__(
            severity=self.Severities.error,
            category=self.Categories.order,
            error_message="Tick size check failed",
            additional_text=None,
            exception_message="Price submitted is not a valid multiple of the pair's tick_size (See AssetPairs endpoint)",
        )


class OrderLimitException(ApiException):
    def __init__(self):
        super().__init__(
            severity=self.Severities.error,
            category=self.Categories.order,
            error_message="Orders limit exceeded",
            additional_text=None,
            exception_message="(See Rate Limits section)",
        )


class RateLimitExceededException(ApiException):
    def __init__(self):
        super().__init__(
            severity=self.Severities.error,
            category=self.Categories.api,
            error_message="Rate limit exceeded",
            additional_text=None,
            exception_message="(See Rate Limits section)",
        )


class DomainRateLimitExceededException(ApiException):
    def __init__(self):
        super().__init__(
            severity=self.Severities.error,
            category=self.Categories.order,
            error_message="Domain rate limit exceeded",
            additional_text=None,
            exception_message="(See Rate Limits section)",
        )


class PositionsLimitExceededException(ApiException):
    def __init__(self):
        super().__init__(
            severity=self.Severities.error,
            category=self.Categories.order,
            error_message="Positions limit exceeded",
            additional_text=None,
            exception_message="",
        )


class PositionUnknownException(ApiException):
    def __init__(self):
        super().__init__(
            severity=self.Severities.error,
            category=self.Categories.order,
            error_message="Unknown position",
            additional_text=None,
            exception_message="",
        )


class CalLimitExceededException(ApiException):
    def __init__(self):
        super().__init__(
            severity=self.Severities.error,
            category=self.Categories.bm,
            error_message="limit exceeded",
            additional_text="CAL",
            exception_message="Exceeded Canadian Acquisition Limits (CAL)",
        )


class WithdrawalFeeException(ApiException):
    def __init__(self):
        super().__init__(
            severity=self.Severities.error,
            category=self.Categories.funding,
            error_message="Max fee exceeded",
            additional_text=None,
            exception_message="Processed fee exceeds max_fee set in Withdraw request",
        )


class AssetPairUnknownException(ApiException):
    """
    Invalid session errors are returned via the WebSocket API, when an attempt is made to subscribe to
    an authenticated (private) feed using an authentication token that is no longer valid (has already
    expired, for example)."""

    def __init__(self):
        super().__init__(
            severity=self.Severities.error,
            category=self.Categories.query,
            error_message="Unknown asset pair",
            additional_text=None,
            exception_message="Processed fee exceeds max_fee set in Withdraw request",
        )


class SessionInvalidException(ApiException):
    """
    Invalid session errors are returned via the WebSocket API, when an attempt is made to subscribe to
    an authenticated (private) feed using an authentication token that is no longer valid (has already
    expired, for example).
    """

    def __init__(self):
        super().__init__(
            severity=self.Severities.error,
            category=self.Categories.session,
            error_message="Invalid session",
            additional_text=None,
            exception_message="The authentication token is no longer valid.",
        )


class EndpointInvalidException(ApiException):
    """
    This error is returned when the endpoint being called is not a valid endpoint.

    """

    def __init__(self):
        super().__init__(
            severity=self.Severities.error,
            category=self.Categories.general,
            error_message="Unknown Method",
            additional_text=None,
            exception_message="Invalid endpoint",
        )


class BadRequestException(ApiException):
    """
    A bad request error indicates that there is something incorrect about the underlying HTTP request (not the subsequent API request),
    such as mismatched URLs between REST/WebSocket, or not including the HTTP POST data correctly:

    """

    def __init__(self):
        super().__init__(
            severity=self.Severities.error,
            category=self.Categories.api,
            error_message="Bad request",
            additional_text=None,
            exception_message="There is something incorrect about the underlying HTTP request,"
            " such as mismatched URLs between REST/WebSocket, or not including the HTTP POST data correctly",
        )


class LockoutException(ApiException):
    """
    Temporary lockout error messages can occur if you had too many failed API calls or too many invalid nonce errors
    in a short period of time or invalid signatures. Even though these calls return an error, that error still counts
    against your API limits and may result in a temporary lockout.

    Temporary lockouts last approximately 15 minutes. After receiving the temporary lock out error, please wait 15
    minutes before sending any new API requests. If you are triggering several invalid nonce errors, please increase
    the nonce window as this can help reduce the frequency that these errors will occur. Please try to reduce the
    frequency of your private API calls also.

    """

    def __init__(self):
        super().__init__(
            severity=self.Severities.error,
            category=self.Categories.general,
            error_message="Temporary lockout",
            additional_text=None,
            exception_message="Temporary lockout: too many malformed requests, incorrect nonces, or too many requests",
        )


class PositionOpposingException(ApiException):
    """
    On Kraken you cannot open a long and short position for the same pair.

    If wishing to open a long and short position for the same currency, please choose different trading pairs
    with the same currency as the base or quote currency. Ex: short XBT/USD, long XBT/EUR.

    """

    def __init__(self):
        super().__init__(
            severity=self.Severities.error,
            category=self.Categories.order,
            error_message="Cannot open opposing position",
            additional_text=None,
            exception_message="On Kraken you cannot open a long and short position for the same pair.",
        )


class OrderNotEditableException(ApiException):
    """
    On Kraken you cannot open a long and short position for the same pair.

    If wishing to open a long and short position for the same currency, please choose different trading pairs
    with the same currency as the base or quote currency. Ex: short XBT/USD, long XBT/EUR.

    """

    def __init__(self):
        super().__init__(
            severity=self.Severities.error,
            category=self.Categories.order,
            error_message="Order not editable",
            additional_text=None,
            exception_message="An attempt was made to edit an existing (open) order but the modifications "
            "could not be completed successfully. Possible reasons include insufficient funds for the new "
            "order, some partial fill scenarios, and some leveraged orders.",
        )


class LeavesQualtityInvalidException(ApiException):
    """
    The new volume is less than the already executed/filled volume.
    """

    def __init__(self):
        super().__init__(
            severity=self.Severities.error,
            category=self.Categories.order,
            error_message="Not enough leaves qty",
            additional_text=None,
            exception_message="The new volume is less than the already executed/filled volume.",
        )


class VolumeMinimumNotMetException(ApiException):
    """
    The display volume has not met the minimum order volume.
    """

    def __init__(self):
        super().__init__(
            severity=self.Severities.error,
            category=self.Categories.general,
            error_message="Invalid arguments",
            additional_text="display volume minimum not met",
            exception_message="The display volume has not met the minimum order volume.",
        )


class VolumeMaximumExceededException(ApiException):
    """
    The display volume must be less than the volume of the order.
    """

    def __init__(self):
        super().__init__(
            severity=self.Severities.error,
            category=self.Categories.general,
            error_message="Invalid arguments",
            additional_text="display-volume",
            exception_message="The display volume must be less than the volume of the order.",
        )


class IcebergOrderIncompatibleException(ApiException):
    """
    Iceberg orders are not compatible with any other order types besides a limit order.
    """

    def __init__(self):
        super().__init__(
            severity=self.Severities.error,
            category=self.Categories.general,
            error_message="Invalid arguments",
            additional_text="iceberg:ordertype",
            exception_message="Iceberg orders are not compatible with any other order types besides a limit order.",
        )


class AddressLimitException(ApiException):
    """
    Each crypto currency has a maximum of 5 new (unused) deposit addresses, after which any attempt to create a 6th new address will return an error.
    """

    def __init__(self):
        super().__init__(
            severity=self.Severities.error,
            category=self.Categories.funding,
            error_message="Too many addresses",
            additional_text=None,
            exception_message="Each crypto currency has a maximum of 5 new (unused) deposit addresses, "
            "after which any attempt to create a 6th new address will return an error.",
        )


class FundingMethodMissingException(ApiException):
    """
    This error is returned whenever the funding endpoints are called with an invalid or missing "method" parameter.
    """

    def __init__(self):
        super().__init__(
            severity=self.Severities.error,
            category=self.Categories.funding,
            error_message="No funding method",
            additional_text=None,
            exception_message='This error is returned whenever the funding endpoints are called with an invalid or missing "method" parameter.',
        )


class WithdrawalKeyUnknownException(ApiException):
    """
    This error is returned whenever the funding endpoints are called with an invalid or missing "method" parameter.
    """

    def __init__(self):
        super().__init__(
            severity=self.Severities.error,
            category=self.Categories.funding,
            error_message="Unknown withdraw key",
            additional_text=None,
            exception_message='The "key" input parameter does not correspond to the address description set within account management (via the Funding -> Withdraw).',
        )


class WithdrawalAmountMinimumException(ApiException):
    """
    The minimum withdrawal amounts by currency varies and any attempted withdrawal below the minimum would result in this error.
    """

    def __init__(self):
        super().__init__(
            severity=self.Severities.error,
            category=self.Categories.funding,
            error_message="Invalid amount",
            additional_text=None,
            exception_message="The minimum withdrawal amounts by currency varies and any attempted withdrawal "
            "below the minimum would result in this error.",
        )


class FundingGeneralException(ApiException):
    """
    This is a generic error indicating that a funding request could not be completed
    (for example, clients from certain locations attempting to make on chain staking
    requests would cause this error).
    """

    def __init__(self):
        super().__init__(
            severity=self.Severities.error,
            category=self.Categories.funding,
            error_message="Failed",
            additional_text=None,
            exception_message="This is a generic error indicating that a funding request could not be completed "
            "(for example, clients from certain locations attempting to make on chain staking requests would cause this error).",
        )


class FundingUnavailableException(ApiException):
    """
    The service errors you are experiencing should only be temporary.
    You may wish to resubmit your requests if they have failed.

    We will be monitoring the issues and will update our page:

    https://status.kraken.com/
    """

    def __init__(self):
        super().__init__(
            severity=self.Severities.error,
            category=self.Categories.funding,
            error_message="Failed",
            additional_text=None,
            exception_message="The service errors you are experiencing should only be temporary. "
            "You may wish to resubmit your requests if they have failed. "
            "We will be monitoring the issues and will update our page: \nhttps://status.kraken.com/",
        )


class FundingBusyException(ApiException):
    """
    The service errors you are experiencing should only be temporary.
    You may wish to resubmit your requests if they have failed.

    We will be monitoring the issues and will update our page:

    https://status.kraken.com/
    """

    def __init__(self):
        super().__init__(
            severity=self.Severities.error,
            category=self.Categories.service,
            error_message="Busy",
            additional_text=None,
            exception_message="The service errors you are experiencing should only be temporary. "
            "You may wish to resubmit your requests if they have failed. "
            "We will be monitoring the issues and will update our page: "
            "https://status.kraken.com/",
        )


class ServiceErrorException(ApiException):
    """
    The service errors you are experiencing should only be temporary.
    You may wish to resubmit your requests if they have failed.

    We will be monitoring the issues and will update our page:

    https://status.kraken.com/
    """

    def __init__(self):
        super().__init__(
            severity=self.Severities.error,
            category=self.Categories.service,
            error_message="Internal error",
            additional_text=None,
            exception_message="The service errors you are experiencing should only be temporary. "
            "You may wish to resubmit your requests if they have failed. "
            "We will be monitoring the issues and will update our page: "
            "https://status.kraken.com/",
        )


class TradeLockedException(ApiException):
    """
    This issue has to do with the security of your account which may have been
    compromised. Please change your password and Two-Factor Authentication
    and contact our Support Center.
    """

    def __init__(self):
        super().__init__(
            severity=self.Severities.error,
            category=self.Categories.trade,
            error_message="Locked",
            additional_text=None,
            exception_message="This issue has to do with the security of your account which may "
            "have been compromised. Please change your password and Two-Factor Authentication "
            "and contact our Support Center.",
        )


class ApiFeatureDisabledException(ApiException):
    """
    This issue has to do with the security of your account which may have been
    compromised. Please change your password and Two-Factor Authentication
    and contact our Support Center.
    """

    def __init__(self):
        super().__init__(
            severity=self.Severities.error,
            category=self.Categories.api,
            error_message="Feature disabled",
            additional_text=None,
            exception_message="This error occurs when a flag or input parameter is disabled temporary or permanently. "
            "The error should come from one of the inputs passed, please contact our support sending a log with the "
            "complete informations used for the call that generated the error.",
        )


class BeneficiaryUnknownException(ApiException):
    """
    The requested withdrawal could not be completed, because the destination address is missing the
    required beneficiary/recipient information (note that this currently only applies to select withdrawals
    from Canadian accounts).
    """

    def __init__(self):
        super().__init__(
            severity=self.Severities.error,
            category=self.Categories.api,
            error_message="Feature disabled",
            additional_text=None,
            exception_message="The requested withdrawal could not be completed, because the "
            "destination address is missing the required beneficiary/recipient information "
            "(note that this currently only applies to select withdrawals from Canadian accounts).",
        )


ApiException.KNOWN_EXCEPTIONS = [
    ApiInvalidArgumentsException,
    InvalidIndexException,
    InvalidPairException,
    ServiceUnavailableException,
    CancelOnlyModeException,
    PostOnlyModeException,
    DeadlineElapsedException,
    InvalidKeyException,
    InvalidSignatureException,
    InvalidNonceException,
    PermissionException,
    IneligibleMarginTradingException,
    MarginAllowanceExceededException,
    InsufficientEquityException,
    ExceedsMaximumPositionException,
    ExchangeMarginException,
    AccountBalanceLowException,
    OrderMinumumException,
    CostMinimumException,
    PriceTickSizeDissonanceException,
    OrderLimitException,
    RateLimitExceededException,
    DomainRateLimitExceededException,
    PositionsLimitExceededException,
    PositionUnknownException,
    CalLimitExceededException,
    WithdrawalFeeException,
    AssetPairUnknownException,
    SessionInvalidException,
    EndpointInvalidException,
    BadRequestException,
    LockoutException,
    PositionOpposingException,
    OrderNotEditableException,
    LeavesQualtityInvalidException,
    VolumeMinimumNotMetException,
    VolumeMaximumExceededException,
    IcebergOrderIncompatibleException,
    AddressLimitException,
    FundingMethodMissingException,
    WithdrawalKeyUnknownException,
    WithdrawalAmountMinimumException,
    FundingGeneralException,
    FundingUnavailableException,
    FundingBusyException,
    ServiceErrorException,
    TradeLockedException,
    ApiFeatureDisabledException,
    BeneficiaryUnknownException,
]
