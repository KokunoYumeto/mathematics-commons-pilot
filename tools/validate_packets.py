#!/usr/bin/env python3
"""Validate Mathematics Commons pilot records without network dependencies.

The repository publishes Draft 2020-12 JSON Schemas as the portable contract.
This tool implements the deliberately small schema subset used by those files so
that contributors can run the same fail-closed check with only Python's standard
library. Unsupported schema keywords are errors rather than silently ignored.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import subprocess
import sys
import uuid
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urldefrag, urlparse


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "schemas"
PILOT_SCHEMA_NAMES = (
    "evidence-record.schema.json",
    "packet-transition.schema.json",
    "problem-record.schema.json",
    "research-packet.schema.json",
    "review-record.schema.json",
    "run-record.schema.json",
    "source-record.schema.json",
)
LIVE_INSTANCE_DIRS = (
    "packets",
    "problems",
    "sources",
    "runs",
    "evidence",
    "reviews",
    "transitions",
    "records",
)
DEFAULT_INSTANCE_DIRS = (
    *LIVE_INSTANCE_DIRS,
    "examples",
)

# Resource limits are part of the validator's public safety contract.  They keep
# discovery and parsing bounded before any untrusted record or schema is loaded.
MAX_JSON_FILE_BYTES = 2 * 1024 * 1024
MAX_ARTIFACT_BYTES = 256 * 1024 * 1024
MAX_INSTANCE_FILES = 2048
MAX_TOTAL_JSON_BYTES = 32 * 1024 * 1024
MAX_DIRECTORY_DEPTH = 16
MAX_WALK_ENTRIES = 10000
MAX_PATTERN_LENGTH = 512
MAX_REGEX_INPUT_LENGTH = 2 * 1024 * 1024
MAX_GIT_TREE_LIST_BYTES = 16 * 1024 * 1024
MAX_GIT_TREE_ENTRIES = 100_000
FULL_GIT_COMMIT = re.compile(r"^[0-9a-f]{40}$")

SAFE_COMPLEX_PATTERNS = {
    # The mandatory slash separator makes each repetition unambiguous; the
    # leading assertion only rejects parent-directory path segments.
    r"^(?!.*(?:^|/)\.\.(?:/|$))[A-Za-z0-9._-]+(?:/[A-Za-z0-9._-]+)*$",
}

SCHEMA_TYPES = {
    "null",
    "boolean",
    "integer",
    "number",
    "string",
    "array",
    "object",
}

DRAFT_2020_12 = "https://json-schema.org/draft/2020-12/schema"
SUPPORTED_FORMATS = {"date", "date-time", "uri", "uri-reference", "uuid"}
SUPPORTED_KEYWORDS = {
    "$comment",
    "$defs",
    "$id",
    "$ref",
    "$schema",
    "additionalProperties",
    "allOf",
    "anyOf",
    "const",
    "default",
    "deprecated",
    "description",
    "enum",
    "examples",
    "exclusiveMaximum",
    "exclusiveMinimum",
    "format",
    "items",
    "maximum",
    "maxItems",
    "maxLength",
    "maxProperties",
    "minimum",
    "minItems",
    "minLength",
    "minProperties",
    "multipleOf",
    "not",
    "oneOf",
    "pattern",
    "properties",
    "readOnly",
    "required",
    "title",
    "type",
    "uniqueItems",
    "writeOnly",
}


class DuplicateKeyError(ValueError):
    """Raised when JSON contains an ambiguous duplicate object key."""


def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError(f"duplicate key {key!r}")
        result[key] = value
    return result


def reject_nonfinite_number(value: str) -> Any:
    raise ValueError(f"non-finite JSON number {value!r} is not permitted")


def load_json(path: Path) -> Any:
    try:
        if path.is_symlink():
            raise ValueError("symbolic-link JSON inputs are not permitted")
        size = path.stat().st_size
        if size > MAX_JSON_FILE_BYTES:
            raise ValueError(
                f"JSON file is {size} bytes; limit is {MAX_JSON_FILE_BYTES}"
            )
        return json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=reject_duplicate_keys,
            parse_constant=reject_nonfinite_number,
        )
    except (
        OSError,
        UnicodeError,
        json.JSONDecodeError,
        RecursionError,
        ValueError,
    ) as exc:
        raise ValueError(f"{path}: invalid JSON: {exc}") from exc


def json_identity(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def display_path(parts: tuple[Any, ...]) -> str:
    if not parts:
        return "$"
    rendered = "$"
    for part in parts:
        if isinstance(part, int):
            rendered += f"[{part}]"
        elif re.fullmatch(r"[A-Za-z_][A-Za-z0-9_-]*", str(part)):
            rendered += f".{part}"
        else:
            rendered += f"[{json.dumps(str(part))}]"
    return rendered


@dataclass(frozen=True)
class SchemaDocument:
    path: Path
    body: dict[str, Any]

    @property
    def schema_id(self) -> str:
        return str(self.body["$id"])


class SchemaSet:
    def __init__(self, documents: list[SchemaDocument]) -> None:
        self.documents = documents
        self.by_id: dict[str, SchemaDocument] = {}
        self.by_name: dict[str, SchemaDocument] = {}
        self.by_record_type: dict[str, SchemaDocument] = {}
        for document in documents:
            if document.schema_id in self.by_id:
                raise ValueError(f"duplicate schema $id: {document.schema_id}")
            self.by_id[document.schema_id] = document
            self.by_name[document.path.name] = document
            record_type = (
                document.body.get("properties", {})
                .get("record_type", {})
                .get("const")
            )
            if isinstance(record_type, str):
                if record_type in self.by_record_type:
                    raise ValueError(f"duplicate record_type schema: {record_type}")
                self.by_record_type[record_type] = document

    def resolve(
        self,
        reference: str,
        current: SchemaDocument,
    ) -> tuple[SchemaDocument, Any]:
        target, fragment = urldefrag(reference)
        if not target:
            document = current
        else:
            # Never alias a reference by URL basename.  Otherwise an arbitrary
            # remote URL ending in a trusted filename could silently resolve to
            # a local schema.  Cross-document references must name the exact
            # published $id; all current schemas use document-local fragments.
            document = self.by_id.get(target)
            if document is None:
                raise ValueError(
                    f"{current.path}: schema reference target must be an exact local "
                    f"$id, not a filename alias: {reference!r}"
                )
        node: Any = document.body
        if fragment:
            if not fragment.startswith("/"):
                raise ValueError(
                    f"{current.path}: unsupported non-pointer fragment in {reference!r}"
                )
            for encoded in fragment[1:].split("/"):
                token = encoded.replace("~1", "/").replace("~0", "~")
                if isinstance(node, dict) and token in node:
                    node = node[token]
                elif isinstance(node, list) and token.isdigit() and int(token) < len(node):
                    node = node[int(token)]
                else:
                    raise ValueError(
                        f"{current.path}: unresolved JSON Pointer in {reference!r}"
                    )
        return document, node


def iter_schema_nodes(schema: Any, path: tuple[Any, ...] = ()) -> Iterable[tuple[tuple[Any, ...], Any]]:
    yield path, schema
    if not isinstance(schema, dict):
        return
    for keyword in ("$defs", "properties"):
        values = schema.get(keyword)
        if isinstance(values, dict):
            for name, child in values.items():
                yield from iter_schema_nodes(child, path + (keyword, name))
    additional = schema.get("additionalProperties")
    if isinstance(additional, dict):
        yield from iter_schema_nodes(additional, path + ("additionalProperties",))
    items = schema.get("items")
    if isinstance(items, dict):
        yield from iter_schema_nodes(items, path + ("items",))
    for keyword in ("allOf", "anyOf", "oneOf"):
        values = schema.get(keyword)
        if isinstance(values, list):
            for index, child in enumerate(values):
                yield from iter_schema_nodes(child, path + (keyword, index))
    negated = schema.get("not")
    if isinstance(negated, dict):
        yield from iter_schema_nodes(negated, path + ("not",))


def is_json_integer(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def is_json_number(value: Any) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
    )


def safe_pattern_error(pattern: Any) -> str | None:
    """Return a reason when a schema regex is outside the bounded safe dialect."""

    if not isinstance(pattern, str):
        return "pattern must be a string"
    if len(pattern) > MAX_PATTERN_LENGTH:
        return f"pattern exceeds {MAX_PATTERN_LENGTH} characters"
    if not pattern.startswith("^") or not pattern.endswith("$"):
        return "pattern must be explicitly anchored with ^ and $"
    if pattern in SAFE_COMPLEX_PATTERNS:
        try:
            re.compile(pattern)
        except re.error as exc:
            return f"invalid pattern: {exc}"
        return None
    # Backreferences, lookbehind, conditionals and atomic/recursive constructs
    # are unnecessary for the public schemas and create avoidable complexity.
    prohibited = (
        r"\\[1-9]",
        r"\(\?P=",
        r"\(\?<=[^)]",
        r"\(\?<![^)]",
        r"\(\?>",
        r"\(\?\(",
        r"\(\?R",
        r"\(\?0",
    )
    for token in prohibited:
        if re.search(token, pattern):
            return "pattern uses a prohibited backreference or advanced construct"
    # Reject the classic nested-quantifier shape, including `(a+)+` and
    # `(.*){2,}`.  The shipped path lookahead contains `.*` but its enclosing
    # assertion is not quantified and therefore does not match this rule.
    if re.search(
        r"\((?:\?[:=!])?(?:[^()\\]|\\.)*[+*](?:[^()\\]|\\.)*\)"
        r"(?:[+*]|\{\d+(?:,\d*)?\})",
        pattern,
    ):
        return "pattern contains a prohibited nested quantifier"
    # Quantifying an alternation can also create exponential backtracking when
    # alternatives overlap (for example ``^(a|aa)+$``).  The public schemas do
    # not need quantified alternation, so reject the whole risky family rather
    # than attempting a brittle overlap proof.
    if re.search(
        r"\((?:\?[:=!])?(?:[^()\\]|\\.)*\|(?:[^()\\]|\\.)*\)"
        r"(?:[+*]|\{\d+(?:,\d*)?\})",
        pattern,
    ):
        return "pattern contains a prohibited quantified alternation"
    try:
        re.compile(pattern)
    except re.error as exc:
        return f"invalid pattern: {exc}"
    return None


def lint_schema_node_shape(
    document: SchemaDocument,
    node_path: tuple[Any, ...],
    node: dict[str, Any],
) -> list[str]:
    """Meta-validate the supported JSON-Schema subset, including value shapes."""

    errors: list[str] = []
    location = display_path(node_path)

    def error(message: str) -> None:
        errors.append(f"{document.path}: {location} {message}")

    for keyword in ("$comment", "title", "description"):
        if keyword in node and not isinstance(node[keyword], str):
            error(f"{keyword} must be a string")
    for keyword in ("$schema", "$id", "$ref", "format"):
        if keyword in node and (
            not isinstance(node[keyword], str) or not node[keyword]
        ):
            error(f"{keyword} must be a non-empty string")
    if node_path and ("$schema" in node or "$id" in node):
        error("nested $schema and $id declarations are not supported")

    schema_type = node.get("type")
    if schema_type is not None:
        if isinstance(schema_type, str):
            declared_types = [schema_type]
        elif (
            isinstance(schema_type, list)
            and schema_type
            and all(isinstance(item, str) for item in schema_type)
            and len(schema_type) == len(set(schema_type))
        ):
            declared_types = schema_type
        else:
            declared_types = []
            error("type must be a supported string or non-empty unique string array")
        unsupported_types = sorted(set(declared_types) - SCHEMA_TYPES)
        if unsupported_types:
            error("type uses unsupported names: " + ", ".join(unsupported_types))

    for keyword in ("$defs", "properties"):
        if keyword in node and not isinstance(node[keyword], dict):
            error(f"{keyword} must be an object of schema values")
    additional = node.get("additionalProperties")
    if "additionalProperties" in node and not isinstance(additional, (dict, bool)):
        error("additionalProperties must be a boolean or schema object")
    items = node.get("items")
    if "items" in node and not isinstance(items, (dict, bool)):
        error("items must be a boolean or one schema object")
    negated = node.get("not")
    if "not" in node and not isinstance(negated, (dict, bool)):
        error("not must be a boolean or schema object")
    for keyword in ("allOf", "anyOf", "oneOf"):
        branches = node.get(keyword)
        if keyword in node and not (
            isinstance(branches, list)
            and branches
            and all(isinstance(branch, (dict, bool)) for branch in branches)
        ):
            error(f"{keyword} must be a non-empty array of schemas")

    required = node.get("required")
    if "required" in node and not (
        isinstance(required, list)
        and all(isinstance(item, str) and item for item in required)
        and len(required) == len(set(required))
    ):
        error("required must be a unique array of non-empty strings")
    enum = node.get("enum")
    if "enum" in node:
        if not isinstance(enum, list) or not enum:
            error("enum must be a non-empty array")
        elif len({json_identity(item) for item in enum}) != len(enum):
            error("enum values must be unique")
    if "examples" in node and not isinstance(node["examples"], list):
        error("examples must be an array")
    for keyword in ("deprecated", "readOnly", "writeOnly", "uniqueItems"):
        if keyword in node and not isinstance(node[keyword], bool):
            error(f"{keyword} must be a boolean")

    integer_limits = (
        "minLength",
        "maxLength",
        "minItems",
        "maxItems",
        "minProperties",
        "maxProperties",
    )
    for keyword in integer_limits:
        if keyword in node and (
            not is_json_integer(node[keyword]) or node[keyword] < 0
        ):
            error(f"{keyword} must be a non-negative integer")
    for minimum_name, maximum_name in (
        ("minLength", "maxLength"),
        ("minItems", "maxItems"),
        ("minProperties", "maxProperties"),
    ):
        if (
            is_json_integer(node.get(minimum_name))
            and is_json_integer(node.get(maximum_name))
            and node[minimum_name] > node[maximum_name]
        ):
            error(f"{minimum_name} cannot exceed {maximum_name}")
    for keyword in ("minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum"):
        if keyword in node and not is_json_number(node[keyword]):
            error(f"{keyword} must be a finite number")
    if "multipleOf" in node and (
        not is_json_number(node["multipleOf"]) or node["multipleOf"] <= 0
    ):
        error("multipleOf must be a finite number greater than zero")

    if "pattern" in node:
        reason = safe_pattern_error(node["pattern"])
        if reason is not None:
            error(reason)
    return errors


def lint_schema(document: SchemaDocument) -> list[str]:
    errors: list[str] = []
    body = document.body
    if body.get("$schema") != DRAFT_2020_12:
        errors.append(f"{document.path}: must declare {DRAFT_2020_12}")
    if not isinstance(body.get("$id"), str) or not body["$id"].strip():
        errors.append(f"{document.path}: missing non-empty $id")
    properties = body.get("properties", {})
    record_type = properties.get("record_type", {}) if isinstance(properties, dict) else {}
    schema_version = properties.get("schema_version", {}) if isinstance(properties, dict) else {}
    is_record_schema = isinstance(record_type.get("const"), str)
    if is_record_schema:
        if body.get("type") != "object":
            errors.append(f"{document.path}: record schema must have top-level type object")
        required = body.get("required")
        if not isinstance(required, list) or not {
            "record_type",
            "schema_version",
        }.issubset(required):
            errors.append(
                f"{document.path}: top-level required must include record_type and schema_version"
            )
        if schema_version.get("const") != "0.1.0":
            errors.append(f"{document.path}: schema_version const must be 0.1.0")
        if body.get("additionalProperties") is not False:
            errors.append(f"{document.path}: top-level additionalProperties must be false")
    elif not isinstance(body.get("$defs"), dict) or not body["$defs"]:
        errors.append(
            f"{document.path}: auxiliary schema must provide non-empty reusable $defs"
        )

    for node_path, node in iter_schema_nodes(body):
        location = display_path(node_path)
        if isinstance(node, bool):
            continue
        if not isinstance(node, dict):
            errors.append(f"{document.path}: {location} is not a schema object")
            continue
        unsupported = sorted(set(node) - SUPPORTED_KEYWORDS)
        if unsupported:
            errors.append(
                f"{document.path}: {location} uses unsupported keywords: "
                + ", ".join(unsupported)
            )
        errors.extend(lint_schema_node_shape(document, node_path, node))
        fmt = node.get("format")
        if fmt is not None and fmt not in SUPPORTED_FORMATS:
            errors.append(f"{document.path}: {location} uses unsupported format {fmt!r}")
    return errors


def load_schema_set(schema_dir: Path = SCHEMA_DIR) -> SchemaSet:
    if not schema_dir.is_dir():
        raise ValueError(f"missing schema directory: {schema_dir}")
    paths = [schema_dir / name for name in PILOT_SCHEMA_NAMES]
    missing = [path.name for path in paths if not path.is_file()]
    if missing:
        raise ValueError(
            f"missing pilot record schemas in {schema_dir}: {', '.join(missing)}"
        )
    documents: list[SchemaDocument] = []
    for path in paths:
        body = load_json(path)
        if not isinstance(body, dict):
            raise ValueError(f"{path}: schema root must be an object")
        documents.append(SchemaDocument(path=path, body=body))
    schema_set = SchemaSet(documents)
    errors: list[str] = []
    for document in documents:
        errors.extend(lint_schema(document))
        for _, node in iter_schema_nodes(document.body):
            if isinstance(node, dict) and isinstance(node.get("$ref"), str):
                try:
                    schema_set.resolve(node["$ref"], document)
                except ValueError as exc:
                    errors.append(str(exc))
    if errors:
        raise ValueError("\n".join(errors))
    if not schema_set.by_record_type:
        raise ValueError("schema set contains no record_type dispatch constants")
    return schema_set


def is_type(value: Any, expected: str) -> bool:
    if expected == "null":
        return value is None
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)
    if expected == "string":
        return isinstance(value, str)
    if expected == "array":
        return isinstance(value, list)
    if expected == "object":
        return isinstance(value, dict)
    return False


def valid_format(value: str, fmt: str) -> bool:
    try:
        if fmt == "date":
            date.fromisoformat(value)
            return bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", value))
        if fmt == "date-time":
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            return parsed.tzinfo is not None
        if fmt == "uri":
            parsed = urlparse(value)
            return bool(parsed.scheme and (parsed.netloc or parsed.scheme == "urn"))
        if fmt == "uri-reference":
            return not any(char.isspace() for char in value)
        if fmt == "uuid":
            uuid.UUID(value)
            return True
    except (ValueError, TypeError):
        return False
    return False


def validate_instance(
    instance: Any,
    schema: Any,
    schema_set: SchemaSet,
    document: SchemaDocument,
    instance_path: tuple[Any, ...] = (),
) -> list[str]:
    errors: list[str] = []
    location = display_path(instance_path)
    if isinstance(schema, bool):
        return [] if schema else [f"{location}: rejected by false schema"]
    if not isinstance(schema, dict):
        return [f"{location}: internal error: schema is not an object"]

    reference = schema.get("$ref")
    if isinstance(reference, str):
        resolved_document, resolved_schema = schema_set.resolve(reference, document)
        errors.extend(
            validate_instance(
                instance,
                resolved_schema,
                schema_set,
                resolved_document,
                instance_path,
            )
        )

    for subschema in schema.get("allOf", []):
        errors.extend(validate_instance(instance, subschema, schema_set, document, instance_path))

    any_of = schema.get("anyOf")
    if isinstance(any_of, list):
        branches = [
            validate_instance(instance, branch, schema_set, document, instance_path)
            for branch in any_of
        ]
        if all(branch_errors for branch_errors in branches):
            errors.append(f"{location}: does not satisfy any allowed schema alternative")

    one_of = schema.get("oneOf")
    if isinstance(one_of, list):
        matches = sum(
            not validate_instance(instance, branch, schema_set, document, instance_path)
            for branch in one_of
        )
        if matches != 1:
            errors.append(f"{location}: must satisfy exactly one schema alternative; matched {matches}")

    negated = schema.get("not")
    if isinstance(negated, (dict, bool)) and not validate_instance(
        instance, negated, schema_set, document, instance_path
    ):
        errors.append(f"{location}: matches a prohibited schema")

    expected = schema.get("type")
    if expected is not None:
        allowed = [expected] if isinstance(expected, str) else expected
        if not isinstance(allowed, list) or not all(isinstance(item, str) for item in allowed):
            errors.append(f"{location}: internal error: malformed type constraint")
            return errors
        if not any(is_type(instance, item) for item in allowed):
            errors.append(
                f"{location}: expected {' or '.join(allowed)}, got {type(instance).__name__}"
            )
            return errors

    if "const" in schema and json_identity(instance) != json_identity(schema["const"]):
        errors.append(f"{location}: must equal {schema['const']!r}")
    if "enum" in schema and all(
        json_identity(instance) != json_identity(choice) for choice in schema["enum"]
    ):
        errors.append(f"{location}: value is not in the allowed enumeration")

    if isinstance(instance, str):
        if len(instance) > MAX_REGEX_INPUT_LENGTH and "pattern" in schema:
            errors.append(
                f"{location}: string exceeds bounded pattern-input limit "
                f"{MAX_REGEX_INPUT_LENGTH}"
            )
            return errors
        if len(instance) < schema.get("minLength", 0):
            errors.append(f"{location}: string is shorter than minLength")
        if "maxLength" in schema and len(instance) > schema["maxLength"]:
            errors.append(f"{location}: string is longer than maxLength")
        if "pattern" in schema and re.search(schema["pattern"], instance) is None:
            errors.append(f"{location}: string does not match required pattern")
        if "format" in schema and not valid_format(instance, schema["format"]):
            errors.append(f"{location}: invalid {schema['format']} value")

    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        if "minimum" in schema and instance < schema["minimum"]:
            errors.append(f"{location}: number is below minimum")
        if "maximum" in schema and instance > schema["maximum"]:
            errors.append(f"{location}: number is above maximum")
        if "exclusiveMinimum" in schema and instance <= schema["exclusiveMinimum"]:
            errors.append(f"{location}: number is not above exclusiveMinimum")
        if "exclusiveMaximum" in schema and instance >= schema["exclusiveMaximum"]:
            errors.append(f"{location}: number is not below exclusiveMaximum")
        if "multipleOf" in schema:
            quotient = instance / schema["multipleOf"]
            if not math.isclose(quotient, round(quotient), rel_tol=0.0, abs_tol=1e-12):
                errors.append(f"{location}: number is not a required multiple")

    if isinstance(instance, list):
        if len(instance) < schema.get("minItems", 0):
            errors.append(f"{location}: array has fewer than minItems")
        if "maxItems" in schema and len(instance) > schema["maxItems"]:
            errors.append(f"{location}: array has more than maxItems")
        if schema.get("uniqueItems"):
            identities = [json_identity(item) for item in instance]
            if len(identities) != len(set(identities)):
                errors.append(f"{location}: array items must be unique")
        item_schema = schema.get("items")
        if isinstance(item_schema, (dict, bool)):
            for index, value in enumerate(instance):
                errors.extend(
                    validate_instance(
                        value,
                        item_schema,
                        schema_set,
                        document,
                        instance_path + (index,),
                    )
                )

    if isinstance(instance, dict):
        if len(instance) < schema.get("minProperties", 0):
            errors.append(f"{location}: object has fewer than minProperties")
        if "maxProperties" in schema and len(instance) > schema["maxProperties"]:
            errors.append(f"{location}: object has more than maxProperties")
        required = schema.get("required", [])
        for name in required:
            if name not in instance:
                errors.append(f"{location}: missing required property {name!r}")
        properties = schema.get("properties", {})
        if isinstance(properties, dict):
            for name, value in instance.items():
                if name in properties:
                    errors.extend(
                        validate_instance(
                            value,
                            properties[name],
                            schema_set,
                            document,
                            instance_path + (name,),
                        )
                    )
                elif schema.get("additionalProperties") is False:
                    errors.append(f"{location}: unexpected property {name!r}")
                elif isinstance(schema.get("additionalProperties"), dict):
                    errors.extend(
                        validate_instance(
                            value,
                            schema["additionalProperties"],
                            schema_set,
                            document,
                            instance_path + (name,),
                        )
                    )
    return errors


def is_within_repository(path: Path, repository_root: Path = ROOT) -> bool:
    try:
        path.resolve().relative_to(repository_root.resolve())
        return True
    except (OSError, ValueError):
        return False


def ensure_safe_path_components(path: Path, repository_root: Path = ROOT) -> Path:
    """Resolve containment and reject symlink components before traversal/read."""

    root = repository_root.resolve()
    lexical = Path(os.path.abspath(path))
    try:
        relative = lexical.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"{path}: path escapes the repository") from exc
    cursor = root
    for part in relative.parts:
        cursor = cursor / part
        if cursor.is_symlink():
            raise ValueError(f"{cursor}: symbolic links are not permitted")
    try:
        lexical.resolve().relative_to(root)
    except (OSError, ValueError) as exc:
        raise ValueError(f"{path}: resolved path escapes the repository") from exc
    return lexical


def expand_paths(
    paths: Iterable[Path],
    repository_root: Path = ROOT,
) -> list[Path]:
    """Expand record paths without following links and within fixed resource caps."""

    expanded: set[Path] = set()
    visited_directories: set[Path] = set()
    total_bytes = 0
    walk_entries = 0
    root = repository_root.resolve()

    def add_file(path: Path) -> None:
        nonlocal total_bytes
        safe = ensure_safe_path_components(path, root)
        if safe in expanded:
            return
        if safe.suffix.lower() == ".json" and safe.exists():
            try:
                size = safe.stat().st_size
            except OSError as exc:
                raise ValueError(f"{safe}: cannot inspect record file: {exc}") from exc
            if size > MAX_JSON_FILE_BYTES:
                raise ValueError(
                    f"{safe}: JSON file is {size} bytes; limit is {MAX_JSON_FILE_BYTES}"
                )
            total_bytes += size
            if total_bytes > MAX_TOTAL_JSON_BYTES:
                raise ValueError(
                    f"record collection exceeds {MAX_TOTAL_JSON_BYTES} total JSON bytes"
                )
        expanded.add(safe)
        if len(expanded) > MAX_INSTANCE_FILES:
            raise ValueError(
                f"record collection exceeds {MAX_INSTANCE_FILES} files"
            )

    for supplied in paths:
        path = ensure_safe_path_components(Path(supplied), root)
        if path.is_symlink():
            raise ValueError(f"{path}: symbolic links are not permitted")
        if not path.exists() or not path.is_dir():
            add_file(path)
            continue

        base_depth = len(path.relative_to(root).parts)
        stack: list[Path] = [path]
        while stack:
            directory = stack.pop()
            if directory in visited_directories:
                continue
            visited_directories.add(directory)
            depth = len(directory.relative_to(root).parts) - base_depth
            if depth > MAX_DIRECTORY_DEPTH:
                raise ValueError(
                    f"{directory}: directory depth exceeds {MAX_DIRECTORY_DEPTH}"
                )
            try:
                with os.scandir(directory) as iterator:
                    entries = sorted(iterator, key=lambda entry: entry.name)
            except OSError as exc:
                raise ValueError(f"{directory}: cannot traverse directory: {exc}") from exc
            for entry in entries:
                walk_entries += 1
                if walk_entries > MAX_WALK_ENTRIES:
                    raise ValueError(
                        f"directory traversal exceeds {MAX_WALK_ENTRIES} entries"
                    )
                child = Path(entry.path)
                if entry.is_symlink():
                    raise ValueError(f"{child}: symbolic links are not permitted")
                ensure_safe_path_components(child, root)
                if entry.is_dir(follow_symlinks=False):
                    stack.append(child)
                elif entry.is_file(follow_symlinks=False) and child.suffix.lower() == ".json":
                    add_file(child)
    return sorted(expanded)


def discover_instances(root: Path = ROOT) -> list[Path]:
    candidates = [root / name for name in DEFAULT_INSTANCE_DIRS if (root / name).exists()]
    return expand_paths(candidates, repository_root=root)


def discover_live_instances(root: Path = ROOT) -> list[Path]:
    """Discover only declared live record directories, never examples.

    This is the authoritative Day-1 collection boundary shared by command-line
    clients.  Calibration material under ``examples/**`` is intentionally
    excluded even when it is a complete, internally valid collection.
    """

    candidates = [root / name for name in LIVE_INSTANCE_DIRS if (root / name).exists()]
    return expand_paths(candidates, repository_root=root)


def is_live_instance_path(path: Path, root: Path = ROOT) -> bool:
    """Return whether *path* belongs to one of the declared live directories."""

    try:
        relative = path.resolve().relative_to(root.resolve())
    except (OSError, ValueError):
        return False
    return bool(relative.parts) and relative.parts[0] in LIVE_INSTANCE_DIRS


def validate_record_file(path: Path, schema_set: SchemaSet) -> list[str]:
    try:
        instance = load_json(path)
    except ValueError as exc:
        return [str(exc)]
    if not isinstance(instance, dict):
        return [f"{path}: record root must be an object"]
    record_type = instance.get("record_type")
    if not isinstance(record_type, str):
        return [f"{path}: missing string record_type"]
    document = schema_set.by_record_type.get(record_type)
    if document is None:
        return [f"{path}: unknown record_type {record_type!r}"]
    return [
        f"{path}: {error}"
        for error in validate_instance(instance, document.body, schema_set, document)
    ]


ID_FIELD_BY_TYPE = {
    "research_packet": "packet_id",
    "problem_record": "problem_id",
    "source_record": "source_id",
    "run_record": "run_id",
    "evidence_record": "artifact_id",
    "review_record": "review_id",
    "packet_transition": "transition_id",
}


@dataclass(frozen=True)
class LoadedRecord:
    path: Path
    body: dict[str, Any]

    @property
    def record_type(self) -> str:
        return str(self.body["record_type"])

    @property
    def record_id(self) -> str:
        return str(self.body[ID_FIELD_BY_TYPE[self.record_type]])

    @property
    def record_version(self) -> str:
        return str(self.body["record_version"])

    @property
    def exact_key(self) -> tuple[str, str, str]:
        """Return the immutable identity of this serialized record snapshot."""

        return (self.record_type, self.record_id, self.record_version)


EXECUTION_LIMIT_DEFAULTS: dict[str, Any] = {
    "allowed_output_paths": [],
    "acceptance_commands": [],
    "maximum_paid_spend": 0,
    "maximum_cpu_seconds": 0,
    "maximum_ram_bytes": 0,
    "maximum_gpu_seconds": 0,
    "maximum_storage_bytes": 0,
    "maximum_upload_bytes": 0,
}

ALLOWED_PACKET_TRANSITIONS: dict[str, set[str]] = {
    "draft": {"ready", "withdrawn"},
    "ready": {"claimed", "withdrawn", "closed"},
    "claimed": {"in_progress", "ready", "withdrawn"},
    "in_progress": {"blocked", "submitted", "withdrawn"},
    "blocked": {"in_progress", "ready", "withdrawn", "closed"},
    "submitted": {"under_review", "in_progress", "withdrawn"},
    "under_review": {
        "accepted",
        "rejected",
        "challenged",
        "in_progress",
        "submitted",
        "withdrawn",
    },
    "accepted": {"challenged", "superseded", "closed"},
    "rejected": {"in_progress", "superseded", "closed"},
    "challenged": {"under_review", "rejected", "withdrawn", "superseded", "closed"},
    "superseded": set(),
    "withdrawn": set(),
    "closed": set(),
}
TERMINAL_PACKET_STATUSES = {"superseded", "withdrawn", "closed"}


def packet_task_projection(body: dict[str, Any]) -> dict[str, Any]:
    """Return the task contract without lifecycle-only snapshot fields.

    A later snapshot may change version, status, lease, update time, and its
    continuation cursor without changing the mathematical task that runs,
    evidence, and reviews addressed.  Every other field remains part of the
    version-bound task contract.  This projection is deliberately structural;
    it never guesses equivalence from prose or semantic-version ordering.
    """

    projection = {
        key: value
        for key, value in body.items()
        if key not in {"record_version", "status", "lease", "updated_at"}
    }
    scope = projection.get("scope")
    if isinstance(scope, dict):
        projection["scope"] = {
            key: value for key, value in scope.items() if key != "continuation_cursor"
        }
    return projection

# A Day-1 live queue must contain current work, not merely a copied example or
# a completed/terminal archive.  ``known_result`` problems remain eligible:
# verification, translation, consolidation, and rediscovery are legitimate
# pilot work.  The published workflow-calibration identities and exact statement
# bytes are reserved so moving or renaming those fixtures cannot manufacture a
# live program accidentally.
LIVE_QUEUE_HEAD_STATUSES = {
    "ready",
    "claimed",
    "in_progress",
    "blocked",
    "submitted",
    "under_review",
    "rejected",
    "challenged",
}
PUBLISHED_CALIBRATION_PROJECT_IDS = {"MC-PILOT-CALIBRATION"}
PUBLISHED_CALIBRATION_PROBLEM_IDS = {"CAL-ODD-SUM-IDENTITY"}
PUBLISHED_CALIBRATION_PACKET_IDS = {"CAL-PACKET-001"}
PUBLISHED_CALIBRATION_STATEMENT_SHA256 = {
    "5e3f3e1061797bc11c343815c356deb5c1d1c882f1ad65f5eb59e39096a82241"
}


def effective_execution_limits(packet_body: dict[str, Any]) -> dict[str, Any]:
    """Return explicit packet limits or the fail-closed all-zero policy."""

    configured = packet_body.get("execution_limits")
    if not isinstance(configured, dict):
        return {
            key: list(value) if isinstance(value, list) else value
            for key, value in EXECUTION_LIMIT_DEFAULTS.items()
        }
    return {
        key: configured.get(
            key,
            list(default) if isinstance(default, list) else default,
        )
        for key, default in EXECUTION_LIMIT_DEFAULTS.items()
    }


def parse_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return None
    return parsed.astimezone(timezone.utc)


def sha256_file(path: Path) -> str:
    """Hash artifact bytes exactly as stored; no text normalization is applied."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_record_file(path: Path) -> str:
    """Hash a JSON record using the public UTF-8/LF serialization policy.

    Record references bind the complete serialized JSON, including key order and
    whitespace, but normalize CRLF and bare CR line endings to LF.  This keeps an
    otherwise byte-identical Git checkout stable across core.autocrlf settings.
    Artifact hashes remain exact-byte hashes through :func:`sha256_file`.
    """

    if path.is_symlink():
        raise ValueError(f"{path}: symbolic-link records cannot be hashed")
    payload = path.read_bytes()
    if len(payload) > MAX_JSON_FILE_BYTES:
        raise ValueError(
            f"{path}: JSON file is {len(payload)} bytes; limit is {MAX_JSON_FILE_BYTES}"
        )
    try:
        payload.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(f"{path}: record hashing requires UTF-8: {exc}") from exc
    normalized = payload.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(normalized).hexdigest()


def declared_sha256(hashes: Any, location: str, errors: list[str]) -> str | None:
    if not isinstance(hashes, list):
        errors.append(f"{location}: hashes must be an array")
        return None
    digests = [
        item.get("digest")
        for item in hashes
        if isinstance(item, dict) and item.get("algorithm") == "sha256"
    ]
    if len(digests) != 1 or not isinstance(digests[0], str):
        errors.append(f"{location}: expected exactly one declared sha256 digest")
        return None
    return digests[0]


def validate_collection(paths: Iterable[Path], schema_set: SchemaSet) -> list[str]:
    """Validate cross-record identities, refs, hashes, and artifact bytes."""

    errors: list[str] = []
    records: list[LoadedRecord] = []
    by_exact_key: dict[tuple[str, str, str], LoadedRecord] = {}
    versions_by_stable_id: dict[tuple[str, str], list[LoadedRecord]] = {}
    for path in sorted(set(paths)):
        if not path.is_file() or path.suffix.lower() != ".json":
            continue
        try:
            body = load_json(path)
        except ValueError:
            continue
        if not isinstance(body, dict):
            continue
        record_type = body.get("record_type")
        id_field = ID_FIELD_BY_TYPE.get(record_type)
        if id_field is None or not isinstance(body.get(id_field), str):
            continue
        record = LoadedRecord(path=path, body=body)
        key = record.exact_key
        if key in by_exact_key:
            errors.append(
                f"{path}: duplicate exact record identity {key!r}; "
                f"first declared in {by_exact_key[key].path}"
            )
        else:
            by_exact_key[key] = record
            versions_by_stable_id.setdefault(
                (record.record_type, record.record_id), []
            ).append(record)
        records.append(record)

    def check_record_reference(
        owner: LoadedRecord,
        reference: Any,
        expected_type: str | None,
        id_field: str,
        location: str,
    ) -> LoadedRecord | None:
        if not isinstance(reference, dict):
            return None
        target_type = expected_type or reference.get("record_type")
        target_id = reference.get(id_field)
        target_version = reference.get("record_version")
        if (
            not isinstance(target_type, str)
            or not isinstance(target_id, str)
            or not isinstance(target_version, str)
        ):
            return None
        target = by_exact_key.get((target_type, target_id, target_version))
        label = f"{owner.path}: {location}"
        if target is None:
            errors.append(
                f"{label}: unresolved {target_type} reference {target_id!r} at "
                f"exact record_version {target_version!r}"
            )
            return None
        expected_digest = declared_sha256(reference.get("hashes"), label, errors)
        if expected_digest is not None:
            try:
                actual_digest = sha256_record_file(target.path)
            except (OSError, ValueError) as exc:
                errors.append(f"{label}: cannot hash target record: {exc}")
            else:
                if expected_digest != actual_digest:
                    errors.append(
                        f"{label}: normalized-record sha256 mismatch for {target.path}; "
                        f"declared {expected_digest}, actual {actual_digest}"
                    )
        return target

    packets = [record for record in records if record.record_type == "research_packet"]
    problems = [record for record in records if record.record_type == "problem_record"]
    sources = [record for record in records if record.record_type == "source_record"]
    runs = [record for record in records if record.record_type == "run_record"]
    evidence_records = [
        record for record in records if record.record_type == "evidence_record"
    ]
    reviews = [record for record in records if record.record_type == "review_record"]
    transitions = [
        record for record in records if record.record_type == "packet_transition"
    ]
    evidence_by_identity: dict[tuple[str, str], LoadedRecord] = {
        (record.record_id, record.record_version): record for record in evidence_records
    }
    packet_sources: dict[tuple[str, str, str], dict[str, LoadedRecord]] = {}
    run_packets: dict[tuple[str, str, str], LoadedRecord] = {}
    evidence_packets: dict[tuple[str, str, str], LoadedRecord] = {}
    evidence_runs: dict[tuple[str, str, str], LoadedRecord] = {}
    review_subjects: dict[tuple[str, str, str], LoadedRecord] = {}
    review_runs: dict[tuple[str, str, str], list[LoadedRecord]] = {}
    review_evidence: dict[tuple[str, str, str], list[LoadedRecord]] = {}
    accepting_review_packets: dict[tuple[str, str, str], LoadedRecord] = {}
    transition_from_packets: dict[tuple[str, str, str], LoadedRecord] = {}
    transition_to_packets: dict[tuple[str, str, str], LoadedRecord] = {}
    transition_evidence: dict[tuple[str, str, str], list[LoadedRecord]] = {}
    transition_reviews: dict[tuple[str, str, str], list[LoadedRecord]] = {}
    problem_predecessors: dict[tuple[str, str, str], LoadedRecord] = {}
    for packet in packets:
        resolved: dict[str, LoadedRecord] = {}
        for reference in packet.body.get("source_inputs", []):
            if not isinstance(reference, dict):
                continue
            source_id = reference.get("source_record_id")
            source_version = reference.get("record_version")
            if isinstance(source_id, str) and isinstance(source_version, str):
                source = by_exact_key.get(
                    ("source_record", source_id, source_version)
                )
                if source is not None:
                    resolved[source_id] = source
        packet_sources[packet.exact_key] = resolved
    for run in runs:
        reference = run.body.get("packet_ref", {})
        if isinstance(reference, dict):
            target = by_exact_key.get(
                (
                    "research_packet",
                    reference.get("packet_id"),
                    reference.get("record_version"),
                )
            )
            if target is not None:
                run_packets[run.exact_key] = target
    for evidence in evidence_records:
        packet_reference = evidence.body.get("packet_ref", {})
        run_reference = evidence.body.get("run_ref", {})
        if isinstance(packet_reference, dict):
            target = by_exact_key.get(
                (
                    "research_packet",
                    packet_reference.get("packet_id"),
                    packet_reference.get("record_version"),
                )
            )
            if target is not None:
                evidence_packets[evidence.exact_key] = target
        if isinstance(run_reference, dict):
            target = by_exact_key.get(
                (
                    "run_record",
                    run_reference.get("run_id"),
                    run_reference.get("record_version"),
                )
            )
            if target is not None:
                evidence_runs[evidence.exact_key] = target
    for review in reviews:
        subject = review.body.get("reviewed_subject", {})
        if isinstance(subject, dict):
            target_type = subject.get("record_type")
            target_id = subject.get("record_id")
            target_version = subject.get("record_version")
            if all(isinstance(value, str) for value in (target_type, target_id, target_version)):
                target = by_exact_key.get((target_type, target_id, target_version))
                if target is not None:
                    review_subjects[review.exact_key] = target
        resolved_runs: list[LoadedRecord] = []
        for reference in review.body.get("review_run_refs", []):
            if not isinstance(reference, dict):
                continue
            target = by_exact_key.get(
                (
                    "run_record",
                    reference.get("run_id"),
                    reference.get("record_version"),
                )
            )
            if target is not None:
                resolved_runs.append(target)
        review_runs[review.exact_key] = resolved_runs

    def require_release_ready(record: LoadedRecord, context: str) -> None:
        boundary = record.body.get("submission_boundary", {})
        rights = record.body.get("submission_rights", {})
        limitations = record.body.get("limitations", {})
        if boundary.get("redaction_status") != "passed":
            errors.append(f"{record.path}: {context} requires redaction_status 'passed'")
        if boundary.get("publication_preview_status") != "approved":
            errors.append(
                f"{record.path}: {context} requires publication_preview_status 'approved'"
            )
        if rights.get("redistribution_status") != "permitted":
            errors.append(
                f"{record.path}: {context} with checked-in public record/artifact "
                "bytes requires permitted redistribution; metadata_only is insufficient"
            )
        if limitations.get("status") == "not_assessed":
            errors.append(f"{record.path}: {context} requires assessed limitations")

    def require_acceptance_eligible_evidence(
        evidence: LoadedRecord,
        packet: LoadedRecord | None,
        run: LoadedRecord | None,
    ) -> None:
        """Apply evidence quality gates only when a transition accepts it.

        Producer evidence is an immutable ``complete`` object in commit A.  The
        independent review and acceptance transition in commit B confer network
        acceptance; the evidence record never predeclares its own acceptance.
        """

        body = evidence.body
        if body.get("status") != "complete":
            errors.append(
                f"{evidence.path}: transition-accepted evidence must have producer "
                "status 'complete', not a self-declared acceptance status"
            )
        require_release_ready(evidence, "transition acceptance of evidence")
        nonpassing = [
            check.get("status")
            for check in body.get("checks", [])
            if check.get("status") != "passed"
        ]
        if nonpassing:
            errors.append(
                f"{evidence.path}: transition-accepted evidence has non-passing "
                f"checks: {nonpassing}"
            )
        formalization = body.get("formalization", {})
        if formalization.get("placeholder_status") in {"unknown", "present"}:
            errors.append(
                f"{evidence.path}: transition-accepted evidence cannot have "
                "unknown or present formal placeholders"
            )
        if formalization.get("formal_status") == "failed":
            errors.append(
                f"{evidence.path}: transition-accepted evidence cannot have failed "
                "formal status"
            )
        if formalization.get("statement_correspondence_status") == "failed":
            errors.append(
                f"{evidence.path}: transition-accepted evidence cannot have failed "
                "statement correspondence"
            )
        if body.get("reproducibility", {}).get("clean_environment_status") == "failed":
            errors.append(
                f"{evidence.path}: transition-accepted evidence cannot have failed "
                "clean-environment reproduction"
            )
        if run is None or run.body.get("status") != "completed":
            errors.append(
                f"{evidence.path}: transition-accepted evidence requires a completed "
                "producing run"
            )
        if packet is not None:
            plan = packet.body.get("formalization_plan", {})
            if formalization.get("artifact_role") == "formalization" and formalization.get(
                "formal_status"
            ) not in {"compiles", "no_placeholders"}:
                errors.append(
                    f"{evidence.path}: transition-accepted formalization must compile"
                )
            if plan.get("expectation") == "complete" and formalization.get(
                "formal_status"
            ) != "no_placeholders":
                errors.append(
                    f"{evidence.path}: complete formalization plan requires "
                    "no_placeholders status"
                )
            if plan.get("statement_correspondence_review") == "required" and formalization.get(
                "statement_correspondence_status"
            ) != "passed":
                errors.append(
                    f"{evidence.path}: required statement correspondence has not passed"
                )

    def require_submission_alignment(record: LoadedRecord) -> None:
        boundary = record.body.get("submission_boundary", {})
        rights = record.body.get("submission_rights", {})
        allowlisted = set(boundary.get("allowlisted_artifact_ids", []))
        submitted = set(rights.get("submitted_component_ids", []))
        if record.record_id not in submitted:
            errors.append(
                f"{record.path}: $.submission_rights.submitted_component_ids must "
                f"include this record id {record.record_id!r}"
            )
        undeclared = submitted - ({record.record_id} | allowlisted)
        if undeclared:
            errors.append(
                f"{record.path}: submitted component ids are outside the record's "
                f"public artifact allowlist: {sorted(undeclared)}"
            )
        for source_id in rights.get("third_party_source_ids", []):
            if ("source_record", source_id) not in versions_by_stable_id:
                errors.append(
                    f"{record.path}: $.submission_rights.third_party_source_ids "
                    f"contains unresolved source {source_id!r}"
                )

    def check_timestamp_order(
        record: LoadedRecord,
        earlier_field: str,
        later_field: str,
    ) -> None:
        earlier = parse_timestamp(record.body.get(earlier_field))
        later = parse_timestamp(record.body.get(later_field))
        if earlier is not None and later is not None and later < earlier:
            errors.append(
                f"{record.path}: $.{later_field} precedes $.{earlier_field}"
            )

    use_permission_field = {
        "inspect": "copying",
        "quote_lawful_excerpt": "copying",
        "extract_facts": "extraction",
        "compute": "extraction",
        "translate": "translation",
        "redistribute": "redistribution",
        "model_training": "model_training",
    }

    def check_requested_source_uses(
        packet: LoadedRecord,
        source_input: dict[str, Any],
        source: LoadedRecord,
        location: str,
    ) -> None:
        assessment = source.body.get("rights_assessment", {})
        aggregate = assessment.get("permissions", {})
        components = {
            component.get("component_id"): component
            for component in source.body.get("third_party_components", [])
            if isinstance(component, dict)
            and isinstance(component.get("component_id"), str)
        }
        selected_ids = source_input.get("component_ids")
        if selected_ids is None:
            selected = list(components.values())
        else:
            selected = []
            for component_id in selected_ids:
                component = components.get(component_id)
                if component is None:
                    errors.append(
                        f"{packet.path}: {location}.component_ids contains unknown "
                        f"source component {component_id!r}"
                    )
                else:
                    selected.append(component)
        for requested_use in source_input.get("permitted_uses", []):
            permission_field = use_permission_field.get(requested_use)
            if permission_field is None:
                continue
            if aggregate.get(permission_field) != "permitted":
                errors.append(
                    f"{packet.path}: {location}.permitted_uses requests "
                    f"{requested_use!r}, but source {source.record_id!r} does not "
                    f"grant {permission_field} permission"
                )
            if requested_use == "redistribute" and assessment.get(
                "redistribution_status"
            ) != "permitted":
                errors.append(
                    f"{packet.path}: {location}.permitted_uses requests redistribution, "
                    f"but source {source.record_id!r} is not redistributable"
                )
            for component in selected:
                component_id = component.get("component_id")
                if component.get("permissions", {}).get(permission_field) != "permitted":
                    errors.append(
                        f"{packet.path}: {location}.permitted_uses requests "
                        f"{requested_use!r}, but component {component_id!r} does not "
                        f"grant {permission_field} permission"
                    )
                if requested_use == "redistribute" and component.get(
                    "redistribution_status"
                ) != "permitted":
                    errors.append(
                        f"{packet.path}: component {component_id!r} is not "
                        "redistributable"
                    )

    def check_exact_repository_artifact(
        owner: LoadedRecord,
        declaration: Any,
        location: str,
    ) -> Path | None:
        """Verify one declared repository artifact against exact stored bytes."""

        if not isinstance(declaration, dict):
            return None
        artifact_path = declaration.get("artifact_path")
        if not isinstance(artifact_path, str):
            return None
        try:
            resolved = ensure_safe_path_components(ROOT / artifact_path, ROOT)
        except ValueError as exc:
            errors.append(f"{owner.path}: {location}.artifact_path is unsafe: {exc}")
            return None
        if not resolved.is_file():
            errors.append(
                f"{owner.path}: {location}.artifact_path does not exist: {artifact_path}"
            )
            return None
        try:
            artifact_size = resolved.stat().st_size
        except OSError as exc:
            errors.append(f"{owner.path}: {location}: cannot inspect artifact: {exc}")
            return None
        if artifact_size > MAX_ARTIFACT_BYTES:
            errors.append(
                f"{owner.path}: {location}: artifact exceeds {MAX_ARTIFACT_BYTES} bytes"
            )
            return None
        if declaration.get("byte_size") != artifact_size:
            errors.append(f"{owner.path}: {location}.byte_size does not match artifact")
        digest = declared_sha256(
            declaration.get("hashes"), f"{owner.path}: {location}.hashes", errors
        )
        if digest is not None:
            try:
                actual_digest = sha256_file(resolved)
            except OSError as exc:
                errors.append(f"{owner.path}: {location}: cannot hash artifact: {exc}")
            else:
                if digest != actual_digest:
                    errors.append(
                        f"{owner.path}: {location}.hashes does not match exact artifact bytes"
                    )
        return resolved

    def check_artifact_reference(
        owner: LoadedRecord,
        reference: Any,
        location: str,
        required_in_collection: bool = True,
    ) -> LoadedRecord | None:
        if not isinstance(reference, dict) or not isinstance(
            reference.get("artifact_id"), str
        ):
            return None
        artifact_id = reference["artifact_id"]
        artifact_version = reference.get("record_version")
        target = evidence_by_identity.get((artifact_id, artifact_version))
        label = f"{owner.path}: {location}"
        if target is None:
            if required_in_collection:
                errors.append(
                    f"{label}: unresolved exact evidence artifact {artifact_id!r} "
                    f"version {artifact_version!r}"
                )
            return None
        expected_digest = declared_sha256(reference.get("hashes"), label, errors)
        actual_digest = declared_sha256(
            target.body.get("hashes"), f"{target.path}: $.hashes", errors
        )
        if expected_digest is not None and actual_digest is not None:
            if expected_digest != actual_digest:
                errors.append(f"{label}: artifact digest does not match evidence record")
        return target

    def artifact_reference_exactly_matches_evidence(
        reference: Any,
        evidence: LoadedRecord,
    ) -> bool:
        """Return whether a run artifact ref binds one exact evidence artifact."""

        if not isinstance(reference, dict):
            return False
        if reference.get("artifact_id") != evidence.record_id:
            return False
        if reference.get("record_version") != evidence.record_version:
            return False
        expected = [
            item.get("digest")
            for item in evidence.body.get("hashes", [])
            if isinstance(item, dict) and item.get("algorithm") == "sha256"
        ]
        observed = [
            item.get("digest")
            for item in reference.get("hashes", [])
            if isinstance(item, dict) and item.get("algorithm") == "sha256"
        ]
        return len(expected) == 1 and observed == expected

    for record in records:
        body = record.body
        require_submission_alignment(record)
        if "created_at" in body and "updated_at" in body:
            check_timestamp_order(record, "created_at", "updated_at")
        if record.record_type == "run_record":
            check_timestamp_order(record, "started_at", "recorded_at")

        if record.record_type == "problem_record":
            previous_reference = body.get("previous_problem_ref")
            if isinstance(previous_reference, dict):
                predecessor = check_record_reference(
                    record,
                    previous_reference,
                    "problem_record",
                    "problem_id",
                    "$.previous_problem_ref",
                )
                if predecessor is not None:
                    problem_predecessors[record.exact_key] = predecessor
                    if predecessor.record_id != record.record_id:
                        errors.append(
                            f"{record.path}: previous_problem_ref must preserve the "
                            "stable problem_id"
                        )
                    predecessor_updated = parse_timestamp(
                        predecessor.body.get("updated_at")
                    )
                    current_updated = parse_timestamp(body.get("updated_at"))
                    if (
                        predecessor_updated is not None
                        and current_updated is not None
                        and current_updated <= predecessor_updated
                    ):
                        errors.append(
                            f"{record.path}: problem successor updated_at must be "
                            "strictly later than its exact predecessor"
                        )
            statement = body.get("statement", {})
            check_exact_repository_artifact(record, statement, "$.statement")
            if body.get("submission_rights", {}).get(
                "redistribution_status"
            ) != "permitted":
                errors.append(
                    f"{record.path}: checked-in canonical problem statement bytes "
                    "require permitted redistribution"
                )
            statement_id = statement.get("artifact_id")
            boundary_ids = set(
                body.get("submission_boundary", {}).get(
                    "allowlisted_artifact_ids", []
                )
            )
            submitted_ids = set(
                body.get("submission_rights", {}).get(
                    "submitted_component_ids", []
                )
            )
            if statement_id not in boundary_ids:
                errors.append(
                    f"{record.path}: exact statement artifact {statement_id!r} is "
                    "absent from the public artifact allowlist"
                )
            if statement_id not in submitted_ids:
                errors.append(
                    f"{record.path}: exact statement artifact {statement_id!r} is "
                    "absent from submitted Commons components"
                )

            resolved_sources: dict[str, LoadedRecord] = {}
            for index, reference in enumerate(body.get("source_refs", [])):
                source = check_record_reference(
                    record,
                    reference,
                    "source_record",
                    "source_record_id",
                    f"$.source_refs[{index}]",
                )
                if source is None:
                    continue
                if source.record_id in resolved_sources:
                    errors.append(
                        f"{record.path}: duplicate source_ref for {source.record_id!r}"
                    )
                resolved_sources[source.record_id] = source
                check_requested_source_uses(
                    record,
                    reference,
                    source,
                    f"$.source_refs[{index}]",
                )

            source_ids = set(resolved_sources)
            current_status = body.get("current_status", {})
            basis_ids = set(current_status.get("basis_source_ids", []))
            missing_basis = basis_ids - source_ids
            if missing_basis:
                errors.append(
                    f"{record.path}: current-status assessment has unresolved or "
                    f"unbound basis sources: {sorted(missing_basis)}"
                )
            for source_id in sorted(basis_ids & source_ids):
                source = resolved_sources[source_id]
                if source.body.get("status") != "verified" or source.body.get(
                    "verification_status"
                ) != "independently_checked":
                    errors.append(
                        f"{record.path}: current-status basis source {source_id!r} "
                        "is not verified and checked"
                    )

            linked_provenance_sources: set[str] = set()
            provenance_ids: list[Any] = []
            for index, entry in enumerate(body.get("provenance", [])):
                provenance_ids.append(entry.get("entry_id"))
                entry_sources = set(entry.get("source_record_ids", []))
                linked_provenance_sources.update(entry_sources)
                missing = entry_sources - source_ids
                if missing:
                    errors.append(
                        f"{record.path}: $.provenance[{index}] has unresolved or "
                        f"unbound sources: {sorted(missing)}"
                    )
            if len(provenance_ids) != len(set(provenance_ids)):
                errors.append(f"{record.path}: $.provenance contains duplicate entry_id values")
            if not linked_provenance_sources:
                errors.append(f"{record.path}: provenance must link at least one source record")

            definitions = body.get("definitions_and_conventions", {})
            for collection_name in ("definitions", "conventions"):
                for index, entry in enumerate(definitions.get(collection_name, [])):
                    missing = set(entry.get("source_record_ids", [])) - source_ids
                    if missing:
                        errors.append(
                            f"{record.path}: $.definitions_and_conventions."
                            f"{collection_name}[{index}] has unresolved or unbound "
                            f"sources: {sorted(missing)}"
                        )

            declared_third_party = set(
                body.get("submission_rights", {}).get("third_party_source_ids", [])
            )
            missing_rights_sources = source_ids - declared_third_party
            if missing_rights_sources:
                errors.append(
                    f"{record.path}: problem sources missing from "
                    "$.submission_rights.third_party_source_ids: "
                    f"{sorted(missing_rights_sources)}"
                )

            assessment = current_status.get("assessment")
            verification = current_status.get("independent_verification_status")
            if assessment in {"solved", "disproved", "known_result"} and verification != "verified":
                errors.append(
                    f"{record.path}: status {assessment!r} requires independently "
                    "verified status evidence"
                )
            kind = body.get("kind")
            if kind == "known_result" and assessment != "known_result":
                errors.append(
                    f"{record.path}: known_result kind requires known_result assessment"
                )
            if kind == "established_open_problem" and assessment not in {
                "open",
                "uncertain",
                "not_assessed",
            }:
                errors.append(
                    f"{record.path}: established_open_problem kind conflicts with "
                    f"assessment {assessment!r}"
                )
            if assessment != "not_assessed" and body.get("limitations", {}).get(
                "status"
            ) == "not_assessed":
                errors.append(
                    f"{record.path}: qualified current status requires assessed limitations"
                )
            assessed_at = parse_timestamp(current_status.get("assessed_at"))
            updated_at = parse_timestamp(body.get("updated_at"))
            if assessed_at is not None and updated_at is not None and assessed_at > updated_at:
                errors.append(
                    f"{record.path}: current-status assessment is later than updated_at"
                )

        elif record.record_type == "source_record":
            assessment = body.get("rights_assessment", {})
            aggregate_permissions = assessment.get("permissions", {})
            aggregate_redistribution = assessment.get("redistribution_status")
            locator = body.get("locator", {})
            canonical_reference = locator.get("canonical_reference")
            if locator.get("reference_kind") == "repository_artifact":
                if (
                    not isinstance(canonical_reference, str)
                    or urlparse(canonical_reference).scheme
                    or canonical_reference.startswith(("/", "\\"))
                    or "\\" in canonical_reference
                ):
                    errors.append(
                        f"{record.path}: repository_artifact canonical_reference "
                        "must be a canonical repository-relative slash path, not a URI"
                    )
                check_exact_repository_artifact(
                    record,
                    {
                        "artifact_path": canonical_reference,
                        "byte_size": body.get("integrity", {}).get("byte_size"),
                        "hashes": body.get("integrity", {}).get("hashes"),
                    },
                    "$.locator.canonical_reference",
                )
                if aggregate_redistribution != "permitted":
                    errors.append(
                        f"{record.path}: checked-in canonical source bytes require "
                        "$.rights_assessment.redistribution_status 'permitted'"
                    )
                if aggregate_permissions.get("redistribution") != "permitted":
                    errors.append(
                        f"{record.path}: checked-in canonical source bytes require "
                        "$.rights_assessment.permissions.redistribution 'permitted'"
                    )
                if body.get("submission_rights", {}).get(
                    "redistribution_status"
                ) != "permitted":
                    errors.append(
                        f"{record.path}: checked-in canonical source bytes require "
                        "$.submission_rights.redistribution_status 'permitted'"
                    )
                restricted_components = [
                    component.get("component_id")
                    for component in body.get("third_party_components", [])
                    if component.get("redistribution_status") != "permitted"
                    or component.get("permissions", {}).get("redistribution")
                    != "permitted"
                ]
                if restricted_components:
                    errors.append(
                        f"{record.path}: checked-in canonical source bytes include "
                        "components without permitted redistribution: "
                        f"{restricted_components}"
                    )
            elif locator.get("reference_kind") == "external_reference" and (
                not isinstance(canonical_reference, str)
                or not urlparse(canonical_reference).scheme
                or urlparse(canonical_reference).scheme.lower() == "file"
                or re.match(r"^[A-Za-z]:[\\/]", canonical_reference) is not None
            ):
                errors.append(
                    f"{record.path}: external_reference canonical_reference must be "
                    "a non-file URI; a repository-relative path must use "
                    "reference_kind 'repository_artifact'"
                )
            if (
                aggregate_redistribution == "permitted"
                and aggregate_permissions.get("redistribution") != "permitted"
            ):
                errors.append(
                    f"{record.path}: permitted aggregate redistribution conflicts "
                    "with $.rights_assessment.permissions.redistribution"
                )
            for index, component in enumerate(body.get("third_party_components", [])):
                if (
                    aggregate_redistribution == "permitted"
                    and component.get("redistribution_status") != "permitted"
                ):
                    errors.append(
                        f"{record.path}: $.third_party_components[{index}] prevents "
                        "aggregate redistribution from being marked permitted"
                    )
            submission_status = body.get("submission_rights", {}).get(
                "redistribution_status"
            )
            if (
                submission_status == "permitted"
                and aggregate_redistribution != "permitted"
            ):
                errors.append(
                    f"{record.path}: submitted source record cannot claim permitted "
                    "redistribution when its rights assessment does not"
                )

        elif record.record_type == "research_packet":
            subject_ids = set(body.get("subject_ids", []))
            exact_problem_dependencies: dict[str, LoadedRecord] = {}
            for index, reference in enumerate(body.get("dependencies", [])):
                target = check_record_reference(
                    record,
                    reference,
                    None,
                    "record_id",
                    f"$.dependencies[{index}]",
                )
                if (
                    target is not None
                    and reference.get("record_type") == "problem_record"
                ):
                    if target.record_id in exact_problem_dependencies:
                        errors.append(
                            f"{record.path}: duplicate exact problem dependency for "
                            f"{target.record_id!r}"
                        )
                    exact_problem_dependencies[target.record_id] = target
            for index, subject_id in enumerate(body.get("subject_ids", [])):
                problem = exact_problem_dependencies.get(subject_id)
                if ("problem_record", subject_id) not in versions_by_stable_id:
                    errors.append(
                        f"{record.path}: $.subject_ids[{index}] has unresolved "
                        f"problem_record subject {subject_id!r}"
                    )
                elif problem is not None and problem.body.get("project_id") != body.get(
                    "project_id"
                ):
                    errors.append(
                        f"{record.path}: subject {subject_id!r} belongs to project "
                        f"{problem.body.get('project_id')!r}, not {body.get('project_id')!r}"
                    )
                if subject_id not in exact_problem_dependencies:
                    errors.append(
                        f"{record.path}: subject {subject_id!r} lacks an exact "
                        "problem_record dependency with matching version and digest"
                    )
            extra_problem_dependencies = set(exact_problem_dependencies) - subject_ids
            if extra_problem_dependencies:
                errors.append(
                    f"{record.path}: exact problem dependencies are not declared as "
                    f"subjects: {sorted(extra_problem_dependencies)}"
                )
            resolved_sources: dict[str, LoadedRecord] = {}
            for index, reference in enumerate(body.get("source_inputs", [])):
                source = check_record_reference(
                    record,
                    reference,
                    "source_record",
                    "source_record_id",
                    f"$.source_inputs[{index}]",
                )
                if source is not None:
                    if source.record_id in resolved_sources:
                        errors.append(
                            f"{record.path}: duplicate source_input for "
                            f"{source.record_id!r}"
                        )
                    resolved_sources[source.record_id] = source
                    check_requested_source_uses(
                        record,
                        reference,
                        source,
                        f"$.source_inputs[{index}]",
                    )
                    if body.get("status") == "accepted" and (
                        source.body.get("status") != "verified"
                        or source.body.get("rights_assessment", {}).get(
                            "review_status"
                        )
                        != "reviewed"
                    ):
                        errors.append(
                            f"{record.path}: accepted packet requires verified, "
                            f"rights-reviewed source {source.record_id!r}"
                        )
            packet_sources[record.exact_key] = resolved_sources
            declared_third_party = set(
                body.get("submission_rights", {}).get("third_party_source_ids", [])
            )
            missing_source_rights = set(resolved_sources) - declared_third_party
            if missing_source_rights:
                errors.append(
                    f"{record.path}: source inputs missing from "
                    "$.submission_rights.third_party_source_ids: "
                    f"{sorted(missing_source_rights)}"
                )

            output_ids = [
                output.get("artifact_id") for output in body.get("outputs", [])
            ]
            if len(output_ids) != len(set(output_ids)):
                errors.append(f"{record.path}: $.outputs contains duplicate artifact_id values")
            packet_allowlist = set(
                body.get("submission_boundary", {}).get(
                    "allowlisted_artifact_ids", []
                )
            )
            missing_outputs = set(output_ids) - packet_allowlist
            if missing_outputs:
                errors.append(
                    f"{record.path}: packet outputs are absent from the public artifact "
                    f"allowlist: {sorted(missing_outputs)}"
                )

            criterion_ids = [
                criterion.get("criterion_id")
                for criterion in body.get("acceptance_criteria", [])
            ]
            if len(criterion_ids) != len(set(criterion_ids)):
                errors.append(
                    f"{record.path}: $.acceptance_criteria contains duplicate criterion_id values"
                )
            limits = effective_execution_limits(body)
            output_namespace = f"work/{record.record_id}/"
            for index, output_path in enumerate(limits["allowed_output_paths"]):
                if not isinstance(output_path, str) or not output_path.startswith(
                    output_namespace
                ):
                    errors.append(
                        f"{record.path}: $.execution_limits.allowed_output_paths"
                        f"[{index}] must be inside {output_namespace!r}"
                    )
            commands = limits["acceptance_commands"]
            command_ids = [command.get("command_id") for command in commands]
            if len(command_ids) != len(set(command_ids)):
                errors.append(
                    f"{record.path}: $.execution_limits.acceptance_commands contains "
                    "duplicate command_id values"
                )
            known_criteria = set(criterion_ids)
            commanded_criteria: set[str] = set()
            for index, command in enumerate(commands):
                cwd = command.get("cwd")
                if isinstance(cwd, str):
                    try:
                        command_cwd = ensure_safe_path_components(ROOT / cwd, ROOT)
                    except ValueError as exc:
                        errors.append(
                            f"{record.path}: $.execution_limits.acceptance_commands"
                            f"[{index}].cwd is unsafe: {exc}"
                        )
                    else:
                        if not command_cwd.is_dir():
                            errors.append(
                                f"{record.path}: $.execution_limits.acceptance_commands"
                                f"[{index}].cwd does not identify a repository directory"
                            )
                command_criteria = set(command.get("criterion_ids", []))
                unknown = command_criteria - known_criteria
                if unknown:
                    errors.append(
                        f"{record.path}: $.execution_limits.acceptance_commands[{index}] "
                        f"references unknown criteria: {sorted(unknown)}"
                    )
                commanded_criteria.update(command_criteria)
            command_methods = {"test_command", "exact_replay", "formal_compile"}
            missing_commands = {
                criterion.get("criterion_id")
                for criterion in body.get("acceptance_criteria", [])
                if criterion.get("mandatory")
                and criterion.get("verification_method") in command_methods
                and criterion.get("criterion_id") not in commanded_criteria
            }
            if body.get("execution_limits") is not None and missing_commands:
                errors.append(
                    f"{record.path}: mandatory command-based criteria lack an allowlisted "
                    f"acceptance command: {sorted(missing_commands)}"
                )

            lease = body.get("lease", {})
            lease_status = lease.get("status")
            compatible_packet_statuses = {
                "unclaimed": {"draft", "ready"},
                "claimed": {"claimed"},
                "active": {"claimed", "in_progress", "blocked"},
                "expired": {"ready", "blocked"},
                "released": {"ready", "blocked", "withdrawn"},
                "completed": {
                    "submitted",
                    "under_review",
                    "accepted",
                    "rejected",
                    "challenged",
                    "superseded",
                    "closed",
                },
                "cancelled": {"ready", "withdrawn", "closed"},
            }
            if body.get("status") not in compatible_packet_statuses.get(
                lease_status, set()
            ):
                errors.append(
                    f"{record.path}: packet status {body.get('status')!r} is "
                    f"incompatible with lease status {lease_status!r}"
                )
            claimed_at = parse_timestamp(lease.get("claimed_at"))
            expires_at = parse_timestamp(lease.get("expires_at"))
            if (
                claimed_at is not None
                and expires_at is not None
                and expires_at <= claimed_at
            ):
                errors.append(f"{record.path}: lease expires_at must follow claimed_at")
            if body.get("status") in {"claimed", "in_progress"} and body.get(
                "execution_limits"
            ) is None:
                errors.append(
                    f"{record.path}: operational packet requires explicit execution_limits; "
                    "omission means deny all execution"
                )
            if body.get("status") == "accepted":
                require_release_ready(record, "accepted packet status")

        elif record.record_type == "packet_transition":
            from_packet = check_record_reference(
                record,
                body.get("from_packet_ref"),
                "research_packet",
                "packet_id",
                "$.from_packet_ref",
            )
            to_packet = check_record_reference(
                record,
                body.get("to_packet_ref"),
                "research_packet",
                "packet_id",
                "$.to_packet_ref",
            )
            if from_packet is not None:
                transition_from_packets[record.exact_key] = from_packet
            if to_packet is not None:
                transition_to_packets[record.exact_key] = to_packet
            if from_packet is not None and to_packet is not None:
                if from_packet.record_id != to_packet.record_id:
                    errors.append(
                        f"{record.path}: from_packet_ref and to_packet_ref must keep "
                        "one stable packet_id"
                    )
                if from_packet.exact_key == to_packet.exact_key:
                    errors.append(
                        f"{record.path}: packet transition must create a distinct "
                        "to-packet snapshot"
                    )
                if body.get("from_status") != from_packet.body.get("status"):
                    errors.append(
                        f"{record.path}: from_status does not match from-packet "
                        "snapshot status"
                    )
                if body.get("to_status") != to_packet.body.get("status"):
                    errors.append(
                        f"{record.path}: to_status does not match to-packet "
                        "snapshot status"
                    )
                occurred_at = parse_timestamp(body.get("occurred_at"))
                from_updated_at = parse_timestamp(from_packet.body.get("updated_at"))
                to_updated_at = parse_timestamp(to_packet.body.get("updated_at"))
                if (
                    occurred_at is not None
                    and from_updated_at is not None
                    and occurred_at < from_updated_at
                ):
                    errors.append(
                        f"{record.path}: transition occurred_at precedes the "
                        "from-packet snapshot"
                    )
                if (
                    occurred_at is not None
                    and to_updated_at is not None
                    and occurred_at > to_updated_at
                ):
                    errors.append(
                        f"{record.path}: transition occurred_at follows the "
                        "to-packet snapshot"
                    )

            event_kind = body.get("event_kind")
            same_status = body.get("from_status") == body.get("to_status")
            if event_kind == "state_transition" and same_status:
                errors.append(
                    f"{record.path}: state_transition must change packet status"
                )
            if event_kind in {"record_revision", "lease_update"} and not same_status:
                errors.append(
                    f"{record.path}: {event_kind} must preserve packet status"
                )
            if event_kind == "record_revision" and body.get("from_status") in {
                "submitted",
                "under_review",
                "accepted",
                "rejected",
                "challenged",
                "superseded",
                "withdrawn",
                "closed",
            }:
                errors.append(
                    f"{record.path}: review-sensitive or terminal packet snapshots "
                    "cannot inherit acceptance through record_revision"
                )
            if event_kind == "lease_update" and body.get("from_status") not in {
                "ready",
                "claimed",
                "in_progress",
                "blocked",
            }:
                errors.append(
                    f"{record.path}: lease_update is only valid while a packet is "
                    "available or actively worked"
                )
            if from_packet is not None and to_packet is not None:
                allowed_top_level = {
                    "record_version",
                    "status",
                    "lease",
                    "updated_at",
                }
                from_lease = from_packet.body.get("lease", {})
                to_lease = to_packet.body.get("lease", {})
                from_generation = (
                    from_lease.get("generation")
                    if isinstance(from_lease, dict)
                    else None
                )
                to_generation = (
                    to_lease.get("generation")
                    if isinstance(to_lease, dict)
                    else None
                )
                if (
                    isinstance(from_generation, int)
                    and not isinstance(from_generation, bool)
                    and isinstance(to_generation, int)
                    and not isinstance(to_generation, bool)
                ):
                    if to_generation < from_generation:
                        errors.append(
                            f"{record.path}: packet transition cannot decrease lease "
                            "generation"
                        )
                    epoch_fields = (
                        "claimant_id",
                        "claimed_at",
                        "base_commit",
                        "branch_name",
                    )
                    epoch_changed = any(
                        from_lease.get(field) != to_lease.get(field)
                        for field in epoch_fields
                    )
                    if epoch_changed and to_generation <= from_generation:
                        errors.append(
                            f"{record.path}: a new claimant/claim basis lease epoch "
                            "must increment generation"
                        )

                def changed_outside_lifecycle_fields() -> list[str]:
                    changed: list[str] = []
                    for field in sorted(
                        set(from_packet.body) | set(to_packet.body)
                    ):
                        if field in allowed_top_level:
                            continue
                        if field == "scope" and event_kind == "state_transition":
                            from_scope = from_packet.body.get("scope", {})
                            to_scope = to_packet.body.get("scope", {})
                            if isinstance(from_scope, dict) and isinstance(to_scope, dict):
                                from_scope = {
                                    key: value
                                    for key, value in from_scope.items()
                                    if key != "continuation_cursor"
                                }
                                to_scope = {
                                    key: value
                                    for key, value in to_scope.items()
                                    if key != "continuation_cursor"
                                }
                                if from_scope != to_scope:
                                    changed.append(field)
                                continue
                        if from_packet.body.get(field) != to_packet.body.get(field):
                            changed.append(field)
                    return changed

                if event_kind in {"state_transition", "lease_update"}:
                    unexpected_changes = changed_outside_lifecycle_fields()
                    if unexpected_changes:
                        errors.append(
                            f"{record.path}: {event_kind} changes task-content fields "
                            f"outside its allowed diff class: {unexpected_changes}"
                        )
                if event_kind == "lease_update":
                    if from_lease == to_lease:
                        errors.append(
                            f"{record.path}: lease_update must change the lease snapshot"
                        )
                    if (
                        isinstance(from_generation, int)
                        and isinstance(to_generation, int)
                        and to_generation <= from_generation
                    ):
                        errors.append(
                            f"{record.path}: lease_update must strictly increment "
                            "lease generation"
                        )
                elif event_kind == "record_revision":
                    if from_packet.body.get("lease") != to_packet.body.get("lease"):
                        errors.append(
                            f"{record.path}: record_revision must preserve the lease; "
                            "use lease_update for lease changes"
                        )
                    if packet_task_projection(
                        from_packet.body
                    ) == packet_task_projection(to_packet.body):
                        errors.append(
                            f"{record.path}: record_revision must change the "
                            "version-bound task-content projection"
                        )
            git_commit = body.get("git_commit")
            if git_commit == "0" * 40:
                errors.append(
                    f"{record.path}: git_commit must identify a real state/basis commit, "
                    "not the all-zero sentinel"
                )

            resolved_evidence: list[LoadedRecord] = []
            for index, reference in enumerate(body.get("evidence_refs", [])):
                evidence = check_record_reference(
                    record,
                    reference,
                    "evidence_record",
                    "artifact_id",
                    f"$.evidence_refs[{index}]",
                )
                if evidence is not None:
                    resolved_evidence.append(evidence)
                    event_time = parse_timestamp(body.get("occurred_at"))
                    evidence_time = parse_timestamp(evidence.body.get("created_at"))
                    if (
                        event_time is not None
                        and evidence_time is not None
                        and evidence_time > event_time
                    ):
                        errors.append(
                            f"{record.path}: $.evidence_refs[{index}] did not exist "
                            "at transition time"
                        )
            transition_evidence[record.exact_key] = resolved_evidence

            resolved_reviews: list[LoadedRecord] = []
            for index, reference in enumerate(body.get("review_refs", [])):
                review = check_record_reference(
                    record,
                    reference,
                    "review_record",
                    "review_id",
                    f"$.review_refs[{index}]",
                )
                if review is not None:
                    resolved_reviews.append(review)
                    event_time = parse_timestamp(body.get("occurred_at"))
                    review_time = parse_timestamp(review.body.get("updated_at"))
                    if (
                        event_time is not None
                        and review_time is not None
                        and review_time > event_time
                    ):
                        errors.append(
                            f"{record.path}: $.review_refs[{index}] was not complete "
                            "at transition time"
                        )
            transition_reviews[record.exact_key] = resolved_reviews

            if (
                body.get("event_kind") == "state_transition"
                and body.get("from_status") != "accepted"
                and body.get("to_status") == "accepted"
            ):
                if not resolved_evidence:
                    errors.append(
                        f"{record.path}: transition into accepted status requires "
                        "exact evidence_refs"
                    )
                if not resolved_reviews:
                    errors.append(
                        f"{record.path}: transition into accepted status requires "
                        "exact review_refs"
                    )

            referenced_artifact_ids = {
                evidence.record_id for evidence in resolved_evidence
            }
            transition_allowlist = set(
                body.get("submission_boundary", {}).get(
                    "allowlisted_artifact_ids", []
                )
            )
            if not referenced_artifact_ids.issubset(transition_allowlist):
                errors.append(
                    f"{record.path}: transition evidence is outside its public "
                    f"allowlist: {sorted(referenced_artifact_ids - transition_allowlist)}"
                )

        elif record.record_type == "run_record":
            packet = check_record_reference(
                record, body.get("packet_ref"), "research_packet", "packet_id", "$.packet_ref"
            )
            if packet is not None:
                run_packets[record.exact_key] = packet
            bound_artifact_refs: list[dict[str, Any]] = []
            for index, reference in enumerate(body.get("input_artifacts", [])):
                if isinstance(reference, dict):
                    bound_artifact_refs.append(reference)
                check_artifact_reference(
                    record,
                    reference,
                    f"$.input_artifacts[{index}]",
                    required_in_collection=False,
                )
            run_output_ids: set[str] = set()
            for index, reference in enumerate(body.get("output_artifacts", [])):
                if isinstance(reference, dict):
                    bound_artifact_refs.append(reference)
                target = check_artifact_reference(
                    record, reference, f"$.output_artifacts[{index}]"
                )
                artifact_id = reference.get("artifact_id")
                if isinstance(artifact_id, str):
                    run_output_ids.add(artifact_id)
                if target is not None and target.body.get("run_ref", {}).get(
                    "run_id"
                ) != record.record_id:
                    errors.append(
                        f"{record.path}: $.output_artifacts[{index}] points to evidence "
                        "whose run_ref names another run"
                    )
            for check_index, check in enumerate(body.get("checks", [])):
                for ref_index, reference in enumerate(
                    check.get("evidence_artifact_refs", [])
                ):
                    check_artifact_reference(
                        record,
                        reference,
                        f"$.checks[{check_index}].evidence_artifact_refs[{ref_index}]",
                    )
                    if reference not in bound_artifact_refs:
                        errors.append(
                            f"{record.path}: $.checks[{check_index}]."
                            f"evidence_artifact_refs[{ref_index}] must exactly match "
                            "one run input_artifacts or output_artifacts reference"
                        )

            resources = body.get("resources", {})
            tools = body.get("tool_disclosures", [])
            any_network_used = False
            execution_categories = {
                "proof_assistant",
                "solver",
                "language_runtime",
            }
            disclosed_execution_tools: list[str] = []
            for tool_index, tool in enumerate(tools):
                network_used = tool.get("network_used")
                data_sent = tool.get("data_sent_categories", [])
                execution_location = tool.get("execution_location")
                if network_used is True:
                    any_network_used = True
                    if not data_sent or "none" in data_sent:
                        errors.append(
                            f"{record.path}: $.tool_disclosures[{tool_index}] with "
                            "network_used true must disclose non-'none' data categories"
                        )
                elif network_used is False and set(data_sent) - {"none"}:
                    errors.append(
                        f"{record.path}: $.tool_disclosures[{tool_index}] with "
                        "network_used false cannot declare sent data categories"
                    )
                if execution_location in {
                    "remote",
                    "local_client_remote_inference",
                    "hybrid",
                } and network_used is not True:
                    errors.append(
                        f"{record.path}: $.tool_disclosures[{tool_index}] remote or "
                        "hybrid execution requires network_used true"
                    )
                if tool.get("category") in execution_categories:
                    disclosed_execution_tools.append(str(tool.get("tool_id")))

            network_calls_status = resources.get("network_calls_status")
            if any_network_used and network_calls_status == "none":
                errors.append(
                    f"{record.path}: network_calls_status 'none' conflicts with a "
                    "tool disclosure that used the network"
                )
            if not any_network_used and network_calls_status == "bounded_and_disclosed":
                errors.append(
                    f"{record.path}: network_calls_status 'bounded_and_disclosed' "
                    "requires at least one tool with network_used true"
                )
            paid_spend = resources.get("paid_spend")
            monetary_status = resources.get("monetary_cost_status")
            if is_json_number(paid_spend) and paid_spend > 0 and monetary_status == "not_applicable":
                errors.append(
                    f"{record.path}: positive paid_spend conflicts with "
                    "monetary_cost_status 'not_applicable'"
                )
            boundary_allowlist = set(
                body.get("submission_boundary", {}).get(
                    "allowlisted_artifact_ids", []
                )
            )
            rights_components = set(
                body.get("submission_rights", {}).get("submitted_component_ids", [])
            )
            if not run_output_ids.issubset(boundary_allowlist):
                errors.append(
                    f"{record.path}: output artifacts are outside the run's public "
                    f"allowlist: {sorted(run_output_ids - boundary_allowlist)}"
                )
            if not run_output_ids.issubset(rights_components):
                errors.append(
                    f"{record.path}: output artifacts are absent from submitted components: "
                    f"{sorted(run_output_ids - rights_components)}"
                )
            if packet is not None:
                capability = packet.body.get("capability", {})
                if resources.get("resource_envelope") != capability.get("envelope"):
                    errors.append(
                        f"{record.path}: $.resources.resource_envelope must match "
                        "the bound packet capability envelope"
                    )
                elapsed = body.get("elapsed_seconds")
                maximum_hours = capability.get("maximum_hours")
                if (
                    is_json_number(elapsed)
                    and is_json_number(maximum_hours)
                    and elapsed > maximum_hours * 3600
                ):
                    errors.append(
                        f"{record.path}: elapsed_seconds exceeds the bound packet "
                        "capability maximum_hours"
                    )
                ended_statuses = {
                    "completed",
                    "partial",
                    "failed",
                    "aborted",
                    "superseded",
                }
                started_at = parse_timestamp(body.get("started_at"))
                recorded_at = parse_timestamp(body.get("recorded_at"))
                if (
                    body.get("status") in ended_statuses
                    and started_at is not None
                    and recorded_at is not None
                    and is_json_number(elapsed)
                    and elapsed > (recorded_at - started_at).total_seconds()
                ):
                    errors.append(
                        f"{record.path}: ended-run elapsed_seconds exceeds the "
                        "started_at-to-recorded_at interval"
                    )
                network_access = capability.get("network_access")
                if network_access == "none":
                    if any_network_used or network_calls_status != "none":
                        errors.append(
                            f"{record.path}: bound packet forbids network access but "
                            "the run reports network activity"
                        )
                    upload_bytes = resources.get("upload_bytes")
                    if is_json_number(upload_bytes) and upload_bytes != 0:
                        errors.append(
                            f"{record.path}: bound packet forbids network access but "
                            "$.resources.upload_bytes is nonzero"
                        )
                if (
                    network_access == "required"
                    and body.get("status") == "completed"
                    and not any_network_used
                ):
                    errors.append(
                        f"{record.path}: completed run for a packet requiring network "
                        "access discloses no network-using tool"
                    )
                if (
                    capability.get("code_execution") == "forbidden"
                    and disclosed_execution_tools
                ):
                    errors.append(
                        f"{record.path}: bound packet forbids code execution but the "
                        "run discloses execution tools: "
                        f"{sorted(disclosed_execution_tools)}"
                    )
                packet_output_ids = {
                    output.get("artifact_id")
                    for output in packet.body.get("outputs", [])
                }
                undeclared_outputs = run_output_ids - packet_output_ids
                if undeclared_outputs:
                    errors.append(
                        f"{record.path}: run outputs are not declared by packet "
                        f"{packet.record_id!r}: {sorted(undeclared_outputs)}"
                    )
                packet_source_ids = set(packet_sources.get(packet.exact_key, {}))
                run_source_ids = set(
                    body.get("submission_rights", {}).get(
                        "third_party_source_ids", []
                    )
                )
                if not packet_source_ids.issubset(run_source_ids):
                    errors.append(
                        f"{record.path}: run rights manifest omits packet sources: "
                        f"{sorted(packet_source_ids - run_source_ids)}"
                    )
                if run_output_ids and body.get("responsible_operator_id") != packet.body.get(
                    "lease", {}
                ).get("claimant_id"):
                    errors.append(
                        f"{record.path}: producing run operator does not match packet lease claimant"
                    )
                if packet.body.get("execution_limits") is not None:
                    limits = effective_execution_limits(packet.body)
                    usage_fields = {
                        "paid_spend": "maximum_paid_spend",
                        "cpu_seconds": "maximum_cpu_seconds",
                        "peak_ram_bytes": "maximum_ram_bytes",
                        "gpu_seconds": "maximum_gpu_seconds",
                        "storage_bytes": "maximum_storage_bytes",
                        "upload_bytes": "maximum_upload_bytes",
                    }
                    if body.get("status") in {
                        "completed",
                        "partial",
                        "failed",
                        "aborted",
                        "superseded",
                    }:
                        for usage_field, limit_field in usage_fields.items():
                            actual = resources.get(usage_field)
                            if not isinstance(actual, (int, float)) or isinstance(
                                actual, bool
                            ):
                                errors.append(
                                    f"{record.path}: completed/ended run under explicit "
                                    f"limits must report $.resources.{usage_field}"
                                )
                            elif actual > limits[limit_field]:
                                errors.append(
                                    f"{record.path}: $.resources.{usage_field} exceeds "
                                    f"packet {limit_field}"
                                )

        elif record.record_type == "evidence_record":
            packet = check_record_reference(
                record, body.get("packet_ref"), "research_packet", "packet_id", "$.packet_ref"
            )
            run = check_record_reference(
                record, body.get("run_ref"), "run_record", "run_id", "$.run_ref"
            )
            if packet is not None:
                evidence_packets[record.exact_key] = packet
            if run is not None:
                evidence_runs[record.exact_key] = run
            if (
                packet is not None
                and run is not None
                and run.body.get("packet_ref") != body.get("packet_ref")
            ):
                errors.append(
                    f"{record.path}: evidence packet_ref and producing run packet_ref "
                    "must bind the same exact lifecycle snapshot"
                )
            for source_id in body.get("source_record_ids", []):
                if ("source_record", source_id) not in versions_by_stable_id:
                    errors.append(
                        f"{record.path}: $.source_record_ids: unresolved source_record {source_id!r}"
                    )
            for index, reference in enumerate(body.get("dependency_artifacts", [])):
                check_artifact_reference(record, reference, f"$.dependency_artifacts[{index}]")
            artifact_path = body.get("artifact_path")
            if isinstance(artifact_path, str):
                try:
                    resolved = ensure_safe_path_components(ROOT / artifact_path, ROOT)
                except ValueError as exc:
                    errors.append(f"{record.path}: $.artifact_path is unsafe: {exc}")
                else:
                    if not resolved.is_file():
                        errors.append(
                            f"{record.path}: $.artifact_path does not exist: {artifact_path}"
                        )
                    else:
                        artifact_size = resolved.stat().st_size
                        if artifact_size > MAX_ARTIFACT_BYTES:
                            errors.append(
                                f"{record.path}: artifact exceeds {MAX_ARTIFACT_BYTES} bytes"
                            )
                        if body.get("byte_size") != artifact_size:
                            errors.append(f"{record.path}: $.byte_size does not match artifact")
                        digest = declared_sha256(
                            body.get("hashes"), f"{record.path}: $.hashes", errors
                        )
                        if digest is not None and digest != sha256_file(resolved):
                            errors.append(f"{record.path}: $.hashes does not match artifact bytes")
            if packet is not None:
                declared_outputs = {
                    output.get("artifact_id"): output
                    for output in packet.body.get("outputs", [])
                }
                output_declaration = declared_outputs.get(record.record_id)
                if output_declaration is None:
                    errors.append(
                        f"{record.path}: artifact_id is not declared by packet {packet.record_id}"
                    )
                else:
                    if output_declaration.get("kind") != body.get("evidence_kind"):
                        errors.append(
                            f"{record.path}: evidence_kind does not match packet output kind"
                        )
                    if output_declaration.get("media_type") != body.get("media_type"):
                        errors.append(
                            f"{record.path}: media_type does not match packet output declaration"
                        )
                packet_source_ids = set(packet_sources.get(packet.exact_key, {}))
                evidence_source_ids = set(body.get("source_record_ids", []))
                if not evidence_source_ids.issubset(packet_source_ids):
                    errors.append(
                        f"{record.path}: evidence cites sources outside its packet: "
                        f"{sorted(evidence_source_ids - packet_source_ids)}"
                    )
                rights_source_ids = set(
                    body.get("submission_rights", {}).get(
                        "third_party_source_ids", []
                    )
                )
                if not evidence_source_ids.issubset(rights_source_ids):
                    errors.append(
                        f"{record.path}: evidence rights manifest omits cited sources: "
                        f"{sorted(evidence_source_ids - rights_source_ids)}"
                    )
                if packet.body.get("execution_limits") is not None:
                    allowed_paths = set(
                        effective_execution_limits(packet.body)["allowed_output_paths"]
                    )
                    if body.get("artifact_path") not in allowed_paths:
                        errors.append(
                            f"{record.path}: artifact_path is outside packet execution "
                            "allowed_output_paths"
                        )
            if record.record_id not in set(
                body.get("submission_boundary", {}).get(
                    "allowlisted_artifact_ids", []
                )
            ):
                errors.append(
                    f"{record.path}: evidence artifact is absent from its own public allowlist"
                )
            if run is not None and record.record_id not in {
                reference.get("artifact_id")
                for reference in run.body.get("output_artifacts", [])
            }:
                errors.append(
                    f"{record.path}: producing run does not declare this evidence artifact as output"
                )
        elif record.record_type == "review_record":
            subject = body.get("reviewed_subject")
            subject_target = check_record_reference(
                record, subject, None, "record_id", "$.reviewed_subject"
            )
            if subject_target is not None:
                review_subjects[record.exact_key] = subject_target
                declared_path = subject.get("artifact_path")
                try:
                    target_relative = subject_target.path.resolve().relative_to(
                        ROOT.resolve()
                    ).as_posix()
                except ValueError:
                    target_relative = None
                if target_relative is not None and declared_path != target_relative:
                    errors.append(
                        f"{record.path}: $.reviewed_subject.artifact_path does not "
                        "identify the exact reviewed record file"
                    )
            resolved_review_runs: list[LoadedRecord] = []
            for index, reference in enumerate(body.get("review_run_refs", [])):
                review_run = check_record_reference(
                    record,
                    reference,
                    "run_record",
                    "run_id",
                    f"$.review_run_refs[{index}]",
                )
                if review_run is not None:
                    resolved_review_runs.append(review_run)
                    if review_run.body.get("responsible_operator_id") != body.get(
                        "responsible_reviewer_id"
                    ):
                        errors.append(
                            f"{record.path}: review run operator does not match responsible reviewer"
                        )
                    if review_run.body.get("status") != "completed":
                        errors.append(
                            f"{record.path}: completed review requires completed review runs"
                        )
            review_runs[record.exact_key] = resolved_review_runs
            resolved_review_evidence: list[LoadedRecord] = []
            exact_evidence_by_stable_id: dict[str, LoadedRecord] = {}

            def resolve_review_evidence_refs(
                collection_name: str,
                entries: list[Any],
            ) -> None:
                for entry_index, entry in enumerate(entries):
                    if not isinstance(entry, dict):
                        continue
                    for ref_index, reference in enumerate(
                        entry.get("evidence_refs", [])
                    ):
                        evidence = check_record_reference(
                            record,
                            reference,
                            "evidence_record",
                            "artifact_id",
                            f"$.{collection_name}[{entry_index}]."
                            f"evidence_refs[{ref_index}]",
                        )
                        if evidence is None:
                            continue
                        previous = exact_evidence_by_stable_id.get(evidence.record_id)
                        if previous is not None and previous.exact_key != evidence.exact_key:
                            errors.append(
                                f"{record.path}: {collection_name} cites multiple exact "
                                f"versions of evidence artifact {evidence.record_id!r}"
                            )
                        else:
                            exact_evidence_by_stable_id[evidence.record_id] = evidence
                        if (
                            subject_target is not None
                            and subject_target.record_type == "evidence_record"
                            and subject_target.record_id == evidence.record_id
                            and subject_target.exact_key != evidence.exact_key
                        ):
                            errors.append(
                                f"{record.path}: evidence_refs for the reviewed evidence "
                                "stable ID must bind the exact reviewed_subject version"
                            )
                        resolved_review_evidence.append(evidence)

            resolve_review_evidence_refs(
                "acceptance_results", body.get("acceptance_results", [])
            )
            resolve_review_evidence_refs("findings", body.get("findings", []))
            review_evidence[record.exact_key] = resolved_review_evidence
            expected_effects = {
                "accept_for_network_record": {"network_checked"},
                "revise_and_resubmit": {"candidate"},
                "reject": {"no_change"},
                "challenge": {"challenged"},
                "no_opinion": {"no_change"},
            }
            recommendation = body.get("conclusion", {}).get("recommendation")
            claim_effect = body.get("conclusion", {}).get("claim_status_effect")
            if claim_effect not in expected_effects.get(recommendation, set()):
                errors.append(
                    f"{record.path}: conclusion claim_status_effect {claim_effect!r} "
                    f"is incoherent with recommendation {recommendation!r}"
                )
            if body.get("conclusion", {}).get("recommendation") == "accept_for_network_record":
                require_release_ready(record, "accept-for-network recommendation")
                if body.get("status") != "completed":
                    errors.append(
                        f"{record.path}: accept-for-network recommendation requires completed review status"
                    )
                if (
                    subject_target is not None
                    and subject_target.record_type == "evidence_record"
                ):
                    exact_subject_runs = [
                        review_run
                        for review_run in resolved_review_runs
                        if review_run.body.get("status") == "completed"
                        and any(
                            artifact_reference_exactly_matches_evidence(
                                reference,
                                subject_target,
                            )
                            for reference in review_run.body.get(
                                "input_artifacts", []
                            )
                        )
                    ]
                    if not exact_subject_runs:
                        errors.append(
                            f"{record.path}: accepting review requires at least one "
                            "completed review run whose input_artifacts bind the exact "
                            "reviewed evidence version and artifact digest"
                        )
                    subject_created_at = parse_timestamp(
                        subject_target.body.get("created_at")
                    )
                    review_updated_at = parse_timestamp(body.get("updated_at"))
                    for review_run in exact_subject_runs:
                        run_started_at = parse_timestamp(
                            review_run.body.get("started_at")
                        )
                        run_recorded_at = parse_timestamp(
                            review_run.body.get("recorded_at")
                        )
                        if (
                            subject_created_at is not None
                            and run_started_at is not None
                            and run_started_at < subject_created_at
                        ):
                            errors.append(
                                f"{record.path}: exact review run "
                                f"{review_run.record_id!r} started before the reviewed "
                                "evidence record was created"
                            )
                        if (
                            review_updated_at is not None
                            and run_recorded_at is not None
                            and run_recorded_at > review_updated_at
                        ):
                            errors.append(
                                f"{record.path}: exact review run "
                                f"{review_run.record_id!r} completed after review "
                                "updated_at"
                            )
                bad_results = [
                    result.get("status")
                    for result in body.get("acceptance_results", [])
                    if result.get("status") != "passed"
                ]
                if bad_results:
                    errors.append(
                        f"{record.path}: accept-for-network recommendation requires "
                        f"every reported criterion to pass; found {bad_results}"
                    )
                if body.get("independence", {}).get("conflict_status") == "unresolved":
                    errors.append(
                        f"{record.path}: accept-for-network recommendation has unresolved conflicts"
                    )
                open_serious = [
                    finding.get("finding_id")
                    for finding in body.get("findings", [])
                    if finding.get("status") == "open"
                    and finding.get("severity") in {"blocking", "major"}
                ]
                if open_serious:
                    errors.append(
                        f"{record.path}: accept-for-network recommendation has open "
                        f"serious findings: {open_serious}"
                    )
                disputed_serious = [
                    finding.get("finding_id")
                    for finding in body.get("findings", [])
                    if finding.get("status") == "disputed"
                    and finding.get("severity") in {"blocking", "major"}
                ]
                if disputed_serious:
                    errors.append(
                        f"{record.path}: accept-for-network recommendation has disputed "
                        f"serious findings: {disputed_serious}"
                    )

                packet_candidates: dict[str, list[LoadedRecord]] = {}

                def add_packet_candidate(candidate: LoadedRecord | None) -> None:
                    if candidate is not None:
                        packet_candidates.setdefault(candidate.record_id, []).append(
                            candidate
                        )

                review_evidence_by_id: dict[str, LoadedRecord] = {}
                if (
                    subject_target is not None
                    and subject_target.record_type == "evidence_record"
                ):
                    review_evidence_by_id[subject_target.record_id] = subject_target
                for evidence in review_evidence.get(record.exact_key, []):
                    previous = review_evidence_by_id.get(evidence.record_id)
                    if previous is None or previous.exact_key == evidence.exact_key:
                        review_evidence_by_id[evidence.record_id] = evidence
                for result in body.get("acceptance_results", []):
                    for reference in result.get("evidence_refs", []):
                        artifact_id = reference.get("artifact_id")
                        evidence = review_evidence_by_id.get(artifact_id)
                        add_packet_candidate(
                            evidence_packets.get(evidence.exact_key)
                            if evidence is not None
                            else None
                        )
                if subject_target is not None:
                    if subject_target.record_type == "research_packet":
                        add_packet_candidate(subject_target)
                    elif subject_target.record_type == "run_record":
                        add_packet_candidate(run_packets.get(subject_target.exact_key))
                    elif subject_target.record_type == "evidence_record":
                        add_packet_candidate(
                            evidence_packets.get(subject_target.exact_key)
                        )
                    elif (
                        subject_target.record_type == "source_record"
                        and not packet_candidates
                    ):
                        for candidate in packets:
                            if subject_target.record_id in packet_sources.get(
                                candidate.exact_key, {}
                            ):
                                add_packet_candidate(candidate)
                for review_run in resolved_review_runs:
                    add_packet_candidate(run_packets.get(review_run.exact_key))
                if len(packet_candidates) != 1:
                    errors.append(
                        f"{record.path}: accepting review must resolve to exactly one "
                        f"packet; found {sorted(packet_candidates)}"
                    )
                    review_packet = None
                else:
                    lineage_candidates = next(iter(packet_candidates.values()))
                    review_run_candidates = [
                        run_packets[review_run.exact_key]
                        for review_run in resolved_review_runs
                        if review_run.exact_key in run_packets
                    ]
                    review_packet = (
                        review_run_candidates[-1]
                        if review_run_candidates
                        else lineage_candidates[-1]
                    )
                    accepting_review_packets[record.exact_key] = review_packet

                if review_packet is not None:
                    criteria = {
                        criterion.get("criterion_id"): criterion
                        for criterion in review_packet.body.get(
                            "acceptance_criteria", []
                        )
                    }
                    result_by_id: dict[str, dict[str, Any]] = {}
                    for index, result in enumerate(body.get("acceptance_results", [])):
                        criterion_id = result.get("criterion_id")
                        if criterion_id in result_by_id:
                            errors.append(
                                f"{record.path}: duplicate acceptance result for "
                                f"criterion {criterion_id!r}"
                            )
                        result_by_id[criterion_id] = result
                        if criterion_id not in criteria:
                            errors.append(
                                f"{record.path}: $.acceptance_results[{index}] names "
                                f"unknown packet criterion {criterion_id!r}"
                            )
                        cited_references = result.get("evidence_refs", [])
                        if not cited_references:
                            errors.append(
                                f"{record.path}: accepting criterion {criterion_id!r} "
                                "must cite evidence"
                            )
                        for reference in cited_references:
                            artifact_id = reference.get("artifact_id")
                            evidence = review_evidence_by_id.get(artifact_id)
                            if evidence is not None and (
                                evidence.body.get("status") != "complete"
                                or evidence_packets.get(evidence.exact_key) is None
                                or evidence_packets[evidence.exact_key].record_id
                                != review_packet.record_id
                            ):
                                errors.append(
                                    f"{record.path}: criterion {criterion_id!r} cites "
                                    f"non-complete or wrong-packet evidence {artifact_id!r}"
                                )
                    missing_mandatory = [
                        criterion_id
                        for criterion_id, criterion in criteria.items()
                        if criterion.get("mandatory")
                        and (
                            criterion_id not in result_by_id
                            or result_by_id[criterion_id].get("status") != "passed"
                        )
                    ]
                    if missing_mandatory:
                        errors.append(
                            f"{record.path}: accepting review omits or does not pass "
                            f"mandatory criteria: {sorted(missing_mandatory)}"
                        )
                    packet_source_ids = set(
                        packet_sources.get(review_packet.exact_key, {})
                    )
                    review_source_ids = set(
                        body.get("submission_rights", {}).get(
                            "third_party_source_ids", []
                        )
                    )
                    if not packet_source_ids.issubset(review_source_ids):
                        errors.append(
                            f"{record.path}: accepting review rights manifest omits "
                            f"packet sources: {sorted(packet_source_ids - review_source_ids)}"
                        )
                    reviewer_id = body.get("responsible_reviewer_id")
                    for result in body.get("acceptance_results", []):
                        for reference in result.get("evidence_refs", []):
                            artifact_id = reference.get("artifact_id")
                            evidence = review_evidence_by_id.get(artifact_id)
                            producer_run = (
                                evidence_runs.get(evidence.exact_key)
                                if evidence is not None
                                else None
                            )
                            if producer_run is not None and producer_run.body.get(
                                "responsible_operator_id"
                            ) == reviewer_id:
                                errors.append(
                                    f"{record.path}: accepting reviewer is the producer "
                                    f"of cited artifact {artifact_id!r}"
                                )
                    cited_ids = {
                        reference.get("artifact_id")
                        for result in body.get("acceptance_results", [])
                        for reference in result.get("evidence_refs", [])
                    }
                    review_allowlist = set(
                        body.get("submission_boundary", {}).get(
                            "allowlisted_artifact_ids", []
                        )
                    )
                    if not cited_ids.issubset(review_allowlist):
                        errors.append(
                            f"{record.path}: acceptance evidence is outside the review "
                            f"public allowlist: {sorted(cited_ids - review_allowlist)}"
                        )
                formalization = body.get("formalization_scope", {})
                if body.get("review_type") == "formal_acceptance" and (
                    formalization.get("lane") != "formal_acceptance"
                    or formalization.get("formal_acceptance_status") != "passed"
                ):
                    errors.append(
                        f"{record.path}: formal-acceptance recommendation requires a passed formal-acceptance lane"
                    )
                if body.get("review_type") == "statement_correspondence" and (
                    formalization.get("lane") != "statement_correspondence"
                    or formalization.get("statement_correspondence_status") != "passed"
                ):
                    errors.append(
                        f"{record.path}: correspondence recommendation requires a passed statement-correspondence lane"
                    )

    # Problem records use the same immutable full-record identity, with an
    # explicit exact predecessor so later status or statement assessments never
    # retarget packets that cited an earlier version.
    problems_by_stable_id: dict[str, list[LoadedRecord]] = {}
    for problem in problems:
        problems_by_stable_id.setdefault(problem.record_id, []).append(problem)
    for problem_id, versions in problems_by_stable_id.items():
        successors: dict[tuple[str, str, str], LoadedRecord] = {}
        roots = [
            version
            for version in versions
            if version.body.get("previous_problem_ref") is None
        ]
        for version in versions:
            predecessor = problem_predecessors.get(version.exact_key)
            if predecessor is None or predecessor.record_id != problem_id:
                continue
            if predecessor.exact_key in successors:
                errors.append(
                    f"{version.path}: problem-record lineage forks from exact version "
                    f"{predecessor.record_version!r}"
                )
            else:
                successors[predecessor.exact_key] = version
        heads = [version for version in versions if version.exact_key not in successors]
        if len(roots) != 1:
            errors.append(
                f"problem {problem_id!r}: immutable version lineage must have one root; "
                f"found {len(roots)}"
            )
        if len(heads) != 1:
            errors.append(
                f"problem {problem_id!r}: immutable version lineage must have one "
                f"unambiguous head; found {len(heads)}"
            )
        if not roots:
            continue
        visited = {roots[0].exact_key}
        cursor = roots[0]
        while cursor.exact_key in successors:
            cursor = successors[cursor.exact_key]
            if cursor.exact_key in visited:
                errors.append(
                    f"{cursor.path}: problem-record version lineage contains a cycle"
                )
                break
            visited.add(cursor.exact_key)
        if len(visited) != len(versions):
            errors.append(
                f"problem {problem_id!r}: immutable version lineage is disconnected; "
                f"reached {len(visited)} of {len(versions)} records"
            )

    # Every packet revision is an immutable full-record snapshot.  Transition
    # records form one exact-reference graph per stable packet id.  A valid graph
    # is a single path from one draft snapshot to one unambiguous head; no version
    # is selected by filename, semantic-version ordering, or mutable projection.
    packets_by_stable_id: dict[str, list[LoadedRecord]] = {}
    transitions_by_stable_packet_id: dict[str, list[LoadedRecord]] = {}
    for packet in packets:
        packets_by_stable_id.setdefault(packet.record_id, []).append(packet)
    for transition in transitions:
        from_packet = transition_from_packets.get(transition.exact_key)
        to_packet = transition_to_packets.get(transition.exact_key)
        if from_packet is None or to_packet is None:
            continue
        transitions_by_stable_packet_id.setdefault(from_packet.record_id, []).append(
            transition
        )

        for evidence in transition_evidence.get(transition.exact_key, []):
            evidence_packet = evidence_packets.get(evidence.exact_key)
            if (
                evidence_packet is None
                or evidence_packet.record_id != from_packet.record_id
            ):
                errors.append(
                    f"{transition.path}: evidence reference {evidence.record_id!r} "
                    "belongs to a different packet lineage"
                )
        if transition.body.get("to_status") == "accepted":
            for review in transition_reviews.get(transition.exact_key, []):
                review_packet = accepting_review_packets.get(review.exact_key)
                if (
                    review_packet is None
                    or review_packet.record_id != to_packet.record_id
                ):
                    errors.append(
                        f"{transition.path}: accepted transition review "
                        f"{review.record_id!r} is not an accepting review for this "
                        "packet lineage"
                    )

    packet_heads: dict[str, LoadedRecord] = {}
    packet_history_positions: dict[
        str, dict[tuple[str, str, str], int]
    ] = {}
    packet_revision_floors: dict[
        str, dict[tuple[str, str, str], int]
    ] = {}
    for packet_id, snapshots in packets_by_stable_id.items():
        chain = transitions_by_stable_packet_id.get(packet_id, [])
        snapshot_by_key = {snapshot.exact_key: snapshot for snapshot in snapshots}
        incoming: dict[tuple[str, str, str], LoadedRecord] = {}
        outgoing: dict[tuple[str, str, str], LoadedRecord] = {}

        sequences = [transition.body.get("sequence") for transition in chain]
        if len(sequences) != len(set(sequences)):
            errors.append(
                f"packet {packet_id!r}: transition chain contains duplicate sequence values"
            )
        ordered_by_sequence = sorted(
            chain,
            key=lambda transition: (
                transition.body.get("sequence", 0),
                transition.body.get("occurred_at", ""),
                transition.record_id,
                transition.record_version,
            ),
        )
        expected_sequences = list(range(1, len(ordered_by_sequence) + 1))
        actual_sequences = [
            transition.body.get("sequence") for transition in ordered_by_sequence
        ]
        if actual_sequences != expected_sequences:
            errors.append(
                f"packet {packet_id!r}: transition sequence must be continuous from 1; "
                f"found {actual_sequences}"
            )

        for transition in chain:
            from_packet = transition_from_packets[transition.exact_key]
            to_packet = transition_to_packets[transition.exact_key]
            if from_packet.record_id != packet_id or to_packet.record_id != packet_id:
                continue
            if from_packet.exact_key in outgoing:
                errors.append(
                    f"{transition.path}: packet history forks from exact snapshot "
                    f"{from_packet.record_version!r}"
                )
            else:
                outgoing[from_packet.exact_key] = transition
            if to_packet.exact_key in incoming:
                errors.append(
                    f"{transition.path}: packet history has multiple predecessors for "
                    f"exact snapshot {to_packet.record_version!r}"
                )
            else:
                incoming[to_packet.exact_key] = transition

            from_status = transition.body.get("from_status")
            to_status = transition.body.get("to_status")
            event_kind = transition.body.get("event_kind")
            if (
                event_kind == "state_transition"
                and to_status not in ALLOWED_PACKET_TRANSITIONS.get(from_status, set())
            ):
                errors.append(
                    f"{transition.path}: illegal packet transition "
                    f"{from_status!r} -> {to_status!r}"
                )
            if (
                event_kind == "state_transition"
                and from_status in TERMINAL_PACKET_STATUSES
            ):
                errors.append(
                    f"{transition.path}: transition follows terminal packet status "
                    f"{from_status!r}"
                )

        roots = [snapshot for snapshot in snapshots if snapshot.exact_key not in incoming]
        heads = [snapshot for snapshot in snapshots if snapshot.exact_key not in outgoing]
        if len(roots) != 1:
            errors.append(
                f"packet {packet_id!r}: immutable snapshot history must have one root; "
                f"found {len(roots)}"
            )
        if len(heads) != 1:
            errors.append(
                f"packet {packet_id!r}: immutable snapshot history must have one "
                f"unambiguous head; found {len(heads)}"
            )
        if len(chain) != max(0, len(snapshots) - 1):
            errors.append(
                f"packet {packet_id!r}: transition count {len(chain)} does not connect "
                f"all {len(snapshots)} immutable snapshots"
            )
        if not roots:
            continue
        root = roots[0]
        if root.body.get("status") != "draft":
            errors.append(
                f"{root.path}: packet snapshot history must begin at draft status"
            )

        visited_snapshots = {root.exact_key}
        graph_order: list[LoadedRecord] = []
        cursor = root
        while cursor.exact_key in outgoing:
            transition = outgoing[cursor.exact_key]
            if transition in graph_order:
                errors.append(f"{transition.path}: packet snapshot history contains a cycle")
                break
            graph_order.append(transition)
            cursor = transition_to_packets[transition.exact_key]
            if cursor.exact_key in visited_snapshots:
                errors.append(f"{transition.path}: packet snapshot history contains a cycle")
                break
            visited_snapshots.add(cursor.exact_key)
        if len(visited_snapshots) != len(snapshot_by_key):
            errors.append(
                f"packet {packet_id!r}: transition history is disconnected; reached "
                f"{len(visited_snapshots)} of {len(snapshot_by_key)} snapshots"
            )
        if [item.exact_key for item in graph_order] != [
            item.exact_key for item in ordered_by_sequence
        ]:
            errors.append(
                f"packet {packet_id!r}: transition sequence order does not match "
                "exact snapshot-link order"
            )

        previous_time: datetime | None = None
        for transition in graph_order:
            occurred_at = parse_timestamp(transition.body.get("occurred_at"))
            if (
                previous_time is not None
                and occurred_at is not None
                and occurred_at <= previous_time
            ):
                errors.append(
                    f"{transition.path}: transition timestamps must be strictly increasing"
                )
            if occurred_at is not None:
                previous_time = occurred_at
        if len(heads) == 1:
            packet_heads[packet_id] = heads[0]

        # Record the exact revision epoch inherited by every snapshot.  A task
        # may be revised and later reverted byte-for-byte at the projection
        # level; positional epoch identity still prevents evidence or reviews
        # from before that revision from floating forward onto the new epoch.
        positions: dict[tuple[str, str, str], int] = {root.exact_key: 0}
        floors: dict[tuple[str, str, str], int] = {root.exact_key: 0}
        revision_floor = 0
        for position, transition in enumerate(graph_order, start=1):
            to_packet = transition_to_packets[transition.exact_key]
            positions[to_packet.exact_key] = position
            if transition.body.get("event_kind") == "record_revision":
                revision_floor = position
            floors[to_packet.exact_key] = revision_floor
        packet_history_positions[packet_id] = positions
        packet_revision_floors[packet_id] = floors

    # Acceptance is a collection-level state: it cannot be established by a
    # record in isolation.  Bind every required output, criterion, review type,
    # reviewer count and evidence version before an accepted packet can pass.
    incoming_transition_by_snapshot = {
        transition_to_packets[transition.exact_key].exact_key: transition
        for transition in transitions
        if transition.exact_key in transition_to_packets
    }

    def acceptance_entry_for_snapshot(packet: LoadedRecord) -> LoadedRecord | None:
        """Find the exact state-transition event that established acceptance."""

        cursor = packet
        seen: set[tuple[str, str, str]] = set()
        while cursor.exact_key not in seen:
            seen.add(cursor.exact_key)
            transition = incoming_transition_by_snapshot.get(cursor.exact_key)
            if transition is None:
                return None
            if (
                transition.body.get("event_kind") == "state_transition"
                and transition.body.get("from_status") != "accepted"
                and transition.body.get("to_status") == "accepted"
            ):
                return transition
            if transition.body.get("from_status") != "accepted":
                return None
            previous = transition_from_packets.get(transition.exact_key)
            if previous is None:
                return None
            cursor = previous
        return None

    for packet in packets:
        if packet.body.get("status") != "accepted":
            continue
        acceptance_transition = acceptance_entry_for_snapshot(packet)
        if acceptance_transition is None:
            errors.append(
                f"{packet.path}: accepted snapshot has no exact transition into "
                "accepted status"
            )
            acceptance_evidence: list[LoadedRecord] = []
            accepting_reviews: list[LoadedRecord] = []
        else:
            acceptance_evidence = transition_evidence.get(
                acceptance_transition.exact_key, []
            )
            accepting_reviews = transition_reviews.get(
                acceptance_transition.exact_key, []
            )

        history_positions = packet_history_positions.get(packet.record_id, {})
        revision_floors = packet_revision_floors.get(packet.record_id, {})
        acceptance_position = history_positions.get(packet.exact_key)
        revision_floor = revision_floors.get(packet.exact_key, 0)
        accepted_projection = packet_task_projection(packet.body)

        def require_current_revision_epoch(
            bound_packet: LoadedRecord | None,
            context: str,
        ) -> None:
            if bound_packet is None:
                return
            if bound_packet.record_id != packet.record_id:
                errors.append(
                    f"{packet.path}: {context} belongs to another packet lineage"
                )
                return
            position = history_positions.get(bound_packet.exact_key)
            if position is None:
                errors.append(
                    f"{packet.path}: {context} is not in the accepted packet's "
                    "exact snapshot history"
                )
                return
            if acceptance_position is not None and position > acceptance_position:
                errors.append(
                    f"{packet.path}: {context} postdates the exact acceptance snapshot"
                )
            if position < revision_floor:
                errors.append(
                    f"{packet.path}: {context} predates the latest record_revision "
                    "epoch inherited by this acceptance"
                )
            if packet_task_projection(bound_packet.body) != accepted_projection:
                errors.append(
                    f"{packet.path}: {context} does not bind the same "
                    "version-bound task-content projection as the accepted snapshot"
                )

        for evidence in acceptance_evidence:
            require_current_revision_epoch(
                evidence_packets.get(evidence.exact_key),
                f"acceptance evidence {evidence.record_id!r}",
            )
            producing_run = evidence_runs.get(evidence.exact_key)
            require_current_revision_epoch(
                run_packets.get(producing_run.exact_key)
                if producing_run is not None
                else None,
                f"producer run for acceptance evidence {evidence.record_id!r}",
            )
        declared_outputs = {
            output.get("artifact_id"): output
            for output in packet.body.get("outputs", [])
            if isinstance(output.get("artifact_id"), str)
        }
        required_ids = {
            artifact_id
            for artifact_id, output in declared_outputs.items()
            if output.get("required") is True
        }
        accepted_outputs: dict[str, LoadedRecord] = {}
        evidence_at_acceptance: dict[str, list[LoadedRecord]] = {}
        for evidence in acceptance_evidence:
            evidence_at_acceptance.setdefault(evidence.record_id, []).append(evidence)
        for artifact_id in sorted(required_ids - set(evidence_at_acceptance)):
            errors.append(
                f"{packet.path}: accepted packet is missing required output "
                f"{artifact_id!r} from its exact acceptance transition"
            )
        for artifact_id, candidates in sorted(evidence_at_acceptance.items()):
            declared_output = declared_outputs.get(artifact_id)
            if declared_output is None:
                errors.append(
                    f"{packet.path}: acceptance transition binds undeclared output "
                    f"evidence {artifact_id!r}"
                )
                continue
            output_label = (
                "required output"
                if declared_output.get("required") is True
                else "accepted optional output"
            )
            if not candidates:
                continue
            if len(candidates) != 1:
                errors.append(
                    f"{packet.path}: acceptance transition binds multiple versions of "
                    f"{output_label} {artifact_id!r}"
                )
                continue
            evidence = candidates[0]
            accepted_outputs[artifact_id] = evidence
            if evidence.body.get("status") != "complete":
                errors.append(
                    f"{packet.path}: {output_label} {artifact_id!r} is not complete"
                )
            if (
                evidence_packets.get(evidence.exact_key) is None
                or evidence_packets[evidence.exact_key].record_id != packet.record_id
            ):
                errors.append(
                    f"{packet.path}: {output_label} {artifact_id!r} belongs to another "
                    "packet lineage"
                )
            require_acceptance_eligible_evidence(
                evidence,
                evidence_packets.get(evidence.exact_key),
                evidence_runs.get(evidence.exact_key),
            )
        accepting_reviews = [
            review
            for review in accepting_reviews
            if accepting_review_packets.get(review.exact_key) is not None
            and accepting_review_packets[review.exact_key].record_id == packet.record_id
        ]
        for review in accepting_reviews:
            require_current_revision_epoch(
                accepting_review_packets.get(review.exact_key),
                f"accepting review {review.record_id!r}",
            )
            for review_run in review_runs.get(review.exact_key, []):
                require_current_revision_epoch(
                    run_packets.get(review_run.exact_key),
                    f"review run {review_run.record_id!r}",
                )
        review_plan = packet.body.get("review_plan", {})
        required_review_types = set(review_plan.get("required_review_types", []))
        if packet.body.get("formalization_plan", {}).get(
            "formal_acceptance_review"
        ) == "required":
            required_review_types.add("formal_acceptance")
        if packet.body.get("formalization_plan", {}).get(
            "statement_correspondence_review"
        ) == "required":
            required_review_types.add("statement_correspondence")
        observed_types = {review.body.get("review_type") for review in accepting_reviews}
        missing_types = required_review_types - observed_types
        if missing_types:
            errors.append(
                f"{packet.path}: accepted packet lacks required accepting review types: "
                f"{sorted(missing_types)}"
            )
        reviewers = {
            review.body.get("responsible_reviewer_id") for review in accepting_reviews
        }
        minimum_reviewers = review_plan.get("minimum_reviewers", 1)
        if len(reviewers) < minimum_reviewers:
            errors.append(
                f"{packet.path}: accepted packet has {len(reviewers)} distinct accepting "
                f"reviewers; requires {minimum_reviewers}"
            )

        for artifact_id in sorted(accepted_outputs):
            for review_type in sorted(required_review_types):
                covering = [
                    review
                    for review in accepting_reviews
                    if review.body.get("review_type") == review_type
                    and review_subjects.get(review.exact_key)
                    == accepted_outputs.get(artifact_id)
                    and any(
                        by_exact_key.get(
                            (
                                "evidence_record",
                                reference.get("artifact_id"),
                                reference.get("record_version"),
                            )
                        )
                        == accepted_outputs.get(artifact_id)
                        for result in review.body.get("acceptance_results", [])
                        for reference in result.get("evidence_refs", [])
                    )
                ]
                if not covering:
                    errors.append(
                        f"{packet.path}: accepted output {artifact_id!r} lacks a "
                        f"{review_type!r} accepting review bound to its exact evidence version"
                    )

        for review in accepting_reviews:
            criteria = {
                criterion.get("criterion_id"): criterion
                for criterion in packet.body.get("acceptance_criteria", [])
            }
            for result in review.body.get("acceptance_results", []):
                criterion = criteria.get(result.get("criterion_id"))
                if criterion is None:
                    continue
                observed_kinds = {
                    target.body.get("evidence_kind")
                    for reference in result.get("evidence_refs", [])
                    if (
                        target := by_exact_key.get(
                            (
                                "evidence_record",
                                reference.get("artifact_id"),
                                reference.get("record_version"),
                            )
                        )
                    )
                    is not None
                    and accepted_outputs.get(target.record_id) == target
                }
                required_kinds = set(criterion.get("required_evidence_kinds", []))
                if not required_kinds.issubset(observed_kinds):
                    errors.append(
                        f"{review.path}: criterion {result.get('criterion_id')!r} "
                        f"lacks required evidence kinds: {sorted(required_kinds - observed_kinds)}"
                    )

        if packet.body.get("submission_rights", {}).get(
            "redistribution_status"
        ) == "permitted":
            restricted_outputs = [
                artifact_id
                for artifact_id, evidence in accepted_outputs.items()
                if evidence.body.get("submission_rights", {}).get(
                    "redistribution_status"
                )
                != "permitted"
            ]
            if restricted_outputs:
                errors.append(
                    f"{packet.path}: packet cannot claim permitted redistribution while "
                    f"transition-accepted outputs are restricted: {sorted(restricted_outputs)}"
                )

    exact_transition_reviews_by_evidence: dict[
        tuple[str, str, str], dict[tuple[str, str, str], LoadedRecord]
    ] = {}
    network_accepted_evidence_keys: set[tuple[str, str, str]] = set()
    for transition in transitions:
        exact_reviews = transition_reviews.get(transition.exact_key, [])
        for evidence in transition_evidence.get(transition.exact_key, []):
            if (
                transition.body.get("event_kind") == "state_transition"
                and transition.body.get("from_status") != "accepted"
                and transition.body.get("to_status") == "accepted"
            ):
                network_accepted_evidence_keys.add(evidence.exact_key)
            by_exact_review = exact_transition_reviews_by_evidence.setdefault(
                evidence.exact_key, {}
            )
            for review in exact_reviews:
                by_exact_review[review.exact_key] = review
    for evidence in evidence_records:
        reproduction = evidence.body.get("reproducibility", {})
        level = reproduction.get("level")
        independently_reproduced = reproduction.get("independently_reproduced")
        independent_levels = {"independently_reproduced", "certified"}
        if independently_reproduced is True and level not in independent_levels:
            errors.append(
                f"{evidence.path}: independently_reproduced true requires an "
                "independently_reproduced or certified reproducibility level"
            )
        if independently_reproduced is False and level in independent_levels:
            errors.append(
                f"{evidence.path}: independently_reproduced false conflicts with "
                f"reproducibility level {level!r}"
            )
        if evidence.exact_key not in network_accepted_evidence_keys:
            continue
        producer = evidence_runs.get(evidence.exact_key)
        producer_id = (
            producer.body.get("responsible_operator_id") if producer is not None else None
        )
        reproduction_reviews = [
            review
            for review in exact_transition_reviews_by_evidence.get(
                evidence.exact_key, {}
            ).values()
            if review.body.get("status") == "completed"
            and review.body.get("review_type")
            in {"computational_reproduction", "mathematical_reconstruction"}
            and review_subjects.get(review.exact_key) == evidence
            and review.body.get("responsible_reviewer_id") != producer_id
        ]
        if not reproduction_reviews:
            errors.append(
                f"{evidence.path}: transition-accepted evidence requires an "
                "independent completed reproduction/reconstruction "
                "review co-bound by exact transition refs and reviewing this exact "
                "evidence version"
            )
    return errors


def _run_git(repository_root: Path, arguments: list[str]) -> subprocess.CompletedProcess[bytes]:
    """Run one bounded, non-shell Git query for repository-aware validation."""

    environment = {
        key: value
        for key, value in os.environ.items()
        if not key.upper().startswith("GIT_")
    }
    environment["GIT_NO_REPLACE_OBJECTS"] = "1"
    environment["GIT_OPTIONAL_LOCKS"] = "0"
    try:
        return subprocess.run(
            ["git", "--no-replace-objects", "-C", str(repository_root), *arguments],
            check=False,
            capture_output=True,
            timeout=10,
            env=environment,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ValueError(f"cannot run bounded Git query {arguments!r}: {exc}") from exc


def _safe_repository_git_path(value: Any) -> str | None:
    """Return one unambiguous repository-relative Git path or ``None``."""

    if not isinstance(value, str) or not value or len(value) > 4096:
        return None
    if value.startswith(("/", "\\")) or "\\" in value or "\0" in value:
        return None
    if urlparse(value).scheme or any(part in {"", ".", ".."} for part in value.split("/")):
        return None
    return value


def _protected_record_artifact_paths(body: dict[str, Any]) -> list[str]:
    """Collect exact artifact paths whose bytes a published record freezes."""

    record_type = body.get("record_type")
    candidates: list[Any] = []
    if record_type == "evidence_record":
        candidates.append(body.get("artifact_path"))
    elif record_type == "problem_record":
        statement = body.get("statement", {})
        if isinstance(statement, dict):
            candidates.append(statement.get("artifact_path"))
    elif record_type == "source_record":
        locator = body.get("locator", {})
        if isinstance(locator, dict) and locator.get("reference_kind") == "repository_artifact":
            candidates.append(locator.get("canonical_reference"))
    elif record_type == "review_record":
        subject = body.get("reviewed_subject", {})
        if isinstance(subject, dict):
            candidates.append(subject.get("artifact_path"))
    return [candidate for candidate in candidates if isinstance(candidate, str)]


def _git_tree_entry(
    repository_root: Path,
    commit: str,
    path: str,
) -> bytes | None:
    """Return the exact single ``ls-tree`` entry for ``commit:path``."""

    result = _run_git(repository_root, ["ls-tree", "-z", commit, "--", path])
    if result.returncode != 0 or not result.stdout:
        return None
    entries = [entry for entry in result.stdout.split(b"\0") if entry]
    if len(entries) != 1:
        return None
    return entries[0]


def validate_protected_base_history(
    repository_root: Path,
    protected_base_commit: str,
) -> list[str]:
    """Protect records/artifacts already present on the trusted integration base.

    The current collection's graph checks cannot prove that a contributor did
    not rewrite every old record and cascade its references.  This Git-backed
    gate treats every recognized record already present at the protected base,
    plus every exact artifact path frozen by such a record, as append-only.
    Corrections add new paths/versions/events; they never alter or delete the
    protected bytes or change a regular file into another Git object type.
    """

    root = repository_root.resolve()
    errors: list[str] = []
    if not FULL_GIT_COMMIT.fullmatch(protected_base_commit) or protected_base_commit == "0" * 40:
        return [
            f"{root}: protected base must be a nonzero full lowercase Git commit SHA"
        ]
    object_type = _run_git(root, ["cat-file", "-t", protected_base_commit])
    if object_type.returncode != 0 or object_type.stdout.strip() != b"commit":
        return [f"{root}: protected base is unavailable or is not a commit"]
    ancestor = _run_git(
        root, ["merge-base", "--is-ancestor", protected_base_commit, "HEAD"]
    )
    if ancestor.returncode != 0:
        return [f"{root}: protected base is not an ancestor of HEAD"]

    listing = _run_git(
        root, ["ls-tree", "-r", "-z", "--name-only", protected_base_commit]
    )
    if listing.returncode != 0:
        return [f"{root}: cannot enumerate the protected-base tree"]
    if len(listing.stdout) > MAX_GIT_TREE_LIST_BYTES:
        return [f"{root}: protected-base tree listing exceeds the bounded limit"]
    raw_paths = [item for item in listing.stdout.split(b"\0") if item]
    if len(raw_paths) > MAX_GIT_TREE_ENTRIES:
        return [
            f"{root}: protected-base tree exceeds {MAX_GIT_TREE_ENTRIES} entries"
        ]

    immutable_paths: set[str] = set()
    for raw_path in raw_paths:
        try:
            path = raw_path.decode("utf-8")
        except UnicodeDecodeError:
            errors.append(f"{root}: protected-base path is not UTF-8")
            continue
        safe_path = _safe_repository_git_path(path)
        if safe_path is None:
            errors.append(f"{root}: unsafe protected-base Git path {path!r}")
            continue
        # Only authoritative instance namespaces publish immutable record
        # identities.  Schemas, tools, and deliberately invalid test fixtures
        # may contain record-shaped JSON but remain ordinary maintainable code.
        if safe_path.split("/", 1)[0] not in DEFAULT_INSTANCE_DIRS:
            continue
        if not safe_path.lower().endswith(".json"):
            continue
        blob_size = _run_git(
            root, ["cat-file", "-s", f"{protected_base_commit}:{safe_path}"]
        )
        if blob_size.returncode != 0:
            errors.append(f"{root}: cannot size protected-base JSON {safe_path!r}")
            continue
        try:
            size = int(blob_size.stdout.strip())
        except ValueError:
            errors.append(f"{root}: invalid protected-base JSON size for {safe_path!r}")
            continue
        if size > MAX_JSON_FILE_BYTES:
            errors.append(
                f"{root}: protected-base JSON {safe_path!r} exceeds "
                f"{MAX_JSON_FILE_BYTES} bytes"
            )
            continue
        blob = _run_git(
            root, ["cat-file", "blob", f"{protected_base_commit}:{safe_path}"]
        )
        if blob.returncode != 0 or len(blob.stdout) != size:
            errors.append(f"{root}: cannot read protected-base JSON {safe_path!r}")
            continue
        try:
            body = json.loads(
                blob.stdout.decode("utf-8"),
                object_pairs_hook=reject_duplicate_keys,
                parse_constant=reject_nonfinite_number,
            )
        except (
            UnicodeDecodeError,
            json.JSONDecodeError,
            DuplicateKeyError,
            RecursionError,
            ValueError,
        ) as exc:
            errors.append(
                f"{root}: invalid protected-base JSON {safe_path!r}: {exc}"
            )
            continue
        if not isinstance(body, dict) or body.get("record_type") not in ID_FIELD_BY_TYPE:
            continue
        immutable_paths.add(safe_path)
        for artifact_path in _protected_record_artifact_paths(body):
            safe_artifact = _safe_repository_git_path(artifact_path)
            if safe_artifact is None:
                errors.append(
                    f"{root}: protected record {safe_path!r} names unsafe artifact "
                    f"path {artifact_path!r}"
                )
            else:
                immutable_paths.add(safe_artifact)

    for path in sorted(immutable_paths):
        base_entry = _git_tree_entry(root, protected_base_commit, path)
        if base_entry is None:
            errors.append(
                f"{root}: protected record references missing base artifact {path!r}"
            )
            continue
        head_entry = _git_tree_entry(root, "HEAD", path)
        if head_entry is None:
            errors.append(f"{root}: protected immutable path was deleted: {path}")
        elif head_entry != base_entry:
            errors.append(f"{root}: protected immutable path was modified: {path}")
    return errors


def validate_repository_bindings(
    paths: Iterable[Path],
    *,
    repository_root: Path | None = None,
    protected_base_commit: str | None = None,
) -> list[str]:
    """Validate Git-backed basis and reviewed-blob claims.

    This opt-in mode is intentionally separate from portable collection
    validation.  It requires complete local history, proves every declared basis
    is a real commit reachable from ``HEAD``, checks commit chronology, and
    proves a review's declared subject bytes actually existed at its stated
    commit.  CI must therefore use an unshallow checkout (``fetch-depth: 0``).
    """

    root = (ROOT if repository_root is None else repository_root).resolve()
    errors: list[str] = []
    try:
        top_level = _run_git(root, ["rev-parse", "--show-toplevel"])
    except ValueError as exc:
        return [str(exc)]
    if top_level.returncode != 0:
        detail = top_level.stderr.decode("utf-8", errors="replace").strip()
        return [f"{root}: repository-aware validation requires Git history: {detail}"]
    try:
        discovered_root = Path(top_level.stdout.decode("utf-8").strip()).resolve()
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        return [f"{root}: cannot decode Git repository root: {exc}"]
    if discovered_root != root:
        return [
            f"{root}: repository-aware root must equal the Git top level "
            f"{discovered_root}"
        ]

    # Historical grafts, object alternates, and replacement refs can make an
    # otherwise ordinary commit query describe a different history or object
    # store.  They are useful Git features, but not an acceptable trust base
    # for a self-contained provenance check.  Inherited GIT_* redirects are
    # already removed by _run_git; reject repository-local equivalents too.
    common_result = _run_git(
        root, ["rev-parse", "--path-format=absolute", "--git-common-dir"]
    )
    if common_result.returncode != 0:
        return [f"{root}: cannot resolve the Git common directory"]
    try:
        common_dir = Path(
            common_result.stdout.decode("utf-8").strip()
        ).resolve(strict=False)
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        return [f"{root}: cannot decode the Git common directory: {exc}"]
    for metadata_path, label in (
        (common_dir / "info" / "grafts", "grafts"),
        (common_dir / "objects" / "info" / "alternates", "object alternates"),
    ):
        try:
            if metadata_path.is_symlink() or (
                metadata_path.is_file() and metadata_path.stat().st_size > 0
            ):
                errors.append(
                    f"{root}: repository-aware validation rejects non-empty "
                    f"Git {label} metadata"
                )
        except OSError as exc:
            errors.append(f"{root}: cannot inspect Git {label} metadata: {exc}")
    replacements = _run_git(
        root, ["for-each-ref", "--format=%(refname)", "refs/replace"]
    )
    if replacements.returncode != 0:
        errors.append(f"{root}: cannot inspect Git replacement refs")
    elif replacements.stdout.strip():
        errors.append(
            f"{root}: repository-aware validation rejects Git replacement refs"
        )
    if protected_base_commit is not None:
        errors.extend(validate_protected_base_history(root, protected_base_commit))
    if errors:
        return errors

    records: list[LoadedRecord] = []
    records_by_exact_key: dict[tuple[str, str, str], LoadedRecord] = {}
    for path in sorted(set(paths)):
        if not path.is_file() or path.suffix.lower() != ".json":
            continue
        try:
            body = load_json(path)
        except ValueError:
            continue
        if isinstance(body, dict) and body.get("record_type") in ID_FIELD_BY_TYPE:
            record = LoadedRecord(path=path, body=body)
            records.append(record)
            records_by_exact_key[record.exact_key] = record

    def run_consumes_exact_evidence(
        run: LoadedRecord,
        evidence: LoadedRecord,
    ) -> bool:
        expected = [
            item.get("digest")
            for item in evidence.body.get("hashes", [])
            if isinstance(item, dict) and item.get("algorithm") == "sha256"
        ]
        if len(expected) != 1:
            return False
        for reference in run.body.get("input_artifacts", []):
            if not isinstance(reference, dict):
                continue
            observed = [
                item.get("digest")
                for item in reference.get("hashes", [])
                if isinstance(item, dict) and item.get("algorithm") == "sha256"
            ]
            if (
                reference.get("artifact_id") == evidence.record_id
                and reference.get("record_version") == evidence.record_version
                and observed == expected
            ):
                return True
        return False

    commit_cache: dict[str, tuple[datetime | None, str | None]] = {}

    def inspect_commit(commit: Any) -> tuple[datetime | None, str | None]:
        if not isinstance(commit, str):
            return None, "commit identifier is missing"
        if not FULL_GIT_COMMIT.fullmatch(commit) or commit == "0" * 40:
            return None, "commit identifier must be a nonzero full lowercase SHA-1"
        if commit in commit_cache:
            return commit_cache[commit]
        try:
            object_type = _run_git(root, ["cat-file", "-t", commit])
        except ValueError as exc:
            result = (None, str(exc))
            commit_cache[commit] = result
            return result
        if object_type.returncode != 0:
            result = (
                None,
                "commit is unavailable; fetch complete history (fetch-depth: 0)",
            )
            commit_cache[commit] = result
            return result
        if object_type.stdout.strip() != b"commit":
            result = (None, "object exists but is not a commit")
            commit_cache[commit] = result
            return result
        ancestor = _run_git(root, ["merge-base", "--is-ancestor", commit, "HEAD"])
        if ancestor.returncode != 0:
            result = (None, "commit is not an ancestor of HEAD")
            commit_cache[commit] = result
            return result
        if protected_base_commit is not None:
            trusted_ancestor = _run_git(
                root,
                ["merge-base", "--is-ancestor", commit, protected_base_commit],
            )
            if trusted_ancestor.returncode != 0:
                result = (
                    None,
                    "commit is not an ancestor of the protected integration base",
                )
                commit_cache[commit] = result
                return result
        timestamp_result = _run_git(root, ["show", "-s", "--format=%cI", commit])
        if timestamp_result.returncode != 0:
            result = (None, "cannot read commit timestamp")
            commit_cache[commit] = result
            return result
        try:
            timestamp_text = timestamp_result.stdout.decode("utf-8").strip()
        except UnicodeDecodeError as exc:
            result = (None, f"commit timestamp is not UTF-8: {exc}")
            commit_cache[commit] = result
            return result
        timestamp = parse_timestamp(timestamp_text)
        if timestamp is None:
            result = (None, f"commit timestamp is invalid: {timestamp_text!r}")
            commit_cache[commit] = result
            return result
        result = (timestamp, None)
        commit_cache[commit] = result
        return result

    for record in records:
        body = record.body
        if record.record_type == "research_packet":
            lease = body.get("lease", {})
            if not isinstance(lease, dict):
                continue
            base_commit = lease.get("base_commit")
            if base_commit is None:
                continue
            commit_time, reason = inspect_commit(base_commit)
            if reason is not None:
                errors.append(
                    f"{record.path}: $.lease.base_commit {base_commit!r} is invalid: "
                    f"{reason}"
                )
                continue
            claimed_at = parse_timestamp(lease.get("claimed_at"))
            if (
                commit_time is not None
                and claimed_at is not None
                and commit_time > claimed_at
            ):
                errors.append(
                    f"{record.path}: $.lease.base_commit was created after "
                    "lease claimed_at"
                )
        elif record.record_type == "run_record":
            workspace = body.get("workspace_revision", {})
            if not isinstance(workspace, dict) or workspace.get(
                "version_control"
            ) != "git":
                continue
            revision = workspace.get("revision")
            commit_time, reason = inspect_commit(revision)
            if reason is not None:
                errors.append(
                    f"{record.path}: $.workspace_revision.revision {revision!r} is "
                    f"invalid: {reason}"
                )
                continue
            started_at = parse_timestamp(body.get("started_at"))
            if (
                commit_time is not None
                and started_at is not None
                and commit_time > started_at
            ):
                errors.append(
                    f"{record.path}: $.workspace_revision.revision was created after "
                    "run started_at"
                )
        elif record.record_type == "packet_transition":
            commit = body.get("git_commit")
            commit_time, reason = inspect_commit(commit)
            if reason is not None:
                errors.append(
                    f"{record.path}: $.git_commit {commit!r} is invalid: {reason}"
                )
                continue
            occurred_at = parse_timestamp(body.get("occurred_at"))
            if (
                commit_time is not None
                and occurred_at is not None
                and commit_time > occurred_at
            ):
                errors.append(
                    f"{record.path}: $.git_commit was created after transition "
                    "occurred_at"
                )
        elif record.record_type == "review_record":
            subject = body.get("reviewed_subject", {})
            if not isinstance(subject, dict):
                continue
            commit = subject.get("git_commit")
            commit_time, reason = inspect_commit(commit)
            if reason is not None:
                errors.append(
                    f"{record.path}: $.reviewed_subject.git_commit {commit!r} is "
                    f"invalid: {reason}"
                )
                continue
            reviewed_at = parse_timestamp(body.get("updated_at"))
            if (
                commit_time is not None
                and reviewed_at is not None
                and commit_time > reviewed_at
            ):
                errors.append(
                    f"{record.path}: reviewed-subject commit was created after "
                    "review updated_at"
                )

            subject_target = records_by_exact_key.get(
                (
                    subject.get("record_type"),
                    subject.get("record_id"),
                    subject.get("record_version"),
                )
            )
            subject_created_at = (
                parse_timestamp(subject_target.body.get("created_at"))
                if subject_target is not None
                else None
            )
            if (
                subject_created_at is not None
                and commit_time is not None
                and subject_created_at > commit_time
            ):
                errors.append(
                    f"{record.path}: reviewed-subject commit predates the subject "
                    "record created_at"
                )

            if (
                body.get("conclusion", {}).get("recommendation")
                == "accept_for_network_record"
                and subject_target is not None
                and subject_target.record_type == "evidence_record"
            ):
                exact_subject_runs: list[LoadedRecord] = []
                for reference in body.get("review_run_refs", []):
                    if not isinstance(reference, dict):
                        continue
                    review_run = records_by_exact_key.get(
                        (
                            "run_record",
                            reference.get("run_id"),
                            reference.get("record_version"),
                        )
                    )
                    if (
                        review_run is not None
                        and review_run.body.get("status") == "completed"
                        and run_consumes_exact_evidence(
                            review_run,
                            subject_target,
                        )
                    ):
                        exact_subject_runs.append(review_run)
                git_subject_runs = [
                    review_run
                    for review_run in exact_subject_runs
                    if review_run.body.get("workspace_revision", {}).get(
                        "version_control"
                    )
                    == "git"
                ]
                if not git_subject_runs:
                    errors.append(
                        f"{record.path}: repository-aware accepting review requires "
                        "an exact-subject completed review run with a Git workspace "
                        "revision"
                    )
                for review_run in git_subject_runs:
                    revision = review_run.body.get("workspace_revision", {}).get(
                        "revision"
                    )
                    _, run_reason = inspect_commit(revision)
                    if run_reason is not None:
                        continue
                    subject_ancestor = _run_git(
                        root,
                        ["merge-base", "--is-ancestor", commit, revision],
                    )
                    if subject_ancestor.returncode != 0:
                        errors.append(
                            f"{record.path}: reviewed-subject commit is not an "
                            f"ancestor of exact review run {review_run.record_id!r} "
                            "workspace revision"
                        )

            artifact_path = subject.get("artifact_path")
            if (
                not isinstance(artifact_path, str)
                or artifact_path.startswith(("/", "\\"))
                or "\\" in artifact_path
                or ".." in artifact_path.split("/")
                or urlparse(artifact_path).scheme
            ):
                errors.append(
                    f"{record.path}: $.reviewed_subject.artifact_path is not a safe "
                    "repository-relative Git path"
                )
                continue
            blob_spec = f"{commit}:{artifact_path}"
            blob_size_result = _run_git(root, ["cat-file", "-s", blob_spec])
            if blob_size_result.returncode != 0:
                errors.append(
                    f"{record.path}: reviewed subject blob {artifact_path!r} does "
                    f"not exist at commit {commit}"
                )
                continue
            try:
                blob_size = int(blob_size_result.stdout.strip())
            except ValueError:
                errors.append(
                    f"{record.path}: cannot parse reviewed subject blob size"
                )
                continue
            if blob_size > MAX_JSON_FILE_BYTES:
                errors.append(
                    f"{record.path}: reviewed subject blob exceeds "
                    f"{MAX_JSON_FILE_BYTES} bytes"
                )
                continue
            blob = _run_git(root, ["cat-file", "blob", blob_spec])
            if blob.returncode != 0 or len(blob.stdout) != blob_size:
                errors.append(
                    f"{record.path}: cannot read the exact reviewed subject blob"
                )
                continue
            try:
                blob.stdout.decode("utf-8")
            except UnicodeDecodeError as exc:
                errors.append(
                    f"{record.path}: reviewed subject blob is not UTF-8: {exc}"
                )
                continue
            normalized = blob.stdout.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
            actual_digest = hashlib.sha256(normalized).hexdigest()
            expected_digests = [
                item.get("digest")
                for item in subject.get("hashes", [])
                if isinstance(item, dict) and item.get("algorithm") == "sha256"
            ]
            if len(expected_digests) != 1 or actual_digest != expected_digests[0]:
                errors.append(
                    f"{record.path}: reviewed subject blob at declared commit does "
                    "not match the exact LF-normalized reviewed-record digest"
                )
    return errors


def resolve_packet_heads(paths: Iterable[Path]) -> list[LoadedRecord]:
    """Return the unique immutable head snapshot for each packet lineage.

    Callers must first run full collection validation.  This helper deliberately
    follows exact ``from_packet_ref`` identities; it never guesses a head from a
    filename, status, modification time, or semantic-version ordering.
    """

    packets: dict[tuple[str, str, str], LoadedRecord] = {}
    outgoing: set[tuple[str, str, str]] = set()
    for path in sorted(set(paths)):
        if not path.is_file() or path.suffix.lower() != ".json":
            continue
        try:
            body = load_json(path)
        except ValueError:
            continue
        if not isinstance(body, dict):
            continue
        if body.get("record_type") == "research_packet":
            packet = LoadedRecord(path=path, body=body)
            packets[packet.exact_key] = packet
        elif body.get("record_type") == "packet_transition":
            reference = body.get("from_packet_ref")
            if isinstance(reference, dict):
                packet_id = reference.get("packet_id")
                record_version = reference.get("record_version")
                if isinstance(packet_id, str) and isinstance(record_version, str):
                    outgoing.add(("research_packet", packet_id, record_version))

    heads_by_id: dict[str, list[LoadedRecord]] = {}
    for key, packet in packets.items():
        if key not in outgoing:
            heads_by_id.setdefault(packet.record_id, []).append(packet)
    ambiguous = {
        packet_id: candidates
        for packet_id, candidates in heads_by_id.items()
        if len(candidates) != 1
    }
    missing_ids = {
        packet.record_id for packet in packets.values()
    } - set(heads_by_id)
    if ambiguous or missing_ids:
        details = [
            f"{packet_id!r} has {len(candidates)} heads"
            for packet_id, candidates in sorted(ambiguous.items())
        ]
        details.extend(f"{packet_id!r} has no head" for packet_id in sorted(missing_ids))
        raise ValueError("packet head resolution is ambiguous: " + "; ".join(details))
    return sorted(
        (candidates[0] for candidates in heads_by_id.values()),
        key=lambda packet: (packet.record_id, packet.record_version, str(packet.path)),
    )


def _published_example_markers(
    repository_root: Path,
) -> tuple[set[str], set[str], set[str], set[str], list[str]]:
    """Collect identities and statement bytes reserved by published examples.

    Static seeds protect the original calibration even in a partial checkout;
    bounded dynamic discovery automatically reserves identities introduced by
    future checked-in examples.  A malformed examples tree fails the live gate
    closed instead of weakening this exclusion silently.
    """

    project_ids = set(PUBLISHED_CALIBRATION_PROJECT_IDS)
    problem_ids = set(PUBLISHED_CALIBRATION_PROBLEM_IDS)
    packet_ids = set(PUBLISHED_CALIBRATION_PACKET_IDS)
    statement_digests = set(PUBLISHED_CALIBRATION_STATEMENT_SHA256)
    errors: list[str] = []
    examples_root = repository_root / "examples"
    if not examples_root.exists():
        return project_ids, problem_ids, packet_ids, statement_digests, errors
    try:
        example_paths = expand_paths([examples_root], repository_root=repository_root)
    except ValueError as exc:
        errors.append(f"cannot enumerate published examples safely: {exc}")
        return project_ids, problem_ids, packet_ids, statement_digests, errors
    for path in example_paths:
        try:
            body = load_json(path)
        except ValueError as exc:
            errors.append(f"cannot inspect published example marker: {exc}")
            continue
        if not isinstance(body, dict):
            continue
        project_id = body.get("project_id")
        if isinstance(project_id, str):
            project_ids.add(project_id)
        if body.get("record_type") == "problem_record":
            problem_id = body.get("problem_id")
            if isinstance(problem_id, str):
                problem_ids.add(problem_id)
            statement = body.get("statement", {})
            if isinstance(statement, dict):
                for item in statement.get("hashes", []):
                    if (
                        isinstance(item, dict)
                        and item.get("algorithm") == "sha256"
                        and isinstance(item.get("digest"), str)
                    ):
                        statement_digests.add(item["digest"])
        elif body.get("record_type") == "research_packet":
            packet_id = body.get("packet_id")
            if isinstance(packet_id, str):
                packet_ids.add(packet_id)
    return project_ids, problem_ids, packet_ids, statement_digests, errors


def _example_path_locations(value: Any, location: str = "$") -> list[str]:
    """Return schema path locations that point back into ``examples/**``."""

    found: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_location = f"{location}.{key}"
            if key in {"artifact_path", "canonical_reference"} and isinstance(
                child, str
            ):
                normalized = child.replace("\\", "/")
                if normalized.startswith("examples/"):
                    found.append(child_location)
            found.extend(_example_path_locations(child, child_location))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(_example_path_locations(child, f"{location}[{index}]"))
    return found


def validate_live_program(
    paths: Iterable[Path],
    *,
    repository_root: Path | None = None,
) -> list[str]:
    """Enforce the content-aware Day-1 live-program gate.

    Full schema and collection validation must run first.  This additional gate
    distinguishes an operational program from examples copied into a live
    directory: identities and exact statement bytes published as examples stay
    reserved, calibration-designated problems stay non-live, and at least one
    current packet head must have reached an actionable non-draft state through
    its exact append-only transition history.
    """

    root = ROOT if repository_root is None else repository_root
    selected = sorted(set(paths))
    errors: list[str] = []
    (
        example_project_ids,
        example_problem_ids,
        example_packet_ids,
        example_statement_digests,
        marker_errors,
    ) = _published_example_markers(root)
    errors.extend(marker_errors)

    records: list[LoadedRecord] = []
    for path in selected:
        if not is_live_instance_path(path, root):
            errors.append(
                f"{path}: --require-live accepts records only from declared live "
                "directories; examples paths never satisfy the live gate"
            )
            continue
        try:
            body = load_json(path)
        except ValueError as exc:
            errors.append(str(exc))
            continue
        if not isinstance(body, dict) or body.get("record_type") not in ID_FIELD_BY_TYPE:
            continue
        record = LoadedRecord(path=path, body=body)
        records.append(record)
        example_locations = _example_path_locations(body)
        if example_locations:
            errors.append(
                f"{path}: live record points into examples/** at "
                f"{', '.join(example_locations)}"
            )

    problems = [record for record in records if record.record_type == "problem_record"]
    packets = [record for record in records if record.record_type == "research_packet"]
    transitions = [
        record for record in records if record.record_type == "packet_transition"
    ]

    for problem in problems:
        body = problem.body
        project_id = body.get("project_id")
        if project_id in example_project_ids:
            errors.append(
                f"{problem.path}: project_id {project_id!r} is reserved by a "
                "published example/calibration"
            )
        if problem.record_id in example_problem_ids:
            errors.append(
                f"{problem.path}: problem_id {problem.record_id!r} is reserved by a "
                "published example/calibration"
            )
        if body.get("kind") == "calibration":
            errors.append(
                f"{problem.path}: problem kind 'calibration' cannot satisfy "
                "--require-live"
            )
        if body.get("current_status", {}).get(
            "assessment_method"
        ) == "calibration_designation":
            errors.append(
                f"{problem.path}: calibration_designation is a fixture/program-test "
                "marker, not a live status assessment"
            )
        statement = body.get("statement", {})
        if isinstance(statement, dict):
            digests = {
                item.get("digest")
                for item in statement.get("hashes", [])
                if isinstance(item, dict) and item.get("algorithm") == "sha256"
            }
            copied_digests = digests & example_statement_digests
            if copied_digests:
                errors.append(
                    f"{problem.path}: exact problem statement bytes are reserved by "
                    "a published example/calibration"
                )

    for packet in packets:
        project_id = packet.body.get("project_id")
        if project_id in example_project_ids:
            errors.append(
                f"{packet.path}: project_id {project_id!r} is reserved by a "
                "published example/calibration"
            )
        if packet.record_id in example_packet_ids:
            errors.append(
                f"{packet.path}: packet_id {packet.record_id!r} is reserved by a "
                "published example/calibration"
            )

    try:
        heads = resolve_packet_heads(selected)
    except ValueError as exc:
        errors.append(f"live packet graph is invalid: {exc}")
        return errors
    if not heads:
        errors.append(
            "live collection contains no research_packet lineage or derived head; "
            "no live packet queue exists"
        )
        return errors

    incoming_exact_keys: set[tuple[str, str, str]] = set()
    state_entries: set[tuple[str, str]] = set()
    for transition in transitions:
        reference = transition.body.get("to_packet_ref", {})
        if not isinstance(reference, dict):
            continue
        packet_id = reference.get("packet_id")
        record_version = reference.get("record_version")
        if isinstance(packet_id, str) and isinstance(record_version, str):
            incoming_exact_keys.add(
                ("research_packet", packet_id, record_version)
            )
            if transition.body.get("event_kind") == "state_transition":
                to_status = transition.body.get("to_status")
                if isinstance(to_status, str):
                    state_entries.add((packet_id, to_status))

    eligible_heads = [
        head
        for head in heads
        if head.body.get("status") in LIVE_QUEUE_HEAD_STATUSES
        and head.exact_key in incoming_exact_keys
        and (head.record_id, head.body.get("status")) in state_entries
    ]
    if not eligible_heads:
        rendered_heads = ", ".join(
            f"{head.record_id}@{head.record_version}:{head.body.get('status')}"
            for head in heads
        )
        errors.append(
            "live collection has no transition-backed actionable packet head; "
            "a copied root/draft, accepted archive, or terminal snapshot does not "
            f"establish a live queue (derived heads: {rendered_heads})"
        )
    return errors


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="record JSON files or directories; defaults to pilot record directories",
    )
    parser.add_argument(
        "--schema-only",
        action="store_true",
        help="lint and resolve the schema set without validating record instances",
    )
    parser.add_argument(
        "--require-live",
        action="store_true",
        help=(
            "validate only declared live record directories and fail when none exist; "
            "examples never satisfy this Day-1 gate"
        ),
    )
    parser.add_argument(
        "--repository-aware",
        action="store_true",
        help=(
            "also verify transition/review commits, ancestry, chronology, and "
            "the exact reviewed blob using complete local Git history"
        ),
    )
    parser.add_argument(
        "--protected-base",
        metavar="COMMIT",
        help=(
            "with --repository-aware, require every declared basis/review commit "
            "to predate this trusted integration-base commit and preserve every "
            "record/artifact already present there byte-for-byte"
        ),
    )
    return parser.parse_args(argv)


def validate_selected_paths(
    paths: Iterable[Path] | None = None,
    schema_set: SchemaSet | None = None,
    *,
    require_live: bool = False,
    repository_aware: bool = False,
    protected_base_commit: str | None = None,
) -> tuple[list[Path], list[str]]:
    """Validate explicit paths, live records, or the default discovered collection."""

    schemas = schema_set if schema_set is not None else load_schema_set()
    if require_live and paths is not None:
        raise ValueError("require_live cannot be combined with explicit record paths")
    if require_live:
        selected = discover_live_instances(ROOT)
    elif paths is not None:
        selected = expand_paths(paths, repository_root=ROOT)
    else:
        selected = discover_instances(ROOT)
    if not selected:
        if require_live:
            return [], [
                "no live pilot record instances found; examples/calibration cannot "
                "satisfy the Day-1 gate and no live packet queue exists"
            ]
        return [], ["no pilot record instances found in the selected collection"]
    errors: list[str] = []
    for path in selected:
        if not is_within_repository(path, ROOT):
            errors.append(f"{path}: record path escapes the repository")
        elif path.suffix.lower() != ".json":
            errors.append(f"{path}: expected a .json record")
        elif path.is_symlink():
            errors.append(f"{path}: symbolic-link records are not permitted")
        elif not path.is_file():
            errors.append(f"{path}: record file does not exist")
        else:
            errors.extend(validate_record_file(path, schemas))
    if not errors:
        errors.extend(validate_collection(selected, schemas))
    if repository_aware and not errors:
        errors.extend(
            validate_repository_bindings(
                selected,
                repository_root=ROOT,
                protected_base_commit=protected_base_commit,
            )
        )
    if require_live and not errors:
        errors.extend(validate_live_program(selected, repository_root=ROOT))
    return selected, errors


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    if args.schema_only and args.paths:
        print("ERROR: --schema-only cannot be combined with record paths")
        return 2
    if args.require_live and args.paths:
        print("ERROR: --require-live cannot be combined with explicit record paths")
        return 2
    if args.require_live and args.schema_only:
        print("ERROR: --require-live cannot be combined with --schema-only")
        return 2
    if args.repository_aware and args.schema_only:
        print("ERROR: --repository-aware cannot be combined with --schema-only")
        return 2
    if args.protected_base and not args.repository_aware:
        print("ERROR: --protected-base requires --repository-aware")
        return 2
    try:
        schema_set = load_schema_set()
    except ValueError as exc:
        for line in str(exc).splitlines():
            print(f"ERROR: {line}")
        return 1

    if args.schema_only:
        print(
            f"PASS: {len(schema_set.documents)} pilot schemas are supported and references resolve"
        )
        return 0

    try:
        paths, errors = validate_selected_paths(
            args.paths if args.paths else None,
            schema_set,
            require_live=args.require_live,
            repository_aware=args.repository_aware,
            protected_base_commit=args.protected_base,
        )
    except ValueError as exc:
        print(f"ERROR: {exc}")
        return 1
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    if args.require_live:
        print(
            f"PASS: {len(paths)} records in the live Day-1 collection satisfy "
            "the versioned schema set"
        )
    elif args.paths:
        print(
            f"PASS: {len(paths)} records in the selected collection satisfy "
            "the versioned schema set"
        )
    else:
        live_count = sum(is_live_instance_path(path, ROOT) for path in paths)
        if live_count == 0:
            print(
                f"PASS: {len(paths)} records in the default discovered collection "
                "satisfy the versioned schema set; calibration-only: no live packet "
                "queue exists"
            )
        else:
            print(
                f"PASS: {len(paths)} records in the default discovered collection "
                f"satisfy the versioned schema set ({live_count} live records)"
            )
    return 0


if __name__ == "__main__":
    sys.exit(main())
