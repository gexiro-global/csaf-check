# Security and trust evidence

This page is an evidence index, not a certification. The evidence does not prove the project is vulnerability-free, does not establish a SLSA level, and does not imply OpenSSF affiliation or endorsement. Tool output describes observed posture; it is not proof of compromise or absence of compromise.

- [Security policy](../SECURITY.md) and [threat model](../THREAT_MODEL.md)
- [Contribution process](../CONTRIBUTING.md), [governance](../GOVERNANCE.md), [maintainers](../MAINTAINERS.md) and [support](../SUPPORT.md)
- CI tests both the no-validator degradation path and the packaged wheel with the real JavaScript validator.
- CodeQL, dependency review, Dependabot and OpenSSF Scorecard are configured in `.github/`.
- Third-party actions are pinned to immutable commit SHAs with version comments.

The Scorecard badge is intentionally withheld until a successful default-branch run has produced a public API result. `.bestpractices.json` contains evidence-backed automation proposals only; it is not an OpenSSF Best Practices or OSPS Baseline claim. A human must review any badge submission.
