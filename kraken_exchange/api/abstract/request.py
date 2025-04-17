import random
import string
from decimal import Decimal
from ..abstract.api_client import ApiClient
from ..errors import GetFactoryResponseNotImplemented
from ..errors import GetPathNotImplemented
from .api_model import ApiModel


class Request(ApiModel):
    def _gen_alpha_str(self, n: int) -> str:
        return "".join(
            random.choice(
                string.ascii_uppercase + string.ascii_lowercase + string.digits
            )
            for _ in range(n)
        )

    def _gen_tx_id(self):
        return "-".join(
            [self._gen_alpha_str(6), self._gen_alpha_str(5), self._gen_alpha_str(6)]
        )

    @classmethod
    def check(cls):
        """Does a number of standardized tests on each request.

        Args:
            cls (BaseRequest): The request class to be tested.
        """

        instance = cls()

        # make sure that the request class initiates
        assert isinstance(instance, cls)

        # and can return a dict
        dict_res = instance.__dict__
        assert isinstance(
            instance.__dict__, dict
        ), "{0}.__dict__ should be of type dict, not {1}".format(
            cls.__name__, dict_res.__class__.__name__
        )

        # and check if the get_path method returns a URL (or raises the correct exception)
        try:
            url = instance.get_path()
            assert (
                isinstance(url, str) or url is None
            ), "{0}.get_url() must return type of str or None, not {1}".format(
                cls.__name__, url.__class__.__name__
            )
        except Exception as e:
            assert isinstance(
                e, GetPathNotImplemented
            ), "{0}.get_url() must only raise GetPathNotImplemented, not {1}".format(
                cls.__name__, e.__class__.__name__
            )

        # and if the response is being returned correctly.
        try:
            response = instance.get_factory_response()
            assert isinstance(response, dict)
        except Exception as e:
            assert isinstance(
                e, GetFactoryResponseNotImplemented
            ), "{0}.get_factory_response() should only raise GetFactoryResponseNotImplemented, not {1}".format(
                cls.__name__, e.__class__.__name__
            )
