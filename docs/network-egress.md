# Network egress and container hardening

Where this server may send requests, how that is enforced at two layers, and
how to run it in a sandbox. Audit references: SEC-021 (egress), SEC-007
(container), SEC-004 (SSRF).

## Allowed hosts

| Host | Purpose | Code layer | Network layer |
|---|---|---|---|
| `api.discover.swiss` | The Infocenter API — the only data source | `EGRESS_ALLOWLIST` in `src/discover_swiss_mcp/net.py` (a `frozenset`) | `deploy/k8s/networkpolicy.yaml` (TCP 443 to public ranges), `deploy/k8s/cilium-networkpolicy.yaml` (by name) |
| the introspection host of your authorization server | Token introspection, **only** when inbound OAuth is configured | a one-element `frozenset` built at start-up from `DISCOVER_SWISS_MCP_AUTH_INTROSPECTION_URL` (`src/discover_swiss_mcp/auth.py`); never extended at runtime | same two policies; in the Cilium policy replace `login.example.ch` |
| the cluster DNS resolver | Name resolution | — | DNS rule in both policies |

Every outbound request, to either host, goes through the same chain in
`net.safe_request`: HTTPS only, host on the allow-list, every resolved address
checked against private, loopback, link-local (cloud metadata), multicast and
reserved ranges — IPv4-mapped, 6to4 and Teredo forms unwrapped first — and the
connection pinned to the checked address, so a second DNS lookup cannot
redirect it. Redirects are re-checked hop by hop; a redirect on a POST is
refused.

## The two layers

**Code layer.** The allow-list is a `frozenset` in the source. It is not read
from the environment: an operator must not be able to widen where the server
talks to without a code review. The one exception — the introspection host —
comes from configuration because it is the operator's own authorization
server, and it is frozen at start-up.

**Network layer.** In Kubernetes, `deploy/k8s/networkpolicy.yaml` allows DNS to
`kube-dns` and TCP 443 to public addresses only; every private,
link-local and CGNAT range is excluded. A standard NetworkPolicy cannot match
host names, so which public host is contacted stays the code layer's job. On
clusters with Cilium, `deploy/k8s/cilium-networkpolicy.yaml` narrows this to
the two names (`toFQDNs`); Cilium learns their addresses from the DNS answers
it proxies, which is why its DNS rule must stay.

**DNS path.** Both policies allow UDP and TCP 53 to the cluster resolver. Without
that rule every call fails at name resolution — which the server reports as
`upstream_unreachable` after its retries, not as a policy block.

Outside Kubernetes — a laptop, a VM — there is no network-layer control in this
repository. A local stdio process is started by the user's own MCP host; if
that environment needs egress control, it belongs to the host firewall or a
proxy, and the table above is the list to allow.

## Update procedure

Adding a host is a reviewed change in one pull request:

1. Add it to `EGRESS_ALLOWLIST` in `src/discover_swiss_mcp/net.py`, with a
   comment saying why.
2. Add it to `deploy/k8s/cilium-networkpolicy.yaml` (both the DNS rule and
   `toFQDNs`); check that `deploy/k8s/networkpolicy.yaml` still covers it
   (a public address on 443).
3. Add a row to the table above.
4. Add a CHANGELOG entry under «Changed».
5. `tests/test_deploy.py` checks that the Cilium policy and the code allow-list
   agree; it fails until both are updated.

## Running the container

The image (`Dockerfile`) runs as UID/GID 10001 with no login shell and writes
no bytecode, so the root filesystem can be read-only. The runtime adds the
rest. Build:

```bash
docker build -t discover-swiss-mcp .
# behind a TLS-inspecting proxy:
docker build --secret id=ca_bundle,src=/path/to/proxy-ca.pem -t discover-swiss-mcp .
```

Run — stdio, the default, e.g. from an MCP host:

```bash
docker run -i --rm \
  --read-only --tmpfs /tmp:rw,noexec,nosuid,size=16m \
  --cap-drop ALL --security-opt no-new-privileges \
  -e DISCOVER_SWISS_KEY \
  discover-swiss-mcp
```

Docker applies its default seccomp profile unless it is switched off; do not
pass `--security-opt seccomp=unconfined`.

Claude Desktop (`claude_desktop_config.json`), with the key taken from the
environment Claude Desktop is started in:

```json
{
  "mcpServers": {
    "discover-swiss": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "--read-only", "--tmpfs", "/tmp:rw,noexec,nosuid,size=16m",
        "--cap-drop", "ALL", "--security-opt", "no-new-privileges",
        "-e", "DISCOVER_SWISS_KEY",
        "discover-swiss-mcp"
      ]
    }
  }
}
```

The HTTP transport inside a container binds to `0.0.0.0`, and the server
refuses that without inbound OAuth and `DISCOVER_SWISS_MCP_ALLOWED_HOSTS` (see
SECURITY.md). `deploy/k8s/deployment.yaml` sets both.

## Verified on 2026-09-26

Image built from this repository (base `python:3.12-slim`, pinned by digest)
and run with the flags above:

| Check | Result |
|---|---|
| `id` | `uid=10001(mcp) gid=10001(mcp)` |
| write to `/` and `/opt/venv` | `Read-only file system` |
| write to `/tmp` | allowed |
| `CapPrm` / `CapEff` | `0000000000000000` |
| `NoNewPrivs` | `1` (counter-check without the flag: `0`) |
| `Seccomp` | `2`, filter active (counter-check with `seccomp=unconfined`: `0`) |
| `initialize` + `tools/list` over stdio with `--network none` | all eight tools listed |
