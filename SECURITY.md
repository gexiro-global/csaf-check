# Security Policy

## Supported Versions

`csaf-check` v0.x is maintained on the latest v0.x release line.

## Reporting a Vulnerability

Use GitHub private vulnerability reporting if enabled on this repository, otherwise email
`admin@gexiro.com`.

Include the `csaf-check` version, your Python and Node.js versions, and a minimal synthetic
document that reproduces the issue. Do not send unpublished advisories or embargoed vulnerability
details.

## Threat model

`validate()` writes the document you pass it to a temporary file and executes `node` on a bundled
script with that path as its only argument. The document is never interpolated into a shell
command. The temporary directory is removed afterwards.

Two things worth stating plainly:

- Advisory documents can be large or deeply nested. The Node process is bounded by a timeout
  (40 s by default) but not by a memory limit. Do not feed it untrusted multi-megabyte input where
  a memory spike matters.
- Validation runs `node` from `PATH`. Where `PATH` is attacker-controlled, that is code execution.
  This is true of anything that shells out, but you should know it is happening.

The package makes no network connections.
