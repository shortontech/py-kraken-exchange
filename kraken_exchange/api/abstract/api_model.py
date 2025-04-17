from decimal import Decimal
from typing import Any, Union
from ..errors import (
    GetFactoryResponseNotImplemented,
    GetMethodNotImplemented,
    GetPathNotImplemented,
    InvalidValue,
    IsChildNotImplemented,
    RequestMethodUnknown,
)
from .api_client import ApiClient
from .api_model_base import ApiModelBase, HasToDict


class ApiModel(ApiModelBase):
    _is_request = True
    TYPE_HEADER = "HEADER"
    """Indicates whether this request is authenticated."""

    _structure_verified: bool = False

    def __init__(self, values: dict | None = None, **kwargs) -> None:
        self._initialized = False
        self._values: dict = {}
        if values and not isinstance(values, dict):
            message = (
                "values provided are of type {0} and not a dict from class {1}".format(
                    type(values).__name__, self.__class__.__name__
                )
            )
            raise InvalidValue(message)
        """Sets default values on this instance"""
        all_values: dict = (values if values else dict()) | kwargs

        self._original: dict = {}
        """Source data provided as values to the constructor or update function"""
        if len(all_values.keys()):
            self.update(all_values)
        else:
            object.__setattr__(self, "_values", dict())

    def set_defaults(self):
        pass

    def get_factory_response(self, response: dict | None = None) -> dict:
        self.set_defaults()

        if not response:
            raise GetFactoryResponseNotImplemented(
                "get_factory_response was not implemented!"
            )

        return response

    def get_original(self) -> dict:
        """Returns the original source object."""
        return self._original

    def update(self, values: dict):
        """(Re) initializes the dict that stores model properties and their values"""
        _values: dict = dict()
        self._original = values

        object.__setattr__(self, "_values", _values)
        for property, field in vars(self.__class__).items():
            if isinstance(field, ApiModelBase.Fields.ResponseField):
                alias = field.alias if field.alias is not None else property
                if alias in values:
                    _values[property] = field.check_value(values.get(alias))
                else:
                    _values[property] = field.check_value(field.get_default_value())

    def _to_dict(self) -> dict[str, Any]:
        """Converts the response model to a dict"""
        self.verify_structure()

        # get the ResponseField instances
        fields = self.get_all_fields()

        result: dict = dict()
        # When there's nothing to return, return nothing.
        if len(fields.keys()) == 0:
            return result

        # Handle each property
        for property, field in fields.items():
            # if it's not a ResponseField, ignore it.
            currVal = self._values.get(property, None)
            # If the value is an instance has a to_dict method,
            # call it.
            if isinstance(currVal, HasToDict):
                result[property] = currVal.__dict__
            elif isinstance(currVal, list):
                # For lists, we need to serialize any objects within
                # the list. That's too long to leave here.
                result[property] = self._list_to_dict(currVal)
            elif currVal is None and field.required and field.default is not None:
                result[property] = field.default
            elif currVal is not None and isinstance(currVal, Decimal):
                result[property] = str(currVal)
            elif currVal is not None and isinstance(currVal, bool):
                result[property] = str(currVal).lower()
            elif currVal is not None or field.required:
                result[property] = currVal

        return result

    def __setattr__(self, name: str, value: Any) -> None:
        """Validates properties when setting them."""
        if name.startswith("_"):
            super().__setattr__(name, value)
        else:
            found = False
            try:
                _values = super().__getattribute__("_values")

                try:
                    field: ApiModelBase.Fields.ResponseField = super().__getattribute__(
                        name
                    )

                    if issubclass(type(field), ApiModelBase.Fields.ResponseField):
                        if self._initialized:
                            field.validate(value)
                        _values[name] = value
                        found = True

                    if not found:
                        super().__setattr__(name, value)
                except AttributeError as e:
                    super().__setattr__(name, value)
            except AttributeError:
                super().__setattr__(name, value)

    def __getattribute__(self, name: str) -> Any:
        """For reading attributes"""
        if name == "__dict__":
            return self._to_dict()

        val = super().__getattribute__(name)

        if isinstance(val, ApiModelBase.Fields.ResponseField):
            _values = super().__getattribute__("_values")
            return _values.get(name, None)
        return val

    def __delattr__(self, name):
        if name in self._values:
            del self._values[name]

    def get_method(self):
        raise GetMethodNotImplemented(
            "{0}.get_method() was not implemented".format(self.__class__.__name__)
        )

    def _list_to_dict(self, items: list):
        """
        Convert each item in the list to something that
        can be used in json.
        """
        newList = list()
        for currVal in items:
            if isinstance(currVal, HasToDict):
                newList.append(currVal.__dict__)
            elif currVal is not None:
                newList.append(currVal)
        return newList

    def skip_structure_verification(self) -> bool:
        """For child classes, to allow skipping structure verification."""
        return False

    def verify_structure(self) -> bool:
        """Verify that the request / response is well structured."""
        # Verify that all classes have implemented is_child()
        if self.skip_structure_verification() or self._structure_verified:
            return True
        try:
            is_child = self.is_child()

            if is_child is not True and self._is_request:
                try:
                    self.get_method()
                except GetMethodNotImplemented:
                    format = "{0}.is_child is not true and {0}.get_method() is not implemented. "
                    "Unless the this is a child request, this method must be implemented."

                    message = format.format(self.__class__.__name__)
                    raise RequestMethodUnknown(message)
                # check the path too.
                try:
                    self.get_path()
                except GetPathNotImplemented:
                    format = "{0}.is_child is not true and {0}.get_path() is not implemented. "
                    "Unless the this is a child request, the get_path must be implemented."

                    message = format.format(self.__class__.__name__)
                    raise GetPathNotImplemented(message)
        except IsChildNotImplemented:
            message = "{0}.is_child is not implemented.".format(self.__class__.__name__)
            raise RequestMethodUnknown(message)
        self._structure_verified = True
        return True

    @classmethod
    def get_field(cls, key: str) -> ApiModelBase.Fields.ResponseField | None:
        """Gets the instance of ResponseField for a given key, or None"""
        value = getattr(cls, key)
        return value if isinstance(value, ApiModelBase.Fields.ResponseField) else None

    @classmethod
    def get_all_fields(cls) -> dict:
        """Retrieves all ResponseField instances on the class"""
        keys = filter(cls.get_field, dir(cls))
        ret = dict(map(lambda key: (key, cls.get_field(key)), keys))

        return ret

    def get_property_value(self, key: str):
        """Gets the current value for the property"""
        _values = super().__getattribute__("_values")
        currVal = self._values.get(_values)

        if isinstance(currVal, HasToDict):
            return currVal.__dict__
        elif isinstance(currVal, list):
            # For lists, we need to serialize any objects within
            # the list. That's too long to leave here.
            return self._list_to_dict(currVal)
        return currVal

    @classmethod
    def get_response_class(cls, values: dict) -> Any:
        """For defining a response class to use for responding."""
        return None

    def get_path(self) -> str | None:
        """For non-child request classes, returns the path part of the API request"""
        raise GetPathNotImplemented(
            "{0} does not implement get_path".format(self.__class__.__name__)
        )

    @classmethod
    def is_child(cls) -> bool:
        """Indicates whether the model is a child class, which is a ApiModel inside of another ApiModel"""
        raise IsChildNotImplemented(
            "{0}.is_child() not implemented".format(cls.__name__)
        )

    def get_properties_in(self, location: str) -> dict:
        """
        Returns a dict of properties that are in the specified location.
        """
        result: dict = dict()
        for property, field in vars(self.__class__).items():
            if isinstance(field, ApiModelBase.Fields.ResponseField):
                currVal = self._values.get(property, None)
                if currVal is not None:
                    if location == "body" and (
                        field.location == location or field.location is None
                    ):
                        result[property] = currVal
                    elif field.location == location:
                        result[property] = currVal
        return result

    def submit(
        self,
        use_mock: bool,
        nonce: str | Decimal | int,
        api_key: str,
        security_key: str,
    ) -> Union[dict, "ApiModel", "ApiModelBase"]:
        if isinstance(nonce, Decimal) or isinstance(nonce, int):
            nonce = str(nonce)

        """Submits as a request and returns either an API model or  """
        client: ApiClient = ApiClient()
        response: dict = client.submit(
            request=self,
            use_mock=use_mock,
            nonce=nonce,
            api_key=api_key,
            security_key=security_key,
        )

        if "result" in response and isinstance(response["result"], dict):
            response_dict: dict = response.get("result", {})
        else:
            response_dict = response

        response_class: Union[type["ApiModel"], None] = self.get_response_class(
            values=response_dict
        )

        if response_class:
            return response_class(values=response_dict)

        return response_dict
