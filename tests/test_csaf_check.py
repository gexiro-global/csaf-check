"""Tests for csaf-check.

These run without Node.js and without @secvisogram/csaf-validator-lib installed. That is
deliberate: the contract this package promises is that a missing validator degrades to an
honest "unavailable" answer rather than an exception, and that contract is exactly what
breaks silently if it is never tested on a machine that lacks the dependency.
"""

import json
import pathlib

from csaf_check import ValidationResult, validate, validator_available
from csaf_check import validator as validator_module
from csaf_check.cli import main

EXAMPLES = pathlib.Path(__file__).resolve().parent.parent / "examples"


def load(name):
    with open(EXAMPLES / name, "r", encoding="utf-8") as handle:
        return json.load(handle)


def test_examples_are_parseable():
    assert load("advisory-minimal.json")["document"]["csaf_version"] == "2.0"
    assert "tracking" not in load("advisory-invalid.json")["document"]


def test_validate_never_raises_without_the_js_dependency():
    result = validate(load("advisory-minimal.json"))
    assert isinstance(result, ValidationResult)
    assert isinstance(result.to_dict(), dict)


def test_unavailable_validator_is_reported_not_raised(monkeypatch):
    """Force the missing-bridge path instead of hoping the machine lacks Node.

    Branching on whatever happens to be installed means this contract goes untested on any
    machine that has the dependency - which is every CI job that matters.
    """
    monkeypatch.setattr(validator_module, "_JS", "/nonexistent/csaf_validate.cjs")
    result = validate(load("advisory-minimal.json"))
    assert result.available is False
    assert result.is_valid is None
    assert result.conclusive is False
    assert result.note


def test_validate_never_raises_when_the_temp_dir_cannot_be_created(monkeypatch):
    def explode(*_args, **_kwargs):
        raise OSError("no space left on device")

    monkeypatch.setattr(validator_module.tempfile, "mkdtemp", explode)
    result = validate(load("advisory-minimal.json"))
    assert isinstance(result, ValidationResult)
    assert result.conclusive is False


def test_validate_tolerates_an_empty_document():
    result = validate({})
    assert isinstance(result, ValidationResult)


def test_validator_available_reports_a_bool():
    assert isinstance(validator_available(), bool)


def test_result_serialises_to_the_documented_shape():
    payload = ValidationResult(available=True, is_valid=False, errors=["x"], note="n").to_dict()
    assert set(payload) == {"available", "isValid", "errors", "note"}
    assert payload["isValid"] is False


def test_cli_rejects_malformed_json(tmp_path, capsys):
    bad = tmp_path / "bad.json"
    bad.write_text("{not json", encoding="utf-8")
    assert main([str(bad)]) == 2


def test_cli_rejects_a_missing_file():
    assert main(["/nonexistent/advisory.json"]) == 2


def test_cli_is_lenient_by_default_and_strict_on_request(monkeypatch, capsys):
    """Pin both halves of the contract with the validator forced unavailable.

    validator_available() only reports whether Node exists, so branching on it left the
    strict-mode assertion unexercised whenever Node was installed but the JS package was not.
    """
    monkeypatch.setattr(validator_module, "_JS", "/nonexistent/csaf_validate.cjs")
    doc = str(EXAMPLES / "advisory-minimal.json")
    assert main([doc]) == 0, "an unavailable validator must not fail a build by default"
    assert main([doc, "--require-validator"]) == 3, "--require-validator must fail with no verdict"


def test_cli_json_output_is_machine_readable(capsys):
    main([str(EXAMPLES / "advisory-minimal.json"), "--json"])
    payload = json.loads(capsys.readouterr().out)
    assert "available" in payload and "isValid" in payload
