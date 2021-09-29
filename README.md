[![Build Status](https://travis-ci.org/huangxiaohen2738/flask-dantic-swagger.svg?branch=master)](https://travis-ci.org/huangxiaohen2738/flask-dantic-swagger)

[![Coverage Status](https://coveralls.io/repos/huangxiaohen2738/flask-dantic-swagger/badge.png)](https://coveralls.io/r/huangxiaohen2738/flask-dantic-swagger)

### flask-dantic-swagger

Please use the [schema-validator](https://github.com/huangxiaohen2738/schema-validator)

Use the pydantic to validate your request or response in flask,
and it can help you generate swagger quickly.

------------------
``` test/app.py

    class Book(ValidatorModel):
        title: str
        price: int

    class Author(ValidatorModel):
        name: str
        age: int = 30
        books: List[Book]
        address: Optional[str]

    @app.route("/")
    @validate(query=Book, body=Author, response=Author)
    def test_route():
        book_title = request.query_params.title
        author = request.body_params
        author_books = author.books
        return jsonify(author)
    
    test_api = Blueprint("test-api", __name__)

<<< from flask_dantic_swagger import generate_swagger
<<< generate_swagger(app, "")
<<< generate_swagger(app, "test-api") 
```
