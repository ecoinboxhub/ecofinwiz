# WCAG 2.1 Accessibility Audit — EcoFinwize

> **Date**: 2026-07-14
> **Scope**: Frontend pages (25 pages), components (5), chat interface
> **Standard**: WCAG 2.1 Level AA

## Summary

| Criterion | Status | Notes |
|-----------|--------|-------|
| Perceivable | Partial | Color contrast adequate; alt text inconsistent |
| Operable | Partial | Keyboard nav works; focus indicators missing |
| Understandable | Partial | Labels present; error announcements absent |
| Robust | Needs Work | ARIA landmarks incomplete; no live regions |

## Findings

### P1 — Critical

| Issue | Location | WCAG | Recommendation |
|-------|----------|------|---------------|
| No skip-to-content link | Layout.tsx | 2.4.1 | Add `<a href="#main">` as first focusable element |
| Chat messages lack `role="log"` / `aria-live` | Advisor.tsx | 4.1.3 | Add `role="log" aria-live="polite"` to chat container |
| VoiceButton has no accessible label | VoiceButton.tsx | 4.1.2 | Add `aria-label="Start voice input"` |

### P2 — Major

| Issue | Location | WCAG | Recommendation |
|-------|----------|------|---------------|
| Focus indicators removed via `outline: none` | index.css | 2.4.7 | Add `:focus-visible` styles |
| No `aria-current` on nav links | Layout.tsx | 2.4.8 | Use `aria-current="page"` on active route |
| Form errors not announced | All forms | 3.3.1 | Add `aria-describedby` to error fields |
| No `lang` attribute on `<html>` | index.html | 3.1.1 | Add `lang="en"` |
| Page titles not descriptive | All pages | 2.4.2 | Set `<title>` per route |

### P3 — Minor

| Issue | Location | WCAG | Recommendation |
|-------|----------|------|---------------|
| Images missing `alt` | Various | 1.1.1 | Add descriptive alt text to all `<img>` |
| Color alone conveys info (charts) | Dashboard.tsx | 1.4.1 | Add patterns / labels |
| No landmark elements (`<nav>`, `<main>`) | Layout.tsx | 1.3.1 | Use semantic HTML regions |

## Remediation Plan

1. Add `<a href="#main" class="skip-link">` to Layout.tsx
2. Add `role="log" aria-live="polite"` to chat container in Advisor.tsx
3. Add `aria-label="Start voice input"` to VoiceButton.tsx
4. Add `:focus-visible` styles in index.css
5. Add `aria-current="page"` to active nav links
6. Add `lang="en"` to index.html
7. Set dynamic `<title>` per route via react-helmet-async
8. Audit all `<img>` elements for alt text

## Verification

Re-audit with axe DevTools after remediation. Target: 0 critical, 0 serious violations.
