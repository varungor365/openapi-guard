# openapi-guard

**Catch breaking OpenAPI changes before they reach your consumers.**

`openapi-guard` compares two OpenAPI 3 documents and reports removed operations, removed response codes, newly required request parameters (including parameters inherited from a path item), newly required request bodies, and required request fields that were added to existing schemas. It is a small, CI-friendly complement to full contract-testing platforms.

## Quick start

```bash
pipx install openapi-guard
openapi_guard openapi.yml openapi.next.yml
openapi_guard openapi.json openapi.next.json --format json --fail-on breaking
```

The command exits non-zero when breaking changes are found and can emit stable JSON for CI annotations. YAML support uses PyYAML; JSON works without YAML syntax.

## Design boundaries

This is a structural diff, not a runtime compatibility guarantee. It does not call endpoints, infer business rules, or claim that two schemas are semantically identical. Review the report alongside contract tests and consumer requirements.

## Why star this repository

Star this project if you publish APIs, maintain OpenAPI specs, review versioned contracts, or want a focused breaking-change gate that is easy to run locally and in CI.

## Development

```bash
git clone https://github.com/varungor365/openapi-guard
cd openapi-guard
python -m pip install -e ".[dev]"
pytest -q
```

## License

MIT.
