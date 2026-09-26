"""The container and Kubernetes artefacts keep their hardening (audit SEC-007, SEC-021).

These are static checks of the files in the repository. The runtime behaviour
— UID, read-only root, capabilities, seccomp — was measured on a built image
and is recorded in docs/network-egress.md; these tests make sure the files
that produced it do not quietly lose a setting.
"""

from __future__ import annotations

import ipaddress
import re
from pathlib import Path

import pytest
import yaml

from discover_swiss_mcp.config import AUTH_VARIABLES
from discover_swiss_mcp.net import EGRESS_ALLOWLIST

ROOT = Path(__file__).resolve().parent.parent
K8S = ROOT / "deploy" / "k8s"


def _docs(name: str) -> list[dict]:
    return [d for d in yaml.safe_load_all((K8S / name).read_text(encoding="utf-8")) if d]


def _deployment() -> dict:
    (deployment,) = [d for d in _docs("deployment.yaml") if d["kind"] == "Deployment"]
    return deployment


# ---------------------------------------------------------------------------
# Dockerfile
# ---------------------------------------------------------------------------


def test_dockerfile_runs_as_an_unprivileged_numeric_user() -> None:
    text = (ROOT / "Dockerfile").read_text(encoding="utf-8")
    users = re.findall(r"^USER\s+(\S+)", text, re.M)
    assert users, "no USER instruction"
    uid, _, gid = users[-1].partition(":")
    # Numeric, so Kubernetes `runAsNonRoot` can verify it without a passwd lookup.
    assert uid.isdigit() and int(uid) >= 10000
    assert gid.isdigit() and int(gid) >= 10000


def test_dockerfile_pins_the_base_image_by_digest() -> None:
    text = (ROOT / "Dockerfile").read_text(encoding="utf-8")
    images = re.findall(r"^FROM\s+(\S+)", text, re.M)
    assert len(images) == 2
    # Literal, not through an ARG: Dependabot does not resolve build args.
    assert all(re.search(r"^[\w./-]+:[\w.-]+@sha256:[0-9a-f]{64}$", i) for i in images), images
    assert len(set(images)) == 1


def test_dockerfile_allows_a_read_only_root() -> None:
    text = (ROOT / "Dockerfile").read_text(encoding="utf-8")
    assert "PYTHONDONTWRITEBYTECODE=1" in text
    assert re.search(r"^ENTRYPOINT \[\"python\", \"-m\", \"discover_swiss_mcp\"\]", text, re.M)


def test_the_build_context_is_deny_by_default() -> None:
    lines = [
        line.strip()
        for line in (ROOT / ".dockerignore").read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]
    assert lines[0] == "*"
    assert not [line for line in lines if ".env" in line and line.startswith("!")]


# ---------------------------------------------------------------------------
# Kubernetes deployment
# ---------------------------------------------------------------------------


def test_pod_security_context() -> None:
    pod = _deployment()["spec"]["template"]["spec"]
    assert pod["automountServiceAccountToken"] is False
    context = pod["securityContext"]
    assert context["runAsNonRoot"] is True
    assert context["runAsUser"] >= 10000
    assert context["seccompProfile"]["type"] == "RuntimeDefault"


def test_container_security_context() -> None:
    (container,) = _deployment()["spec"]["template"]["spec"]["containers"]
    context = container["securityContext"]
    assert context["allowPrivilegeEscalation"] is False
    assert context["readOnlyRootFilesystem"] is True
    assert context["privileged"] is False
    assert context["capabilities"]["drop"] == ["ALL"]
    assert "add" not in context["capabilities"]
    assert context["seccompProfile"]["type"] == "RuntimeDefault"


def test_tmp_is_a_bounded_memory_volume() -> None:
    pod = _deployment()["spec"]["template"]["spec"]
    (container,) = pod["containers"]
    mounts = {m["name"]: m["mountPath"] for m in container["volumeMounts"]}
    assert mounts == {"tmp": "/tmp"}
    (volume,) = pod["volumes"]
    assert volume["emptyDir"]["medium"] == "Memory"
    assert volume["emptyDir"]["sizeLimit"]


def test_the_deployment_satisfies_the_bind_policy_and_keeps_secrets_out() -> None:
    """0.0.0.0 needs OAuth and a host list, or the server refuses to start."""
    (container,) = _deployment()["spec"]["template"]["spec"]["containers"]
    env = {e["name"]: e for e in container["env"]}
    assert env["DISCOVER_SWISS_MCP_HOST"]["value"] == "0.0.0.0"
    assert env["DISCOVER_SWISS_MCP_ALLOWED_HOSTS"]["value"]
    assert set(AUTH_VARIABLES.values()) <= set(env)
    for secret in ("DISCOVER_SWISS_KEY", "DISCOVER_SWISS_MCP_AUTH_CLIENT_SECRET"):
        assert "value" not in env[secret], f"{secret} must come from a Secret"
        assert env[secret]["valueFrom"]["secretKeyRef"]["name"]


# ---------------------------------------------------------------------------
# Network policies
# ---------------------------------------------------------------------------

MUST_EXCLUDE = ["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16", "127.0.0.0/8", "169.254.0.0/16"]


def test_networkpolicy_allows_only_dns_and_public_https() -> None:
    (policy,) = _docs("networkpolicy.yaml")
    spec = policy["spec"]
    assert "Egress" in spec["policyTypes"]
    rules = spec["egress"]
    ports = sorted((p["protocol"], p["port"]) for rule in rules for p in rule["ports"])
    assert ports == [("TCP", 53), ("TCP", 443), ("UDP", 53)]

    (https,) = [r for r in rules if any(p["port"] == 443 for p in r["ports"])]
    (block,) = [t["ipBlock"] for t in https["to"]]
    assert block["cidr"] == "0.0.0.0/0"
    excluded = [ipaddress.ip_network(c) for c in block["except"]]
    for cidr in MUST_EXCLUDE:
        assert any(ipaddress.ip_network(cidr).subnet_of(e) for e in excluded), cidr

    (dns,) = [r for r in rules if any(p["port"] == 53 for p in r["ports"])]
    assert dns["to"][0]["podSelector"]["matchLabels"]["k8s-app"] == "kube-dns"


def test_cilium_policy_names_exactly_the_allowed_hosts() -> None:
    """Update procedure step 5: code allow-list and host-name policy agree."""
    (policy,) = _docs("cilium-networkpolicy.yaml")
    egress = policy["spec"]["egress"]
    fqdns = {f["matchName"] for rule in egress for f in rule.get("toFQDNs", [])}
    dns_names = {
        d["matchName"]
        for rule in egress
        for port in rule.get("toPorts", [])
        for d in port.get("rules", {}).get("dns", [])
    }
    # The introspection host is deployment-specific and stands in as a placeholder.
    assert fqdns - {"login.example.ch"} == set(EGRESS_ALLOWLIST)
    assert dns_names == fqdns


@pytest.mark.parametrize("host", sorted(EGRESS_ALLOWLIST))
def test_every_allowed_host_is_documented(host: str) -> None:
    text = (ROOT / "docs" / "network-egress.md").read_text(encoding="utf-8")
    assert f"`{host}`" in text
