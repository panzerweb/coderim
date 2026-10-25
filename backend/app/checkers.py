"""Bounded output comparison shared by local, managed, and authoring judges."""
import json
from .models import Checker, JsonChecker


def normalize(text: str, checker: Checker) -> str:
    # Keep the legacy text contract, including its serialized configuration.
    if checker.normalize_line_endings:
        text = text.replace("\r\n", "\n").replace("\r", "\n")
    if checker.trim_trailing_whitespace_per_line:
        text = "\n".join(line.rstrip(" \t") for line in text.split("\n"))
    if checker.ignore_final_newline and text.endswith("\n"):
        text = text[:-1]
    return text


def _invalid_constant(value):
    raise ValueError("Nonstandard JSON constant")


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON field")
        result[key] = value
    return result


def _parse(text: str, checker: JsonChecker):
    value = json.loads(text, parse_constant=_invalid_constant, object_pairs_hook=_unique_object)
    if checker.value_type == "boolean":
        valid = type(value) is bool
    elif checker.value_type == "string_array":
        valid = type(value) is list and all(type(item) is str for item in value)
    elif checker.value_type == "integer_array":
        valid = type(value) is list and all(type(item) is int for item in value)
    elif checker.value_type == "integer":
        valid = type(value) is int
    else:
        valid = (type(value) is dict and set(value) == {"k", "nums"}
            and type(value["k"]) is int and value["k"] >= 0
            and type(value["nums"]) is list and len(value["nums"]) == value["k"]
            and all(type(item) is int for item in value["nums"]))
    if not valid:
        raise ValueError("JSON output has the wrong type")
    return value


def validate_expected_output(expected: str, checker: Checker | JsonChecker) -> None:
    if checker.type == "json":
        try:
            _parse(expected, checker)
        except (ValueError, RecursionError, OverflowError) as error:
            raise ValueError("Invalid expected JSON output") from error


def outputs_match(actual: str, expected: str, checker: Checker | JsonChecker) -> bool:
    if checker.type == "text":
        return normalize(actual, checker) == normalize(expected, checker)
    # Expected output is validated on loading. A malformed program result is a
    # wrong answer, not an infrastructure failure or incomplete assessment.
    wanted = _parse(expected, checker)
    try:
        value = _parse(actual, checker)
    except (ValueError, RecursionError, OverflowError):
        return False
    if checker.unordered:
        # Sorting preserves multiplicity; using sets would accept duplicates.
        return sorted(value) == sorted(wanted)
    return value == wanted
