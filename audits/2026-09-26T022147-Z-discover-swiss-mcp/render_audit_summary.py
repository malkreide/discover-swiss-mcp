"""Render audits/AUDIT_2026-09-26.md and the CHANGELOG findings table.

Every number comes from summary.json, verification-results-local.json or
dispositions.json — nothing is typed by hand (mcp-audit, step 6.1). The prose
around the tables is fixed text in this file.

Usage (from the repository root):
    python audits/2026-09-26T022147-Z-discover-swiss-mcp/render_audit_summary.py
Writes:
    audits/AUDIT_2026-09-26.md
    audits/2026-09-26T022147-Z-discover-swiss-mcp/changelog-findings.md
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

RUN = Path(__file__).resolve().parent
OUT = RUN.parent / "AUDIT_2026-09-26.md"
OUT_CHANGELOG = RUN / "changelog-findings.md"
RUN_NAME = RUN.name

SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}
KIND_DE = {
    "fix-before-release": "vor Release",
    "fix-later": "später",
    "accepted": "akzeptiert",
    "fixed": "behoben",
}
KIND_EN = {
    "fix-before-release": "fix before release",
    "fix-later": "planned",
    "accepted": "accepted",
    "fixed": "fixed",
}


def load(name: str) -> dict:
    return json.loads((RUN / name).read_text(encoding="utf-8"))


def main() -> int:
    summary = load("summary.json")
    results = load("verification-results.json")["results"]
    local = load("verification-results-local.json")["results"]
    dispositions = {k: v for k, v in load("dispositions.json").items() if not k.startswith("_")}
    meta = load("audit-meta.json")["audit_meta"]
    applicability = load("applicability.json")

    totals = summary["totals"]
    by_status = totals["by_status"]
    sev = totals["by_severity_among_findings"]
    blocking = summary["blocking_findings"]
    advisory = summary["advisory_findings"]
    not_verified = summary["not_verified_findings"]
    finding_ids = summary["findings"]["expected_ids"]
    dropped = sorted(
        k for k, v in applicability.items() if str(v.get("reason", "")).startswith("baseline")
    )
    local_findings = [k for k, v in local.items() if v["status"] in ("fail", "partial")]

    listed = finding_ids + not_verified + local_findings
    kinds = Counter(dispositions[k][0] for k in listed)

    def row(cid: str, result: dict) -> str:
        kind, reason = dispositions[cid]
        flag = " **blockierend**" if cid in blocking else ""
        flag += " (advisory)" if cid in advisory else ""
        return (
            f"| `{cid}` | {result['severity']} | {result['status']}{flag} | "
            f"{KIND_DE[kind]} | {reason} |"
        )

    ordered = sorted(finding_ids, key=lambda c: (SEVERITY_ORDER[results[c]["severity"]], c))

    md: list[str] = []
    md += [
        "# Audit discover-swiss-mcp — 26.09.2026",
        "",
        f"Vollständiger Durchlauf nach dem `mcp-audit`-Skill (Version {meta['skill_version']}), "
        f"Katalog-Hash `{meta['catalog_hash'][:12]}`, Ziel-Revision `{meta['target_sha'][:7]}` "
        f"(Branch `{meta['target_branch']}`, inzwischen in `main`). Lauf-Verzeichnis mit "
        f"Rohdaten, Finding-Dokumenten und dem generierten Detail-Report: "
        f"[`{RUN_NAME}/`]({RUN_NAME}/audit-report.md).",
        "",
        "## Executive Summary",
        "",
        f"Geprüft wurden {totals['applicable']} anwendbare Katalog-Checks: "
        f"{by_status['pass']} bestanden, {by_status['partial']} teilweise, "
        f"{by_status['fail']} nicht bestanden, {by_status['not_verified']} nicht verifizierbar — "
        f"{len(finding_ids)} Findings ({sev['critical']} critical, {sev['high']} high, "
        f"{sev['medium']} medium, {sev['low']} low). "
        f"**Production-ready: nein** — {len(blocking)} blockierende Findings "
        f"({', '.join(blocking)}); dazu {len(advisory)} advisory-Findings auf "
        f"blockierender Severity ({', '.join(advisory)}). "
        "Der Datentreue-Kern (Lizenz-Gate, Testobjekt-Filter, HTML-Bereinigung, Scope-Parameter, "
        "Leermengen-Hints) hält; die Lücken liegen in der Härtung des HTTP-Transports, im "
        "SSRF-Detail (IPv4-mapped IPv6), in der Durchsetzung von Protokoll-Pin und Serverversion "
        "sowie in fehlenden Live-Canaries für Status- und Fallback-Endpoints.",
        "",
        "Nicht verifizierbar: " + ", ".join(f"`{c}`" for c in not_verified) + ". "
        "Sie zählen weder als bestanden noch als gescheitert und stehen unten mit Grund.",
        "",
        "## Stand der Dispositionen",
        "",
        "| Disposition | Anzahl |",
        "|---|---:|",
    ]
    for kind in ("fix-before-release", "fix-later", "accepted", "fixed"):
        md.append(f"| {KIND_DE[kind]} | {kinds.get(kind, 0)} |")
    md += [
        "",
        "«vor Release» heisst: Die Behebung ist Bedingung für den ersten Release, zusätzlich "
        "zum Release-Gate der Search-Bestätigung. «akzeptiert» trägt immer eine Begründung. "
        "Jede Zeile steht mit derselben Begründung im CHANGELOG (Abschnitt «Audit findings»).",
        "",
        "## Profil",
        "",
        "Im Notion-Audit-Tracker existierte keine Karte für diesen Server; das Profil wurde "
        "aus dem Repository abgeleitet und mit `validate_profile.py` geprüft (konsistent).",
        "",
        "| Feld | Wert |",
        "|---|---|",
        "| transport | dual (stdio, Streamable HTTP auf 127.0.0.1) |",
        "| sdk_language | Python (`mcp` 2.x) |",
        "| mcp_spec_version | 2026-07-28 |",
        "| auth_model | API-Key (Bring-your-own-Upstream-Key; kein eingehender Schutz) |",
        "| data_class | Public Open Data |",
        "| write_capable | false |",
        "| deployment | local-stdio |",
        "| tools_make_external_requests | true |",
        "",
        f"Spec-Baseline: {len(dropped)} Checks entfallen, weil sie nur für 2025-11-25 gelten: "
        + ", ".join(f"`{c}`" for c in dropped)
        + ".",
        "",
        "## Findings nach Severity",
        "",
        "| Check | Severity | Befund | Disposition | Begründung / Massnahme |",
        "|---|---|---|---|---|",
    ]
    md += [row(c, results[c]) for c in ordered]
    md += [
        "",
        "## Nicht verifizierbar",
        "",
        "| Check | Severity | Grund |",
        "|---|---|---|",
    ]
    md += [f"| `{c}` | {results[c]['severity']} | {dispositions[c][1]} |" for c in not_verified]
    md += [
        "",
        "## FID — vier serverspezifische Checks",
        "",
        "Verlangt für P4: Lizenz-Whitelist, Facetten-Vollständigkeit, Testobjekte, HTML. Nach "
        "§2.5 des Skills («Reichweite vor neuer Regel») zuerst gegen den Katalog gehalten: "
        "`FID-L01` und `FID-L03` verengen `FID-003` (eine Filterung ohne Zähler ist eine "
        "stille Leermenge), `FID-L02` verengt `FID-006` auf die Facetten-Keys, nur `FID-L04` "
        "(Kodierung ausgelieferter Texte) fragt etwas, das kein Katalog-Check fragt. Sie "
        "laufen deshalb **neben** dem Katalog — Definitionen in "
        f"[`{RUN_NAME}/checks-local/`]({RUN_NAME}/checks-local/), Ergebnisse in "
        "`verification-results-local.json` —, damit der Katalog-Hash nur verbürgt, was im "
        "Katalog steht. Ein Vorschlag an das Skill-Repo wäre allenfalls `FID-L04`.",
        "",
        "| Check | Titel | Severity | Befund | Disposition |",
        "|---|---|---|---|---|",
    ]
    titles = {
        "FID-L01": "Lizenz-Whitelist greift",
        "FID-L02": "Facetten-Antwort vollständig oder gemeldet",
        "FID-L03": "Testobjekte gefiltert und gezählt",
        "FID-L04": "HTML gestrippt, Entities aufgelöst",
    }
    for cid in sorted(local):
        result = local[cid]
        disp = dispositions.get(cid)
        disp_text = f"{KIND_DE[disp[0]]}: {disp[1]}" if disp else "—"
        md.append(
            f"| `{cid}` | {titles[cid]} | {result['severity']} | {result['status']} | {disp_text} |"
        )
    md += [
        "",
        "Bestanden: "
        + ", ".join(f"`{k}`" for k, v in sorted(local.items()) if v["status"] == "pass")
        + "; teilweise: "
        + ", ".join(f"`{k}`" for k, v in sorted(local.items()) if v["status"] == "partial")
        + "; nicht bestanden: "
        + (
            ", ".join(f"`{k}`" for k, v in sorted(local.items()) if v["status"] == "fail")
            or "keiner"
        )
        + ".",
        "",
        "## Befunde über den Katalog",
        "",
        "- **`auth_model: API-Key` ist doppeldeutig.** Der Katalog wertet es als «irgendeine "
        "Authentisierung konfiguriert» und zieht damit `SEC-002`, `SEC-003` und `SEC-026` "
        "(eingehendes OAuth) heran. Hier ist es ein Bring-your-own-**Upstream**-Key; eingehend "
        "hat der Server keinen Schutz. Das Profil war vor dem Lauf festgelegt und wurde nicht "
        "nachträglich geändert — die Findings stehen, ihre Disposition sagt, warum sie "
        "akzeptiert sind. Frage an das Skill-Repo: ein eigener Wert `upstream-key`?",
        "- **Nummerierung DRIFT.** Der Vergleich CHANGELOG gegen Code ist `DRIFT-006`, nicht "
        "`DRIFT-008`; beide wurden nach ihrer Katalog-Definition geprüft.",
        "",
        "## Abweichungen vom Verfahren",
        "",
        "- **Ziel-Prüfung mit `--skip-target-check`.** Das Lauf-Verzeichnis liegt im "
        "auditierten Repo und macht den Worktree «dirty», obwohl HEAD unverändert "
        f"`{meta['target_sha'][:7]}` ist. Belegt: `git status --short --untracked-files=all "
        "-- . ':!audits'` liefert 0 Zeilen (Negativkontrolle mit einer Testdatei: 1 Zeile). "
        "Kein Check hat etwas anderes als den Commit gesehen.",
        "- **Profil ohne Tracker-Karte**, siehe «Profil».",
        "- **Live-Verhalten nicht reproduziert.** Die Sandbox verbietet ausgehende Verbindungen "
        "per IP; der Client pinnt DNS und umgeht damit den Proxy. Live-Kriterien stützen sich "
        "auf die aufgezeichneten Probe-Antworten; die Live-Canaries (`tests/test_live.py`) "
        "sind geschrieben, aber zum Audit-Zeitpunkt nicht ausgeführt.",
        "- **Evidenz-Gate.** `OPS-010` trug beim ersten Aggregieren 2 statt 3 Belege; der dritte "
        "(`tests/test_client.py:384`, globaler Patch von `time.monotonic`) wurde vom "
        "Report-Autor nachgelesen und aus `gaps` nach `evidence` übernommen.",
        "- **Stichproben.** Drei Befunde wurden vom Report-Autor unabhängig nachgemessen: "
        "`SEC-004` (`::ffff:169.254.169.254` und `::ffff:127.0.0.1` gelten als nicht "
        "gesperrt), `ARCH-016` (`MCPServer.version == ''`), `ARCH-012` (kein Test gegen "
        "`LATEST_PROTOCOL_VERSION`, obwohl `server.py:69-72` ihn behauptet).",
        "- **Secrets-Scan.** `gitleaks` war in dieser Umgebung nicht beziehbar; geprüft wurde "
        "mit `git grep` auf Key-Muster (Negativkontrolle schlägt an). `detect-secrets` erkannte "
        "die Negativkontrolle nicht und zählt deshalb nicht als Beleg.",
        "",
        "## Metadaten",
        "",
        "| Feld | Wert |",
        "|---|---|",
        f"| Run-ID | `{meta['run_id']}` |",
        f"| Start | {meta['started_at']} |",
        f"| Skill-Version | {meta['skill_version']} |",
        f"| Katalog-Hash | `{meta['catalog_hash']}` |",
        f"| Ziel | `{meta['target_sha']}` |",
        "| Policy | fail-or-partial |",
        "| Ausführung | vier Prüf-Agenten nach Kategorie, je Lauf durch `verify_raw_outputs.py` "
        "und `agent_run_log.py` gegated (alle `ok`, keine Wiederholung) |",
        "",
    ]
    OUT.write_text("\n".join(md), encoding="utf-8")

    cl: list[str] = [
        "### Audit findings (2026-09-26)",
        "",
        f"Full mcp-audit run against `{meta['target_sha'][:7]}`: "
        f"{totals['applicable']} applicable checks, {by_status['pass']} pass, "
        f"{by_status['partial']} partial, {by_status['fail']} fail, "
        f"{by_status['not_verified']} not verified; four server-specific FID checks "
        "(" + ", ".join(f"{k} {v['status']}" for k, v in sorted(local.items())) + "). "
        "Report: `audits/AUDIT_2026-09-26.md`. Not production-ready. Every open finding is "
        "listed with its disposition — *fix before release* (a release blocker besides the "
        "entitlement gate), *planned*, *accepted* (with the reason) or *fixed*.",
        "",
        "| Check | Severity | Result | Disposition | Reason / action |",
        "|---|---|---|---|---|",
    ]
    all_rows = [(c, results[c]) for c in finding_ids + not_verified] + [
        (c, local[c]) for c in local_findings
    ]
    all_rows.sort(key=lambda r: (SEVERITY_ORDER[r[1]["severity"]], r[0]))
    for cid, result in all_rows:
        kind, reason = dispositions[cid]
        cl.append(
            f"| {cid} | {result['severity']} | {result['status']} | {KIND_EN[kind]} | {reason} |"
        )
    cl.append("")
    OUT_CHANGELOG.write_text("\n".join(cl), encoding="utf-8")
    print(f"wrote {OUT} and {OUT_CHANGELOG} ({len(all_rows)} changelog rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
