import doctest

import pytest

import jsonpath_ng
from jsonpath_ng.ext import parse


@pytest.mark.parametrize(
    ["string", "initial_data", "insert_val", "target"],
    [
        ("$.foo", {}, 42, {"foo": 42}),
        ("$.foo.bar", {}, 42, {"foo": {"bar": 42}}),
        ("$.foo[0]", {}, 42, {"foo": [42]}),
        ("$.foo[1]", {}, 42, {"foo": [{}, 42]}),
        ("$.foo[0].bar", {}, 42, {"foo": [{"bar": 42}]}),
        ("$.foo[1].bar", {}, 42, {"foo": [{}, {"bar": 42}]}),
        ("$.foo[0][0]", {}, 42, {"foo": [[42]]}),
        ("$.foo[1][1]", {}, 42, {"foo": [{}, [{}, 42]]}),
        ("foo[0]", {}, 42, {"foo": [42]}),
        ("foo[1]", {}, 42, {"foo": [{}, 42]}),
        ("foo", {}, 42, {"foo": 42}),
        # Initial data can be a list if we expect a list back
        ("[0]", [], 42, [42]),
        ("[1]", [], 42, [{}, 42]),
        # Converts initial data to a list if necessary
        ("[0]", {}, 42, [42]),
        ("[1]", {}, 42, [{}, 42]),
        (
            'foo[?bar="baz"].qux',
            {
                "foo": [
                    {"bar": "baz"},
                    {"bar": "bizzle"},
                ]
            },
            42,
            {"foo": [{"bar": "baz", "qux": 42}, {"bar": "bizzle"}]},
        ),
    ],
)
def test_update_or_create(string, initial_data, insert_val, target):
    jsonpath = parse(string)
    result = jsonpath.update_or_create(initial_data, insert_val)
    assert result == target


@pytest.mark.parametrize(
    ["string", "initial_data", "insert_val", "target"],
    [
        # Slice not supported
        ("foo[0:1]", {}, 42, {"foo": [42, 42]}),
        # result is {'foo': {}}
        # Filter does not create items to meet criteria
        ('foo[?bar="baz"].qux', {}, 42, {"foo": [{"bar": "baz", "qux": 42}]}),
        # result is {'foo': {}}
        # Does not convert initial data to a dictionary
        ("foo", [], 42, {"foo": 42}),
        # raises TypeError
    ],
)
@pytest.mark.xfail
def test_unsupported_classes(string, initial_data, insert_val, target):
    jsonpath = parse(string)
    result = jsonpath.update_or_create(initial_data, insert_val)
    assert result == target


@pytest.mark.parametrize(
    ["string", "initial_data", "insert_val", "target"],
    [
        ("$.name[0].text", {}, "Sir Michael", {"name": [{"text": "Sir Michael"}]}),
        (
            "$.name[0].given[0]",
            {"name": [{"text": "Sir Michael"}]},
            "Michael",
            {"name": [{"text": "Sir Michael", "given": ["Michael"]}]},
        ),
        (
            "$.name[0].prefix[0]",
            {"name": [{"text": "Sir Michael", "given": ["Michael"]}]},
            "Sir",
            {
                "name": [
                    {"text": "Sir Michael", "given": ["Michael"], "prefix": ["Sir"]}
                ]
            },
        ),
        (
            "$.birthDate",
            {
                "name": [
                    {"text": "Sir Michael", "given": ["Michael"], "prefix": ["Sir"]}
                ]
            },
            "1943-05-05",
            {
                "name": [
                    {"text": "Sir Michael", "given": ["Michael"], "prefix": ["Sir"]}
                ],
                "birthDate": "1943-05-05",
            },
        ),
    ],
)
def test_build_doc(string, initial_data, insert_val, target):
    jsonpath = parse(string)
    result = jsonpath.update_or_create(initial_data, insert_val)
    assert result == target


def test_doctests():
    results = doctest.testmod(jsonpath_ng)
    assert results.failed == 0
