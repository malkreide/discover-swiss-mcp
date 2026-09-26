# syntax=docker/dockerfile:1
#
# Hardened image for discover-swiss-mcp (audit SEC-007).
#
# What the image guarantees on its own: a non-root user (UID/GID 10001) with no
# login shell, no build tools, no pip cache, and no bytecode writes at runtime,
# so the root filesystem can be mounted read-only. What the runtime must add —
# read-only root, tmpfs /tmp, dropped capabilities, no privilege escalation,
# seccomp — is spelled out in docs/network-egress.md (docker run) and
# deploy/k8s/deployment.yaml (Kubernetes).
#
# Default transport is stdio (`docker run -i`). The HTTP transport binds to
# 0.0.0.0 inside a container and therefore needs inbound OAuth and
# DISCOVER_SWISS_MCP_ALLOWED_HOSTS; the server refuses to start without them.
#
# The base image is pinned by digest: a tag moves, a digest does not.
# Dependabot (docker ecosystem) proposes digest updates. Written out in both
# FROM lines rather than through an ARG, which Dependabot does not resolve.

FROM python:3.12-slim@sha256:f77ac9e44ae96ef2c90b8053ea08c31f8be030f824196b0ae4db6d462c84e51f AS build
ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /src
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
# Behind a TLS-inspecting proxy, pass its CA as a build secret:
#   docker build --secret id=ca_bundle,src=/path/to/ca.pem .
# A secret mount exists only for this step and never enters a layer.
RUN --mount=type=secret,id=ca_bundle,required=false \
    if [ -f /run/secrets/ca_bundle ]; then export PIP_CERT=/run/secrets/ca_bundle; fi \
    && python -m venv /opt/venv \
    && /opt/venv/bin/pip install . \
    # find_events computes «today» in Europe/Zurich; fail the build, not the
    # first request, if the zone database is missing.
    && /opt/venv/bin/python -c "import zoneinfo; zoneinfo.ZoneInfo('Europe/Zurich')" \
    && /opt/venv/bin/python -m compileall -q /opt/venv

FROM python:3.12-slim@sha256:f77ac9e44ae96ef2c90b8053ea08c31f8be030f824196b0ae4db6d462c84e51f AS runtime
RUN groupadd --gid 10001 mcp \
    && useradd --uid 10001 --gid 10001 --no-create-home --home-dir /nonexistent \
       --shell /usr/sbin/nologin mcp
COPY --from=build /opt/venv /opt/venv
ENV PATH=/opt/venv/bin:$PATH \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
USER 10001:10001
WORKDIR /tmp
ENTRYPOINT ["python", "-m", "discover_swiss_mcp"]
