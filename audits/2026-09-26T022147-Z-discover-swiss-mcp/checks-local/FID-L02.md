---
id: FID-L02
title: "Facetten-Antwort vollständig oder gemeldet"
category: FID
severity: high
applies_when: 'always'
scope: server-specific (discover-swiss-mcp, P4)
narrows: FID-006 (Antwortstruktur und Feldnamen bestätigen) — angewandt auf die Facetten-Keys
evidence_required: 2
---

# FID-L02 — Facetten-Antwort vollständig oder gemeldet

## Description

discover.swiss verwirft falsch geschriebene Facetten-Namen **still**
(Fundstück 8) — und beantwortet einen erfundenen Namen mit 400 für den ganzen
Request (P3-Stop-Gate). Jede angefragte Facette muss deshalb in der Antwort
stehen oder in `missing_facets` gemeldet werden; eine fehlende Facette darf nie
als «keine Werte» erscheinen.

## Verification

1. `code_review`: Vergleich der Antwort-Keys gegen die gesendeten Namen
   (Client) und Weitergabe an das Envelope (`explore_area`, `resolve_area`).
2. `code_review`: Unbekannte Namen werden nicht gesendet, aber gemeldet.
3. `automated`: Unit-Test «gesendet, nicht zurück → missing_facets» und
   Live-Canary `containedInPlace/id` kommt zurück.

## Pass Criteria

- Keine angefragte Facette verschwindet ohne Eintrag in `missing_facets` + `hint`.
- Ein Test belegt es mit einer Antwort, in der eine Facette fehlt.
