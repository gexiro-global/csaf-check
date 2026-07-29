# Putting csaf-check in a release pipeline

## Where it belongs

Schema validation is a release gate, not an authoring aid. Run it where the advisory becomes
immutable - the same place you sign artefacts - rather than on every edit.

```bash
csaf-check "advisories/${ID}.json" --require-validator || exit 1
```

`--require-validator` is the right flag here: in a release job, "we could not check" and "it is
fine" are not the same answer.

## Where the lenient default belongs

In a pre-commit hook or a developer's local run, exiting 0 on a missing Node.js is what you want.
A contributor without the JavaScript toolchain should still be able to run your test suite.

## Two verdicts you should not conflate

| Result | Meaning | Reasonable response |
|---|---|---|
| `available=False` | The validator could not run. | Install Node.js and the library, or accept the gap knowingly. |
| `is_valid=False` | The validator ran and rejected the document. | Fix the advisory. |

Treating the first as a pass is how unvalidated advisories get published. Treating it as a failure
in every context is how you block contributors who have no reason to install Node.

## Validating by hand

For a one-off check without any toolchain, paste the document into
[Secvisogram](https://secvisogram.github.io). It runs the same mandatory tests this package bridges
to. Do not do this with an advisory that is still under embargo.

## A note on scope

This package answers "is this document well-formed CSAF 2.0?". It cannot answer "is this advisory
true?" - product identifiers, affected version ranges and remediation text are all schema-valid
when they are wrong. Keep a human review step.
