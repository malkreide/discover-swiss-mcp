# Security Policy

## Reporting a vulnerability

Report security issues through GitHub's private vulnerability reporting:
[Report a vulnerability](https://github.com/malkreide/discover-swiss-mcp/security/advisories/new).

Please do not open a public issue for a security problem. Expect a first
response within five working days.

## The subscription key

The discover.swiss Infocenter Open is bring-your-own-key. `DISCOVER_SWISS_KEY`
is read from the environment and from nowhere else.

- It is held as a `SecretStr`, so `repr()`, `str()`, `model_dump_json()` and
  any structlog event render it as `**********`. A test asserts this.
- It is unwrapped in exactly one place — the outbound
  `Ocp-Apim-Subscription-Key` header.
- It must never appear in a committed file. `.gitignore` covers `.env`,
  `.env.*`, `*.key`, `*.pem`, `credentials.json`, `secrets.yaml` and
  `config.local.*`.
- **If a key has been pushed, rotate it first.** A pushed secret is
  compromised even after deletion — forks, caches and crawlers keep it.
  Cleaning the history comes second, not first.

## Scope and posture

- **Read-only.** Every tool carries `readOnlyHint: true`. The server performs
  no writes against discover.swiss and holds no user data.
- **Open world.** Every tool carries `openWorldHint: true`: results come from a
  live third-party API whose content the server does not control.
- **Third-party text.** Descriptions, opening hours and provider names come
  from external providers and are data, not instructions. Treat them as
  untrusted input in whatever consumes the output.
- **Logging.** structlog writes JSON to stderr; stdout belongs to the JSON-RPC
  stream. Error details are masked towards the model and kept in the server
  log.
- **Network binding.** The HTTP transport binds to loopback by default. A
  non-loopback bind needs an explicit host allow-list, otherwise DNS rebinding
  protection cannot be applied.

## Supported versions

This project is pre-release. Only the current `main` receives fixes.
