from typing import List, Optional
from enum import Enum

from flask import jsonify, request
from pydantic import ValidationError
from flask_dantic_swagger import (
    validate, ValidatorModel
)


class TestEnum(Enum):
    test = "test"


class EnumTest(ValidatorModel):
    enum: TestEnum


class Book(ValidatorModel):
    title: Optional[str]
    price: Optional[int]
    tag: Optional[str] = "book"


class Author(ValidatorModel):
    name: str
    age: int = 30
    books: List[Book]
    address: Optional[str]

    def raise_for_error(self, errors=None):
        errors = {}
        assert self.age > 0
        if errors:
            return super().raise_for_error(errors)


def test_dantic_model():

    book = {"title": "title", "price": "123"}
    book_v = Book(**book)
    assert book_v.title == book["title"]

    author = {"name": "123", "books": [book]}
    author_v = Author(**author)
    assert author_v.name == author["name"]
    assert author_v.books[0].title == book["title"]


def test_body_validate(app, client):

    @app.route("/test", methods=["POST"])
    @validate(body=Author)
    def test():
        return jsonify({})

    book = {"title": "title", "price": "123"}
    author = {"name": "123", "books": [book]}
    resp = client.post("/test", json=author)
    assert resp.status_code == 200


def test_query_validate(app, client):

    @app.route("/book")
    @validate(query=Book)
    def test2():
        return jsonify(request.query_params.document)

    resp = client.get("/book?title=123")
    assert resp.status_code == 200
    assert resp.json["tag"] == "book"
    assert resp.json["title"] == "123"


def test_in_query_validate(app, client):

    @app.route("/names/<path:title>/books", methods=["PUT"])
    @validate(body=Book, validate_path=True)
    def test3(title):
        return jsonify(request.body_params.to_dict())

    book = {"price": "123"}
    resp = client.put("/names/1234/books", json=book)
    assert resp.status_code == 200
    assert resp.json["title"] == "1234"


def test_enum_validate(app, client):

    @app.route("/testenum", methods=["POST"])
    @validate(body=EnumTest)
    def test():
        return jsonify()

    resp = client.post("/testenum", json={"enum": "not_test"})
    assert "validation_error" in resp.json


def test_raise_for_error(app, client):
    @app.errorhandler(ValidationError)
    def error_handler(e):
        return jsonify(errors=e.errors()), 200

    @app.route("/test/raise_for_error", methods=["GET"])
    @validate(query=Book, raise_for_error=True)
    def test():
        return jsonify(success=True)

    resp = client.get("/test/raise_for_error?price=str")
    assert resp.status_code == 200
    assert "errors" in resp.json
