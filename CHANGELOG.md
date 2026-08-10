# Changelog

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

- No unreleased changes.

## [0.1.1] - 2026-08-10

- Ship the inline type-information marker and explicit license-file metadata.
- Bound build and development dependencies to tested next-major ceilings and add complete
  license, audience, Python, security-topic, and typed-package classifiers.

## [0.1.0] - 2026-08-01

### Added
- Initial public release.
- `validate()` bridge to `@secvisogram/csaf-validator-lib` that never raises and reports an explicit
  unavailable state.
- `ValidationResult` with `available`, `is_valid`, `errors`, `note` and `conclusive`.
- `csaf-check` CLI with human and JSON output, stdin support and `--require-validator`.
- Synthetic valid and invalid advisory fixtures.
- CI covering both the degradation path and real validation with the library installed.

### Notes
- Verified end to end against `@secvisogram/csaf-validator-lib` 2.1.1: the library exposes subpath
  exports only (no main entry), `validate` is the default export of `validate.js`, and the mandatory
  tests are individually-named exports of `mandatoryTests.js`.
- The bridge is shipped as `.cjs` so its module type is unambiguous wherever the Python package is
  installed, and it resolves the validator from the package directory, the working directory, or
  `NODE_PATH`.
- An empty resolved test list is treated as "no verdict" rather than "valid", so a library API change
  can never silently report a broken advisory as clean.
