from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

METHODS = {"get", "put", "post", "delete", "options", "head", "patch", "trace"}


@dataclass
class Change:
    level: str
    kind: str
    path: str
    detail: str


def load_document(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        return json.loads(text)
    if yaml is None:
        raise RuntimeError("YAML input requires PyYAML; use JSON or install the yaml extra")
    data = yaml.safe_load(text)
    if not isinstance(data, dict):
        raise ValueError("OpenAPI document must be an object")
    return data


def operations(doc: dict) -> dict[tuple[str, str], dict]:
    result = {}
    for path, item in (doc.get("paths") or {}).items():
        if not isinstance(item, dict):
            continue
        for method, operation in item.items():
            if method.lower() in METHODS and isinstance(operation, dict):
                result[(path, method.lower())] = operation
    return result


def required_parameters(path_item: dict, operation: dict) -> set[tuple[str, str]]:
    """Return required parameters inherited from the path item and operation."""
    parameters = []
    parameters.extend(path_item.get("parameters") or [])
    parameters.extend(operation.get("parameters") or [])
    return {
        (item.get("in", ""), item.get("name", ""))
        for item in parameters
        if isinstance(item, dict) and item.get("required")
    }


def required_body_fields(operation: dict) -> set[str]:
    body = operation.get("requestBody") or {}
    schema = ((body.get("content") or {}).get("application/json") or {}).get("schema") or {}
    return set(schema.get("required") or [])


def compare(old: dict, new: dict) -> list[Change]:
    changes: list[Change] = []
    before, after = operations(old), operations(new)
    old_paths = old.get("paths") or {}
    new_paths = new.get("paths") or {}
    for key in sorted(before.keys() - after.keys()):
        changes.append(Change("breaking", "removed-operation", f"{key[1].upper()} {key[0]}", "operation was removed"))
    for key in sorted(after.keys() - before.keys()):
        changes.append(Change("non-breaking", "added-operation", f"{key[1].upper()} {key[0]}", "operation was added"))
    for key in sorted(before.keys() & after.keys()):
        path, method = key
        old_op, new_op = before[key], after[key]
        old_item = old_paths.get(path) if isinstance(old_paths.get(path), dict) else {}
        new_item = new_paths.get(path) if isinstance(new_paths.get(path), dict) else {}
        added_params = required_parameters(new_item, new_op) - required_parameters(old_item, old_op)
        for location, name in sorted(added_params):
            changes.append(Change("breaking", "new-required-parameter", f"{method.upper()} {path}", f"required {location} parameter '{name}' was added"))
        if not (old_op.get("requestBody") or {}).get("required") and (new_op.get("requestBody") or {}).get("required"):
            changes.append(Change("breaking", "required-request-body", f"{method.upper()} {path}", "request body became required"))
        for field in sorted(required_body_fields(new_op) - required_body_fields(old_op)):
            changes.append(Change("breaking", "new-required-field", f"{method.upper()} {path}", f"request field '{field}' became required"))
        old_responses = old_op.get("responses") or {}
        new_responses = new_op.get("responses") or {}
        for status in sorted(set(old_responses) - set(new_responses)):
            if str(status).startswith("2") or str(status) == "default":
                changes.append(Change("breaking", "removed-response", f"{method.upper()} {path}", f"response {status} was removed"))
    return changes


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Detect structural breaking changes between OpenAPI 3 documents")
    parser.add_argument("old", type=Path)
    parser.add_argument("new", type=Path)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--fail-on", choices=("breaking", "any", "never"), default="breaking")
    args = parser.parse_args(argv)
    changes = compare(load_document(args.old), load_document(args.new))
    if args.format == "json":
        print(json.dumps({"changes": [asdict(change) for change in changes], "breaking": sum(c.level == "breaking" for c in changes)}, indent=2))
    else:
        if not changes:
            print("openapi-guard: no structural changes detected")
        for change in changes:
            print(f"{change.level.upper():12} {change.kind:24} {change.path} — {change.detail}")
    if args.fail_on == "breaking" and any(c.level == "breaking" for c in changes):
        return 1
    if args.fail_on == "any" and changes:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
