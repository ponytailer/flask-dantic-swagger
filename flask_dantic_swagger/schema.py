basic_schema = lambda path: {  # noqa
    "openapi": "3.0.0",
    "info": {
        "version": "1.0.0",
        "title": "API Swagger"
    },
    "paths": path
}

request_body_schema = lambda x: {  # noqa
    "requestBody": {
        "content": {
            "application/json": {
                "schema": x
            }
        }
    }
}
request_param_schema = lambda x: {  # noqa
    "parameters": x
}
response_schema = lambda x: {  # noqa
    "responses": {
        "200": {
            "description": "success",
            "content": {
                "application/json": {
                    "schema": x
                }
            }
        }
    }
}

definitions_schema = lambda x: {  # noqa
    "components": {
        "schemas": x
    }
}
