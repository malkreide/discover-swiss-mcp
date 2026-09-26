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
- **Network binding.** See «HTTP transport» below: loopback by default, and
  any other bind address is refused unless OAuth and an exact host list are
  configured.

## HTTP transport

stdio is the default and has no network surface. The Streamable HTTP
transport is decided in one place, `src/discover_swiss_mcp/http_app.py`, and
every rule below is enforced at start-up — a misconfiguration stops the
process with exit code 2 instead of starting a weaker server.

| Bind address | Needs | Host / Origin check |
|---|---|---|
| `127.0.0.1`, `localhost`, `::1` (default) | nothing | exact `host:port`: `127.0.0.1:<port>`, `localhost:<port>`, `[::1]:<port>` — another port is refused (421) |
| anything else (`0.0.0.0`, a LAN or container address) | inbound OAuth **and** `DISCOVER_SWISS_MCP_ALLOWED_HOSTS` | exactly the listed `host:port` values; browser origins only if listed in `DISCOVER_SWISS_MCP_ALLOWED_ORIGINS` |

A non-loopback start is logged as the warning `http_bind_non_loopback`.
`DISCOVER_SWISS_MCP_ALLOWED_HOSTS` takes exact values and refuses wildcards.
A name without a port (`mcp.example.ch`) is exact as well: it is the Host a
client sends for the default port, e.g. behind an HTTPS ingress.
Ingress names come from the environment on purpose — the name a deployment is
reached under depends on its domain and proxy. Egress is the opposite, see
[docs/network-egress.md](docs/network-egress.md).

## Inbound OAuth (HTTP transport)

The server acts as an OAuth **resource server**; the operator's authorization
server issues the tokens. Enabled by setting all five variables — half a
configuration is refused:

| Variable | Meaning |
|---|---|
| `DISCOVER_SWISS_MCP_AUTH_ISSUER` | Issuer URL of the authorization server (`https://`) |
| `DISCOVER_SWISS_MCP_AUTH_RESOURCE_URL` | This server's resource identifier, e.g. `https://mcp.example.ch/mcp` |
| `DISCOVER_SWISS_MCP_AUTH_INTROSPECTION_URL` | Token introspection endpoint (RFC 7662, `https://`) |
| `DISCOVER_SWISS_MCP_AUTH_CLIENT_ID` | Client this server introspects as |
| `DISCOVER_SWISS_MCP_AUTH_CLIENT_SECRET` | Its secret — held as `SecretStr`, never logged |

What happens per request (`src/discover_swiss_mcp/auth.py`):

1. `GET /.well-known/oauth-protected-resource` and
   `/.well-known/oauth-protected-resource/mcp` (RFC 9728) name the resource,
   the authorization server and **all** supported scopes. No token needed.
2. Every other request needs `Authorization: Bearer …`. The token is checked by
   introspection: active, not expired, `iss` equal to the configured issuer
   when present, and `aud` containing the resource URL (RFC 8707). A token
   issued for another service is refused even if it is valid there. Answers
   are cached for at most 60 seconds and never beyond the token's expiry; an
   authorization server that cannot be reached lets nothing through.
3. The scopes are checked **per call**, from the JSON-RPC body (not only from
   the client-supplied routing headers).
4. Missing or invalid token: `401`. Too few scopes: `403` with
   `WWW-Authenticate: Bearer error="insufficient_scope", scope="…",
   resource_metadata="…"`, so a client can ask for exactly the missing scope.

### Scopes

Two dimensions — access (read/write) and data class — with the entry scope
kept minimal:

| Scope | Grants |
|---|---|
| `mcp:tools-basic` | Discovery: initialise, list tools, ping, `source_status`. The scope a first authorisation needs. |
| `tourism:read:public` | Every tool that returns index content. |

| Tool | Required scopes |
|---|---|
| `source_status` | `mcp:tools-basic` |
| `search`, `get_details`, `find_accommodation`, `find_tours`, `find_events`, `webcams_near`, `explore_area` | `mcp:tools-basic` `tourism:read:public` |

There is **no write scope and no admin scope**, because there is no tool that
writes and no administrative operation. The data class is only `public`:
objects under a non-open licence are withheld for every caller, so no scope
could unlock them. A tool call for an unknown name needs the read scope (fail
closed). A test holds that every registered tool has an entry in the table.

## Container

A hardened image and Kubernetes manifests are in `Dockerfile` and `deploy/`:
non-root UID 10001, read-only root filesystem with a tmpfs `/tmp`, all
capabilities dropped, no privilege escalation, seccomp `RuntimeDefault`, and a
NetworkPolicy that allows egress only to TCP 443 outside private ranges plus
DNS. Details and the run commands are in
[docs/network-egress.md](docs/network-egress.md).

## Supported versions

This project is pre-release. Only the current `main` receives fixes.
