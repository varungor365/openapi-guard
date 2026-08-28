# openapi-guard: OpenAPI Breaking-Change Detector

**Catch structural OpenAPI contract changes before they reach your consumers.**

`openapi-guard` is a small, CI-friendly command-line tool for comparing two OpenAPI 3 documents. It reports removed operations, removed successful responses, newly required request parameters, newly required request bodies, and request fields that became required in existing JSON request schemas.

## Why this exists

An API specification can change in ways that are easy to miss in a pull request but disruptive to SDKs, clients, and downstream services. `openapi-guard` gives maintainers a deterministic structural diff that is easy to run locally, review in CI, or serialize for automation.

| Use case | Recommended command |
|---|---|
| Local API review | `openapi_guard old.yml new.yml` |
| CI breaking-change gate | `openapi_guard old.yml new.yml --fail-on breaking` |
| Machine-readable report | Add `--format json` |
| Non-breaking-change gate | Use `--fail-on any` to fail on every detected change |

## Three-minute quick start

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install openapi-guard
openapi_guard openapi.yml openapi.next.yml
```

The command exits non-zero when the selected failure policy is triggered. JSON input works without the YAML dependency; YAML input uses PyYAML. Try the included fixture pair:

```bash
openapi_guard examples/old.yaml examples/new.yaml --format json --fail-on breaking
```

The changed fixture intentionally removes a response code, so the command demonstrates a breaking finding and a non-zero exit status.

## CI usage

```yaml
name: API compatibility

on:
  pull_request:
  push:
    branches: [main]

permissions:
  contents: read

jobs:
  contract-diff:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683
      - uses: actions/setup-python@42375524e23c412d93fb67b49958b491fce71c38
        with:
          python-version: '3.12'
      - run: python -m pip install openapi-guard
      - run: openapi_guard openapi.yml openapi.next.yml --format json --fail-on breaking
```

The action references in this example are pinned to full-length commit SHAs. Review and update them through your normal dependency process.

## What it reports

| Finding | Meaning |
|---|---|
| Removed operation | A method/path combination disappeared. |
| Removed successful response | A `2xx` or `default` response disappeared. |
| New required parameter | A required path, query, header, or cookie parameter was added. |
| Required request body | An optional request body became required. |
| New required request field | A JSON request field became required in an existing operation. |
| Added operation | A new operation was detected as non-breaking. |

## Design boundaries

This is a structural diff, not a runtime compatibility guarantee. It does not call endpoints, resolve every `$ref`, infer business rules, compare every schema constraint, or claim that two documents are semantically identical. Review the report alongside contract tests, generated-client checks, and consumer requirements. The tool is intentionally conservative about what it reports so the behavior remains inspectable.

## Why star this repository?

Star this project if you publish APIs, maintain OpenAPI specifications, review versioned contracts, or want a focused breaking-change gate that is easy to run locally and in CI without adopting a larger platform.

## Development

```bash
git clone https://github.com/varungor365/openapi-guard
cd openapi-guard
python -m pip install -e '.[dev]'
pytest -q
```

## References

See the [OpenAPI Specification](https://spec.openapis.org/oas/latest.html) for the document format and [GitHub Actions secure-use guidance](https://docs.github.com/en/actions/reference/security/secure-use) for workflow permissions and dependency hygiene.

## License

MIT. See [LICENSE](LICENSE).
