from decimal import Decimal
from datetime import datetime
from typing import Any, Callable, List, Union
from ..errors import InvalidValue


class HasToDict:
    pass


class ApiModelBase(HasToDict):
    _is_request = True
    TYPE_HEADER = "HEADER"
    AUTHENTICATE = True
    _structure_verified: bool = False
    """Indicates whether this request is authenticated."""

    class Fields:
        TYPE_PATH = "path"
        TYPE_JSON = "JSON"

        class ResponseField:
            def __init__(
                self,
                location: str | None = None,
                alias: str | None = None,
                required: bool | None = None,
                default: Any = None,
            ) -> None:
                self.required = required if required is not None else required
                self.location = location
                self.alias: str | None = alias
                self.default = default

            def valid(self, val: Any) -> bool:
                """Indicates if a value is valid"""
                return not self.required or val is not None

            def check_value(self, value: Any):
                """In case the value needs to be processed before being set."""
                return value

            def get_default_value(self) -> Any:
                """Returns the default value, which is by default, None."""

                if self.default:
                    return self.default

                val: None = None
                return val

            def validate(self, val: Any):
                """Checks the value to see if it's valid."""
                if self.required and val is None:
                    raise InvalidValue("Invalud value {0}".format(str(val)))

        class CharField(ResponseField):
            def __init__(
                self,
                values: List[str] | None = None,
                location: str | None = None,
                alias: str | None = None,
                required: bool | None = None,
                default: Any | None = None,
            ) -> None:
                if default is not None and not isinstance(default, str):
                    default = str(default)

                super().__init__(
                    location=location, required=required, alias=alias, default=default
                )
                self.values = values

            def check_value(self, value: Any):
                if (
                    self.values is not None
                    and (value not in self.values)
                    or (value is None and self.required)
                ):
                    raise InvalidValue(
                        "Invalid value {0} for {1}".format(
                            str(value), type(self).__name__
                        )
                    )
                return super().check_value(value)

            pass

        class DecimalField(ResponseField):
            def __init__(
                self,
                min: int | Decimal | None = None,
                max: int | Decimal | None = None,
                location: str | None = None,
                alias: str | None = None,
                required: bool | None = None,
                default: Decimal | str | None = None,
            ) -> None:
                super().__init__(
                    location=location, required=required, alias=alias, default=default
                )
                if min is not None:
                    self.min = Decimal(str(min))

                if max is not None:
                    self.max = Decimal(str(max))

            def check_value(
                self, value: int | Decimal | float | str | datetime | None
            ) -> Decimal | None:
                """This value needs to be processed before being set."""
                valid_types = [int, Decimal, float, str, datetime]
                is_valid = (
                    isinstance(value, int)
                    or isinstance(value, Decimal)
                    or isinstance(value, float)
                    or isinstance(value, str)
                    or isinstance(value, datetime)
                    or (not self.required and value is None)
                )

                if isinstance(value, datetime):
                    value = Decimal(str(datetime.timestamp(value)))
                elif (
                    isinstance(value, str)
                    or isinstance(value, float)
                    or isinstance(value, int)
                ):
                    value = Decimal(value)

                # Check minimum and maximum values
                if (
                    is_valid
                    and self.min is not None
                    and value is not None
                    and value < self.min
                ):
                    is_valid = False
                elif (
                    is_valid
                    and self.max is not None
                    and value is not None
                    and value > self.max
                ):
                    is_valid = False

                if isinstance(value, datetime):
                    value = Decimal(str(datetime.timestamp(value)))

                if not is_valid:
                    raise Exception(
                        "Invalid value {0} for {1}".format(
                            str(value), type(self).__name__
                        )
                    )

                return value

        class UuidField(ResponseField):
            pass

        class DateField(ResponseField):
            pass

        class BoolField(ResponseField):
            pass

        class DateTimeField(ResponseField):
            pass

        class FileField(ResponseField):
            pass

        class ListField(ResponseField):
            def __init__(
                self,
                related: type,
                location: str | None = None,
                default: Any = None,
                alias: str | None = None,
                required: bool | None = None,
            ) -> None:
                super().__init__(
                    location=location, required=required, alias=alias, default=default
                )
                self.related = related

            def get_default_value(self) -> Any:
                """Initializes an empty list"""
                val: list = list()
                return val

        class ChildModelField(ResponseField, HasToDict):
            def __init__(
                self,
                related: type,
                location: str | None = None,
                alias: str | None = None,
                default: Any = None,
                required: bool | None = None,
            ) -> None:
                super().__init__(
                    location=location, required=required, alias=alias, default=default
                )
                self.related = related

            def get_default_value(self) -> Any:
                val = self.related()
                return val

            def check_value(self, value: Any):
                """This value needs to be processed before being set."""
                if value is None or isinstance(value, self.related):
                    return value

                return self.related(values=value)

    def get_original(self) -> dict:
        """Returns the original source object."""
        return {}

    def update(self, values: dict):
        """(Re) initializes the dict that stores model properties and their values"""
        pass

    def get_method(self):
        pass

    def _list_to_dict(self, items: list):
        """
        Convert each item in the list to something that
        can be used in json.
        """
        pass

    def skip_structure_verification(self) -> bool:
        """For child classes, to allow skipping structure verification."""
        return False

    def verify_structure(self) -> bool:
        """Verify that the request / response is well structured."""
        # Verify that all classes have implemented is_child()
        return True

    def get_factory_response(self, response: dict | None = None) -> dict:
        return {}

    @classmethod
    def get_field(cls, key: str) -> Fields.ResponseField | None:
        """Gets the instance of ResponseField for a given key, or None"""
        value = getattr(cls, key)
        return value if isinstance(value, cls.Fields.ResponseField) else None

    @classmethod
    def get_all_fields(cls) -> dict:
        """Retrieves all ResponseField instances on the class"""
        return {}

    def get_property_value(self, key: str):
        """Gets the current value for the property"""
        pass

    @classmethod
    def get_response_class(cls, values: dict) -> Any:
        """For defining a response class to use for responding."""
        pass

    def get_path(self) -> str | None:
        """For non-child request classes, returns the path part of the API request"""
        pass

    @classmethod
    def is_child(cls) -> bool:
        """Indicates whether the model is a child class, which is a ApiModel inside of another ApiModel"""
        raise Exception("Not implemented here")

    def get_properties_in(self, location: str) -> dict:
        """
        Returns a dict of properties that are in the specified location.
        """
        return {}

    def submit(
        self,
        use_mock: bool,
        nonce: str | Decimal | int,
        api_key: str,
        security_key: str,
    ) -> Union[dict, "ApiModelBase"]:
        """Submits as a request and returns either an API model or"""
        raise Exception("submit on ApiModelBase is not implemented")
