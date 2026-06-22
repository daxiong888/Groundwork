#!/usr/bin/env python3
import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ValidationError:
    path: str
    message: str

    def __str__(self):
        return f"{self.path}: {self.message}"


class SchemaResolver:
    def __init__(self):
        self._cache = {}

    def load_json(self, path):
        path = Path(path).resolve()
        if path not in self._cache:
            self._cache[path] = json.loads(path.read_text(encoding="utf-8"))
        return self._cache[path]

    def resolve_ref(self, ref, base_path):
        if "#" in ref:
            path_part, pointer = ref.split("#", 1)
        else:
            path_part, pointer = ref, ""
        target_path = Path(base_path).resolve() if not path_part else (Path(base_path).resolve().parent / path_part).resolve()
        target = self.load_json(target_path)
        if pointer:
            if not pointer.startswith("/"):
                raise ValueError(f"unsupported JSON pointer in $ref: {ref}")
            for part in pointer.lstrip("/").split("/"):
                key = part.replace("~1", "/").replace("~0", "~")
                target = target[key]
        return target, target_path


def type_matches(value, expected):
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return (isinstance(value, int) or isinstance(value, float)) and not isinstance(value, bool)
    if expected == "null":
        return value is None
    return True


def json_key(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def validate_instance(instance, schema, resolver, base_path, path="$"):
    errors = []

    if "$ref" in schema:
        target, target_path = resolver.resolve_ref(schema["$ref"], base_path)
        return validate_instance(instance, target, resolver, target_path, path)

    for sub_schema in schema.get("allOf", []):
        errors.extend(validate_instance(instance, sub_schema, resolver, base_path, path))

    if "if" in schema:
        if not validate_instance(instance, schema["if"], resolver, base_path, path):
            errors.extend(validate_instance(instance, schema.get("then", {}), resolver, base_path, path))

    if "const" in schema and instance != schema["const"]:
        errors.append(ValidationError(path, f"expected const {schema['const']!r}, got {instance!r}"))

    if "enum" in schema and instance not in schema["enum"]:
        allowed = ", ".join(str(item) for item in schema["enum"])
        errors.append(ValidationError(path, f"value {instance!r} is not one of: {allowed}"))

    expected_type = schema.get("type")
    if expected_type:
        expected_types = expected_type if isinstance(expected_type, list) else [expected_type]
        if not any(type_matches(instance, item) for item in expected_types):
            errors.append(ValidationError(path, f"expected type {expected_type}, got {type(instance).__name__}"))
            return errors

    if isinstance(instance, str):
        if "minLength" in schema and len(instance) < schema["minLength"]:
            errors.append(ValidationError(path, f"expected minLength {schema['minLength']}"))
        if "pattern" in schema and not re.search(schema["pattern"], instance):
            errors.append(ValidationError(path, f"value does not match pattern {schema['pattern']!r}"))

    if isinstance(instance, list):
        item_schema = schema.get("items")
        if item_schema:
            for index, item in enumerate(instance):
                errors.extend(validate_instance(item, item_schema, resolver, base_path, f"{path}[{index}]"))
        if schema.get("uniqueItems"):
            seen = set()
            for index, item in enumerate(instance):
                key = json_key(item)
                if key in seen:
                    errors.append(ValidationError(f"{path}[{index}]", "duplicate item violates uniqueItems"))
                seen.add(key)

    if isinstance(instance, dict):
        required = schema.get("required", [])
        for key in required:
            if key not in instance:
                errors.append(ValidationError(path, f"missing required property {key!r}"))

        property_name_schema = schema.get("propertyNames")
        if property_name_schema:
            for key in instance:
                errors.extend(validate_instance(key, property_name_schema, resolver, base_path, f"{path}.{key}"))

        properties = schema.get("properties", {})
        for key, value in instance.items():
            if key in properties:
                errors.extend(validate_instance(value, properties[key], resolver, base_path, f"{path}.{key}"))
            elif schema.get("additionalProperties") is False:
                errors.append(ValidationError(f"{path}.{key}", "additional property is not allowed"))
            elif isinstance(schema.get("additionalProperties"), dict):
                errors.extend(
                    validate_instance(
                        value,
                        schema["additionalProperties"],
                        resolver,
                        base_path,
                        f"{path}.{key}",
                    )
                )

    return errors


def validate_json_file(schema_path, instance_path):
    resolver = SchemaResolver()
    schema_path = Path(schema_path)
    instance_path = Path(instance_path)
    schema = resolver.load_json(schema_path)
    instance = json.loads(instance_path.read_text(encoding="utf-8"))
    return validate_instance(instance, schema, resolver, schema_path)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Validate a JSON instance against the Groundwork schema subset.")
    parser.add_argument("schema", type=Path)
    parser.add_argument("instance", type=Path)
    args = parser.parse_args(argv)

    errors = validate_json_file(args.schema, args.instance)
    if errors:
        print("schema_validation=fail")
        for error in errors:
            print(error)
        return 1
    print("schema_validation=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
