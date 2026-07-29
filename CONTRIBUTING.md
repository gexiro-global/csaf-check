# Contributing

Bug reports with a minimal synthetic advisory are the most useful contribution.

## Ground rules

- **`validate()` must never raise.** That is the whole point of the package. A pull request that
  lets an exception escape will be closed, however unlikely the path looks.
- No runtime Python dependencies. The standard library covers what this does.
- Do not reimplement CSAF schema logic in Python. If a test is missing, it belongs upstream in
  `@secvisogram/csaf-validator-lib`.
- Every fixture must be synthetic: fictional vendor, fictional product, placeholder CVE id.
- The suite must keep passing on a machine with no Node.js installed.

## Support expectations

Best-effort maintenance, no SLA, no commercial support. This is a thin bridge; the substance lives
in the upstream validator, and that is where schema questions belong.
