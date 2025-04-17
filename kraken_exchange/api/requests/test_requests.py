import importlib
from importlib.util import module_from_spec, spec_from_file_location
import inspect
import string
import sys
from .. import requests
import os
import secrets

checked_classes = []


def gensym(length=32, prefix="gensym_"):
    """
    generates a fairly unique symbol, used to make a module name,
    used as a helper function for load_module

    :return: generated symbol
    """
    alphabet = string.ascii_uppercase + string.ascii_lowercase + string.digits
    symbol = "".join([secrets.choice(alphabet) for i in range(length)])

    return prefix + symbol


def check_request(cls: requests.Request):
    """Does a number of standardized tests on the request class to make sure nothing
    is broken.

    Args:
        request_class (BaseRequest): The request class to be tested.
    """
    # At the end of this module ALL classes thar are not in checked_classes are tested.
    if cls in checked_classes:
        return
    checked_classes.append(cls)
    cls.check()


def is_request(val):
    """Checks an object to see if it's a subclass of requests.Request

    Args:
        val (any): The value to check.

    Returns:
        bool: Whether the value is a subclass of requests.Request
    """

    return inspect.isclass(val) and requests.Request.__qualname__ in map(
        lambda base_class: base_class.__qualname__, val.__bases__
    )


def test_all_requests():
    """
    Ensure all request classes have methods in this file
    """
    for req in filter(is_request, ([getattr(requests, key) for key in dir(requests)])):
        check_request(req)


def test_check_for_unimported_request_classes():
    """Ensure all request classes are imported from ./requests/__init__.py"""
    all_requests = filter(
        is_request, ([getattr(requests, key) for key in dir(requests)])
    )
    all_requests = list(map(lambda req: req.__qualname__, all_requests))  # type: ignore

    dir_path = os.path.dirname(os.path.realpath(__file__))

    files = os.listdir(dir_path)
    files = list(
        filter(
            lambda f: ".py" in f and f not in ["test_requests.py", "__init__.py"], files
        )
    )

    for file in files:
        module_name = file.replace(".py", "")
        module_alias = f"api.requests.{module_name}"
        file_path = f"{dir_path}/{file}"

        # load the module
        spec = spec_from_file_location(module_alias, file_path)
        if spec is None:
            continue

        module = module_from_spec(spec)
        sys.modules[module_name] = module
        if spec.loader is None:
            continue

        spec.loader.exec_module(module)

        # filter out all attributes that aren't request classes
        class_names = list(
            filter(
                lambda cn: cn is not None,
                [d if "Request" in d and d != "Request" else None for d in dir(module)],
            )
        )

        # check to make sure each one has been checked independantly.
        for cn in class_names:
            if not cn or not isinstance(cn, str):
                continue
            class_item = getattr(module, cn)
            assert (
                class_item.__qualname__ in all_requests
            ), "{0} from {1} was not included in src/api/requests/__init__.py".format(
                class_item.__name__, file
            )
