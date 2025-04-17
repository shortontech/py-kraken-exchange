import base64
import hashlib
import hmac
import urllib.parse
import requests
import simplejson as json
from decimal import Decimal
from json import JSONDecodeError
from typing import Callable, List, Protocol, Union
from ..errors import ApiException, RequestFailedException
from .api_model_base import ApiModelBase


class MockFactoryBase:
    def __init__(self):
        pass


class MockFactoryResponse(requests.models.Response, MockFactoryBase):
    def __init__(self, request: ApiModelBase):
        super(MockFactoryBase, self).__init__()
        self._mock_json: dict = request.get_factory_response()
        self._mock_content = json.dumps(self._mock_json)

    @property
    def content(self):
        return self._mock_content.encode()

    @property
    def text(self):
        return self._mock_content

    @property
    def status_code(self):
        return 200

    def json(self):
        return self._mock_json


class PostRequestHook(Protocol):
    def __call__(
        self,
        response: Union["MockFactoryResponse", requests.models.Response],
        path: str,
        post_data: dict,
        query: dict,
        headers: dict,
        files: Union[list, None],
        is_authenticated,
    ) -> float:
        pass


class PreRequestHook(Protocol):
    def __call__(
        self,
        path: str,
        post_data: dict,
        query: dict,
        headers: dict,
        files: Union[list, None],
        is_authenticated,
    ) -> float:
        pass


