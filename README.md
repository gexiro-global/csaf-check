# csaf-check

[![CI](https://github.com/gexiro-global/csaf-check/actions/workflows/ci.yml/badge.svg)](https://github.com/gexiro-global/csaf-check/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](pyproject.toml)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)

Validate CSAF 2.0 advisories from Python, using the same validator Secvisogram runs - and get an
honest answer when that validator is not installed.

## The problem

If you publish security advisories as CSAF, you want schema validation in your release pipeline,
not in a browser tab at the end. The authoritative implementation of the CSAF 2.0 mandatory tests
is [`@secvisogram/csaf-validator-lib`](https://github.com/secvisogram/csaf-validator-lib), which is
JavaScript. Reimplementing the schema in Python means maintaining a second, subtly different
opinion about what "valid" means - and yours will be the wrong one.

So this package does not reimplement anything. It bridges to the real validator and handles the
part that is annoying to get right: **what happens when the validator is not there.**

## The contract

`validate()` never raises. Not when Node is missing, not when the library is absent, not when the
validator times out or returns something unexpected. Each of those returns a result that says so:

```python
from csaf_check import validate

result = validate(advisory_dict)

result.available   # could the validator run at all?
result.is_valid    # True / False / None when no verdict was reached
result.errors      # one message per failed mandatory test
result.note        # why there is no verdict, when there isn't
result.conclusive  # available and a verdict exists
```

This matters because the alternative - a validator that throws on a missing optional dependency -
turns a quality gate into a hard dependency, and every caller ends up wrapping it in `try/except`
and swallowing real failures along with the boring ones.

## Install

```bash
pip install csaf-check
```

That gives you the Python API and CLI. For actual validation you also need Node.js and the
validator library:

```bash
npm install @secvisogram/csaf-validator-lib
```

Without them, `csaf-check` reports `UNKNOWN - validator unavailable` and exits 0, so it can sit in a
pipeline that has no Node without breaking it. Add `--require-validator` where the absence itself
should be a failure.

The validator is found either next to the installed package or under `node_modules` in your current
working directory, so running `npm install` in your own project directory is enough - you do not
have to install it into `site-packages`. `NODE_PATH` is honoured as well.

## CLI

```bash
csaf-check advisory.json                      # human-readable verdict
csaf-check advisory.json --json               # machine-readable
csaf-check - < advisory.json                  # stdin
csaf-check advisory.json --require-validator  # fail if no verdict is possible
```

Exit codes: `0` valid (or inconclusive without `--require-validator`) - `1` invalid -
`2` unreadable or malformed input - `3` no verdict possible and `--require-validator` was set.

## Python API

```python
import json
from csaf_check import validate, validator_available

if not validator_available():
    print("install Node.js to enable strict validation")

with open("advisory.json", encoding="utf-8") as fh:
    result = validate(json.load(fh))

if result.conclusive and not result.is_valid:
    for message in result.errors:
        print("FAIL", message)
```

## What this does NOT do

- It does not generate CSAF documents. It only validates ones you already have.
- It runs the mandatory tests only, not the informative or optional profiles.
- It does not check that your advisory is *correct*, only that it is well-formed. A schema-valid
  document can still describe the wrong product or the wrong affected range.
- It does not publish anything, sign anything, or talk to any network service.
- It is not legal advice about the EU Cyber Resilience Act. CRA is format-neutral and does not
  mandate CSAF. CSAF is a good machine-readable choice for advisories and VEX, not a compliance
  checkbox.

## Examples

`examples/advisory-minimal.json` is a small synthetic advisory for a fictional vendor using a
placeholder CVE identifier. `examples/advisory-invalid.json` is deliberately missing the mandatory
`tracking` object. Both exist to exercise this wrapper; neither describes a real product or a real
vulnerability.

## Testing

```bash
pip install -e ".[dev]"
pytest -q
```

The suite runs without Node.js on purpose - the degradation path is the part most likely to rot.

## License

Apache-2.0. See [LICENSE](LICENSE).

Built and maintained by Gexiro Global Enterprises Ltd.
