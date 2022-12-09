import pytest
from src.requestClasses import *
import random
import string
from typing import Any

testclasses = [
    GraphRequest,
    SearchRequest
]


def get_random_value(parameter_type):
    if parameter_type == int:
        return random.randint(1, 10)
    elif parameter_type == str:
        return str(''.join([random.choice(string.ascii_letters)
                            for _ in range(random.randint(4, 10))]))
    else:
        raise TypeError(f'Unknown type of parameter: {parameter_type}')


def generate_input(parameters: dict[str, type]) -> dict[str, Any]:
    data = {}

    for parameter, t in parameters.items():
        data[parameter] = get_random_value(t)

    return data


@pytest.mark.parametrize("request_class", testclasses)
def test_request_all_parameters(request_class):
    all_parameters = request_class.get_parameters()

    data = generate_input(all_parameters)

    req = request_class(**data)

    for parameter in all_parameters.keys():
        assert data[parameter] == getattr(req, parameter)


@pytest.mark.parametrize("request_class", testclasses)
def test_request_only_required(request_class):
    require_parameters = request_class.get_required_parameters()
    optional_parameters = request_class.get_optional_parameters()

    data = generate_input(require_parameters)

    req = request_class(**data)

    for parameter in require_parameters.keys():
        assert data[parameter] == getattr(req, parameter)

    for parameter in optional_parameters.keys():
        assert getattr(request_class, parameter) == getattr(req, parameter)


@pytest.mark.parametrize("request_class", testclasses)
def test_graph_request_without_required(request_class):
    require_parameters = request_class.get_required_parameters()
    all_parameters = request_class.get_parameters()

    base = generate_input(all_parameters)

    for parameter in require_parameters.keys():
        data = base.copy()
        data.pop(parameter)

        with pytest.raises(AttributeError):
            request_class(**data)
