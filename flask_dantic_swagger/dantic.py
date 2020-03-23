from functools import wraps
from typing import Optional, Callable, Any, Type, Dict

from flask import request, jsonify
from pydantic import BaseModel, ValidationError
from requests.status_codes import codes


class ValidatorModel(BaseModel):
    """
    Define the request args model:

    class Book(ValidatorModel):
        title: str
        price: int

    class Author(ValidatorModel):
        name: str
        age: int = 30
        books: List[Book]
        address: Optional[str]
    """

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.raise_for_error()

    def raise_for_error(self, errors=None):
        """Define the method to check your business
        For example:
            def raise_for_error(self, errors=None):
                errors = errors or {}
                errors["name"] = f"{self.name} was invalid"
                errors["age"] = f"{self.name}'s age is too old: {self.age}"
                if errors:
                    return super().raise_for_error(errors)
        """
        if errors:
            raise ValidationError(errors, ValidatorModel)

    @property
    def document(self) -> Dict:
        return self.dict()

    def to_dict(self) -> Dict:
        return self.dict()

    def populate_obj(self, obj: object) -> object:
        """can set attribute quickly"""
        for key, val in self.document.items():
            setter = getattr(obj, "set_{0}".format(key), None)
            if setter:
                setter(val)
            else:
                setattr(obj, key, val)
        return obj


def validate(
    body: Optional[Type[ValidatorModel]] = None,
    query: Optional[Type[ValidatorModel]] = None,
    validate_path: bool = False,
    response: Optional[Type[ValidatorModel]] = None,
    raise_for_error: bool = False
):
    """
    Pydantic's faster than cerberus 26.3x in document benchmarks with python3.7
    Request parameters are accessible via flask's `request` variable:
        - request.query_params
        - request.body_params

    And if the validate_path is true,
    it could merge the `request.view_args` into the parameters or body

    @app.route("/")
    @validate(query=Book, body=Author)
    def test_route():
        book_title = request.query_params.title
        author = request.body_params
        author_books = author.books
        return jsonify(author)
    """
    def decorator(func: Callable[[Any], Any]):
        """ for swagger """
        if query is not None:
            func.query_model = query
        if body is not None:
            func.body_model = body
        func.response_model = response

        @wraps(func)
        def wrapper(*args, **kwargs):
            q, b, err = None, None, {}
            if query is not None:
                query_params = dict(request.view_args) if validate_path else {}
                query_params.update(dict(request.args.items()))
                if raise_for_error:
                    q = query(**query_params)
                else:
                    try:
                        q = query(**query_params)
                    except ValidationError as ve:
                        err["query_params"] = str(ve.errors())
                request.query_params = q
            if body is not None:
                body_params = dict(request.view_args) if validate_path else {}
                body_params.update(request.get_json(True))
                if raise_for_error:
                    b = body(**body_params)
                else:
                    try:
                        b = body(**body_params)
                    except ValidationError as ve:
                        err["body_params"] = str(ve.errors())
                request.body_params = b
            if err:
                return jsonify(validation_error=err), codes.bad_request
            return func(*args, **kwargs)
        return wrapper
    return decorator
