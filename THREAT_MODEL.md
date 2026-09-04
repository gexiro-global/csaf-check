# Threat model

csaf-check parses attacker-controlled JSON and invokes a local Node.js validator. The primary risks are resource exhaustion, malformed validator output, executing an attacker-selected `node` from `PATH`, accidental disclosure of unpublished advisories and a misleading conclusive verdict when the validator is unavailable.

The implementation passes the temporary path as a process argument without shell interpolation, bounds validator runtime, removes the temporary directory and represents validator absence explicitly. Operators must use a trusted runtime and dependencies, apply their own input-size limit, avoid untrusted or embargoed documents in shared CI logs and use `--require-validator` where an inconclusive result must fail.

The project performs no network discovery and makes no claim that schema validity proves advisory correctness.