class ApiClient:

    BASE_URL: str = "https://api.kraken.com"

    _pre_request_hooks: List[PreRequestHook] = list()
    """Hooks added via add_post_request_hook(hook)"""

    _post_request_hooks: List[PostRequestHook] = list()
    """Hooks added via add_pre_request_hooks(hook)"""

    logged_in = False

    @classmethod
    def check_response(
        cls,
        response: requests.models.Response,
        method,
        path,
        post_data=None,
        query=None,
        headers=None,
    ):
        debug_dict: dict = {
            "path": path,
            "method": method,
            "query": query,
            "post_data": post_data,
            "headers": headers,
            "response_text": response.text,
            "response": None,
        }

        try:
            debug_dict["response"] = response.json()
        finally:
            print(f"Debug data for response to {path} ({response.status_code})")
            print(json.dumps(debug_dict, indent=4))

        """Checks the response to see if there's an issue."""
        # Use simplejson's loads method with Decimal parsing
        resp_dict = json.loads(response.text, use_decimal=True)
        if "error" in resp_dict:
            for error in resp_dict["error"]:
                exception_class = ApiException.get_exception_class(error)
                raise exception_class()

        if response.status_code in [200, 201, 202, 301]:
            try:
                # As simplejson is used, there's no need to decode again
                response_dict = resp_dict
                if "response" in response_dict and isinstance(
                    response_dict["response"], dict
                ):
                    return response_dict["response"]
                else:
                    return response_dict

            except JSONDecodeError:
                return response.text

        raise RequestFailedException(
            response=response,
            method=method,
            path=path,
            post_data=post_data,
            query=query,
            headers=headers,
        )

    @classmethod
    def get_url(cls, path: str, query: dict | None = None):
        """Helper function for creating a URL from the query"""
        base_url = cls.BASE_URL
        url = base_url + path

        if query and isinstance(query, dict) and len(query.keys()) > 0:
            parts = []
            for key, value in query.items():
                if value is None:
                    value = ""
                elif isinstance(value, bool) and value is True:
                    value = "true"
                elif isinstance(value, bool) and value is False:
                    value = "false"
                elif not isinstance(value, str):
                    value = str(value)
                parts.append(
                    urllib.parse.quote(key.encode())
                    + "="
                    + urllib.parse.quote(value.encode())
                )
            query_string = "&".join(parts)
            url += f"?{query_string}"
            parts

        return url

    @classmethod
    def add_pre_request_hook(cls, hook: PreRequestHook):
        """Adds a handler for the post request hook.

        The hook will be called with the following code:

        hook(
            path,
            post_data,
            query,
            headers,
            files,
            authenticated
        )
        """
        cls._pre_request_hooks.append(hook)

    @classmethod
    def add_post_request_hook(cls, hook: PostRequestHook):
        """Adds a handler for the post request hook.

        The hook will be called with the following code:

        hook(
            response,
            path,
            post_data,
            query,
            headers,
            files,
            authenticated
        )
        """
        cls._post_request_hooks.append(hook)

    @classmethod
    def get_kraken_signature(
        cls, security_key: str, path: str, nonce: str | Decimal, data: dict
    ):
        # Helper function to add padding if necessary
        def decode_base64(data):
            missing_padding = len(data) % 4
            if missing_padding:
                data += "=" * (4 - missing_padding)
            return base64.b64decode(data)

        postdata = urllib.parse.urlencode(data)
        encoded = (str(nonce) + postdata).encode()
        message = path.encode() + hashlib.sha256(encoded).digest()

        # Check if SECURITY_KEY is set
        if security_key is None:
            raise ValueError("SECURITY_KEY is not set.")

        # Use the helper function to decode SECURITY_KEY
        decoded_security_key = decode_base64(security_key)
        mac = hmac.new(decoded_security_key, message, hashlib.sha512)
        sigdigest = base64.b64encode(mac.digest())
        return sigdigest.decode()

    @classmethod
    def submit(
        cls,
        request: ApiModelBase,
        nonce: str,
        api_key: str,
        security_key: str,
        use_mock: bool,
    ) -> dict:
        # verify all of the args
        if not isinstance(request, ApiModelBase):
            raise ValueError("request must be an instance of ApiModelBase | ApiModel")

        if not isinstance(use_mock, bool):
            raise ValueError("use_mock must be a boolean")

        if not isinstance(nonce, str):
            raise ValueError("nonce must be a string")

        if not isinstance(api_key, str):
            raise ValueError("api_key must be a string")

        if not isinstance(security_key, str):
            raise ValueError("security_key must be a string")

        if len(security_key) % 4 != 0:
            raise ValueError(
                "security_key must be a multiple of 4 in length to be decoded from base64"
            )

        path = request.get_path()
        method = request.get_method()
        query = request.get_properties_in("query")
        post_data = request.get_properties_in("body")
        files = request.get_properties_in("files")
        headers = request.get_properties_in("headers")
        files_list: list = [file for file in files]

        if path is None:
            raise ValueError(
                "The request's path is None. This is not allowed. The request must have a path."
            )

        url = cls.get_url(path, query)

        if "nonce" not in post_data:
            post_data["nonce"] = nonce

        if headers is None:
            headers = {}

        header_keys = list(map(lambda k: k.lower(), headers.keys()))

        for hook in cls._pre_request_hooks:
            hook(path, post_data, query, headers, files_list, request.AUTHENTICATE)

        if request.AUTHENTICATE and "API-Key" not in header_keys:
            if api_key is None:
                raise Exception("API Key is required for this request.")
            headers["API-Key"] = api_key
            headers["API-Sign"] = cls.get_kraken_signature(
                security_key, path, nonce, post_data
            )
        response: Union["MockFactoryResponse", requests.models.Response, None] = None
        if use_mock:
            print("Using mock factory responses; no requests will be made.")
            response = MockFactoryResponse(request)
        else:
            try:
                response = None
                match method:
                    case "GET":
                        response = requests.get(url, headers=headers)
                    case "DELETE":
                        response = requests.delete(url, headers=headers)
                    case "PATCH":
                        response = requests.patch(url, headers=headers, data=post_data)
                    case "POST":
                        response = requests.post(url, data=post_data, headers=headers)

            except requests.RequestException as e:
                response = e.response

        if response is None:
            raise Exception("Response is None. This should never happen.")

        # run post request hooks
        for post_req_hook in cls._post_request_hooks:
            post_req_hook(
                response,
                path,
                post_data,
                query,
                headers,
                files_list,
                request.AUTHENTICATE,
            )

        if isinstance(response, requests.models.Response):
            response_dict: dict = cls.check_response(
                response, method, path, post_data, query, headers
            )
            return response_dict
