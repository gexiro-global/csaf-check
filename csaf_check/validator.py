"""Thin, dependency-free bridge to @secvisogram/csaf-validator-lib.

The library that actually knows the CSAF 2.0 schema is JavaScript - it is the same engine
Secvisogram runs, maintained under the BSI umbrella. Reimplementing the schema in Python
would mean maintaining a second, subtly different opinion about what "valid" means, so this
module shells out to the real thing instead.

Design rule: never raise. A validator that throws when Node is missing turns an optional
quality gate into a hard dependency, and the caller ends up wrapping every call in
try/except. Every failure mode here returns a ValidationResult with ``available=False`` or
``is_valid=None`` and an explanatory note.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

_JS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "js", "csaf_validate.cjs")


@dataclass
class ValidationResult:
    """Outcome of a validation attempt.

    available: the JS validator could be executed at all.
    is_valid:  True/False when the validator ran, None when it could not reach a verdict.
    errors:    human-readable messages, one per failed mandatory test.
    note:      why a verdict is missing, when it is.
    """

    available: bool
    is_valid: Optional[bool] = None
    errors: List[str] = field(default_factory=list)
    note: str = ""

    @property
    def conclusive(self) -> bool:
        return self.available and self.is_valid is not None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "available": self.available,
            "isValid": self.is_valid,
            "errors": list(self.errors),
            "note": self.note,
        }


def node_available() -> bool:
    """True if a usable ``node`` binary is on PATH."""
    try:
        proc = subprocess.run(
            ["node", "--version"], capture_output=True, text=True, timeout=5
        )
        return proc.returncode == 0
    except Exception:
        return False


def validator_available() -> bool:
    """True if both Node and the bundled bridge script are present.

    This does not prove ``@secvisogram/csaf-validator-lib`` is installed - that is only
    discoverable by running the bridge, which :func:`validate` reports as ``available=False``.
    """
    return node_available() and os.path.isfile(_JS)


def validate(document: Dict[str, Any], timeout: int = 40) -> ValidationResult:
    """Validate a CSAF document against the strict CSAF 2.0 mandatory tests.

    Args:
        document: the advisory, already parsed into a dict.
        timeout: seconds to allow the Node process.

    Returns:
        ValidationResult. Never raises.
    """
    if not validator_available():
        return ValidationResult(
            available=False,
            note="node or the bundled bridge script is not available; "
                 "install Node.js and @secvisogram/csaf-validator-lib, "
                 "or validate manually at https://secvisogram.github.io",
        )

    workdir = tempfile.mkdtemp(prefix="csaf_check_")
    docfile = os.path.join(workdir, "doc.json")
    try:
        with open(docfile, "w", encoding="utf-8") as handle:
            json.dump(document, handle)

        proc = subprocess.run(
            ["node", _JS, docfile], capture_output=True, text=True, timeout=timeout
        )
        stdout = (proc.stdout or "").strip()
        if stdout:
            try:
                payload = json.loads(stdout.splitlines()[-1])
                return ValidationResult(
                    available=bool(payload.get("available", False)),
                    is_valid=payload.get("isValid"),
                    errors=list(payload.get("errors") or []),
                    note=str(payload.get("note") or ""),
                )
            except (ValueError, AttributeError):
                pass
        return ValidationResult(
            available=True,
            note=((proc.stderr or stdout or "no validator output")[-500:]),
        )
    except subprocess.TimeoutExpired:
        return ValidationResult(available=True, note=f"validator timed out after {timeout}s")
    except Exception as exc:  # pragma: no cover - defensive, must never propagate
        return ValidationResult(available=True, note=str(exc))
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
