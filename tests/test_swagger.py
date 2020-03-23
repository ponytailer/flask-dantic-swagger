from enum import Enum

from typing import List
from flask_dantic_swagger.schema import (
    basic_schema,
    request_body_schema,
    response_schema,
    definitions_schema
)
from flask_dantic_swagger.swagger import (
    convert_parameter,
    merge_definitions,
    find_definitions
)
from flask_dantic_swagger import ValidatorModel


class A(str, Enum):
    """bbbb"""
    a = "a"


class C(ValidatorModel):
    address: str


class B(ValidatorModel):
    """弄好阿凡达"""
    books: List[str]


class Test(ValidatorModel):
    """Test Model"""
    name: str
    age: int
    a: A
    c: C


def test_schema():
    path = {"test": ""}
    assert basic_schema(path)["paths"] == path

    body = request_body_schema(path)["requestBody"]
    assert body["content"]["application/json"]["schema"] == path

    resp = response_schema(path)["responses"]
    assert resp["200"]["content"]["application/json"]["schema"] == path

    assert definitions_schema(path)["components"]["schemas"] == path


def test_convert_parameter():
    sc = {'title': 'Test', 'description': 'Test Model', 'type': 'object', 'properties': {'name': {'title': 'Name', 'type': 'string'}, 'age': {'title': 'Age', 'type': 'integer'}, 'a': {'title': 'A', 'enum': ['a'], 'type': 'string'}, 'c': {'$ref': '#/components/schemas/C'}}, 'required': ['name', 'age', 'a', 'c']}  # noqa
    ret = convert_parameter(sc)
    assert ret == [{'name': 'name', 'in': 'query', 'schema': {'title': 'Name', 'type': 'string'}}, {'name': 'age', 'in': 'query', 'schema': {'title': 'Age', 'type': 'integer'}}, {'name': 'a', 'in': 'query', 'schema': {'title': 'A', 'enum': ['a'], 'type': 'string'}}, {'name': 'c', 'in': 'query', 'schema': {'$ref': '#/components/schemas/C'}}]  # noqa


def test_merge_definitions():
    assert {} == merge_definitions([])


def test_find_definitions():
    assert find_definitions({"properties": {}}, []) is None
