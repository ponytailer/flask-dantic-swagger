import json

from typing import TypeVar, Set, Dict, List, Any
from .schema import (
    basic_schema,
    request_body_schema,
    request_param_schema,
    response_schema,
    definitions_schema
)


FlaskApp = TypeVar("FlaskApp")
options: Set[str] = {"OPTIONS", "HEAD"}


def generate_swagger(app: FlaskApp, module_name: str) -> Dict[str, Any]:
    """
        param: app
        module_name: shop-api
    """
    schemas: Dict[str, Any] = {}
    definitions: List[Dict[str, Any]] = []
    for name, view in app.view_functions.items():
        if not name.startswith(module_name):
            continue
        if not getattr(view, "response_model", None):
            continue
        # FIXME do not support args in path
        query_model = getattr(view, "query_model", None)
        body_model = getattr(view, "body_model", None)
        model = query_model or body_model

        for rule_func in app.url_map._rules_by_endpoint[name]:
            # request schema convert
            http_method = list(rule_func.methods - options)[0]
            if not model:
                schema = {"summary": "no parameters"}
            else:
                model_schema = model.schema()
                #  replace definitions in request body
                find_definitions(model_schema, definitions)
                if query_model is not None:
                    schema = request_param_schema(
                        convert_parameter(model_schema)
                    )
                else:
                    schema = request_body_schema(model_schema)
            # response schema convert
            resp_model_schema = view.response_model.schema()
            find_definitions(resp_model_schema, definitions)
            schema.update(response_schema(resp_model_schema))
            # {"/testapi/<test_id>"}
            schemas[rule_func.rule] = {http_method.lower(): schema}

    basic: Dict[str, Any] = basic_schema(schemas)
    if definitions:
        basic.update(definitions_schema(merge_definitions(definitions)))
    write_json(module_name, basic)
    return basic


def convert_parameter(model_schema: Dict[str, Any]) -> List[Dict[str, Any]]:
    return [
        {"name": name, "in": "query", "schema": schema}
        for name, schema in model_schema["properties"].items()
    ]


def find_definitions(model_schema: Dict, definitions: List):
    _definitions: Dict[str, Any] = model_schema.pop("definitions", {})
    if _definitions:
        definitions.append(_definitions)
    for __, schema in model_schema["properties"].items():
        ref = schema.get("$ref")
        if ref is None:
            continue
        if schema.get("type") == "array":
            return find_definitions(schema["items"], definitions)
        if "schemas" in ref:
            continue
        schema["$ref"] = ref.replace("definitions", "components/schemas")


def merge_definitions(definitions: List[Dict[str, Any]]) -> Dict[str, Any]:
    definition_map: Dict[str, Any] = {}
    for define in definitions:
        define_name = list(define.keys())[0]
        if define_name not in definition_map:
            definition_map.update(define)
    return definition_map


def write_json(module_name: str, swagger: Dict[str, Any]):
    with open(f"docs/{module_name}-swagger.json", "w") as fd:
        fd.write(json.dumps(swagger, indent=4, ensure_ascii=False))
