# Changelog

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.1.0] - Unreleased

### Added
- Initial public release.
- `validate()` bridge to `@secvisogram/csaf-validator-lib` that never raises and reports an explicit
  unavailable state.
- `ValidationResult` with `available`, `is_valid`, `errors`, `note` and `conclusive`.
- `csaf-check` CLI with human and JSON output, stdin support and `--require-validator`.
- Synthetic valid and invalid advisory fixtures.
- CI covering both the degradation path and real validation with the library installed.
