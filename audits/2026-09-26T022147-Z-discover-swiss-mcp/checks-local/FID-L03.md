---
id: FID-L03
title: "Testobjekte gefiltert und gezählt"
category: FID
severity: medium
applies_when: 'always'
scope: server-specific (discover-swiss-mcp, P4)
narrows: FID-003 (Leermenge unterscheidbar) — Filterung ohne Zähler wäre eine stille Verkleinerung
evidence_required: 2
---

# FID-L03 — Testobjekte gefiltert und gezählt

## Description

Der Produktivindex enthält ein «Demo Event» mit Platzhalteradresse
(Fundstück 10). Der Server muss es herausfiltern **und** in
`excluded_test_objects` zählen: gefiltert ohne Zähler verschweigt, wie dünn
der Bestand ist; ungefiltert empfiehlt er einem Gast den Platzhalter.

## Verification

1. `code_review`: Erkennungsregeln (Name, Platzhalter-Strasse/PLZ/Ort, Mail)
   und Anwendung in allen ausliefernden Tools.
2. `automated`: Unit-Test mit dem aufgezeichneten Demo-Event; Gegenprobe: ein
   echtes Event mit ähnlichem Namen bleibt drin.
3. `runtime_test`: Live-Canary `excluded_test_objects ≥ 1` (skip bei 0).

## Pass Criteria

- Filter greift in jedem Tool, das Objekte ausliefert, und zählt.
- Test mit dem aufgezeichneten Objekt vorhanden.
