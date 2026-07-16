# UI Verification Tool Router

Target Reader: Codex running `verify` for browser-visible or UI behavior.
Reader Action Needed: Choose the right UI inspection tool and record evidence without confusing tool roles.
Decision Supported: Whether UI claims are actually observed or still unverified.
Scope: Browser plugin, Chrome DevTools MCP, Chrome extension tooling, Playwright, and Puppeteer routing.
Out of Scope: Tool installation, bypassing security interstitials, or claiming visual correctness without observation.
Evidence Level: Groundwork issue #10 acceptance criteria and existing prototype UI verification rules.

## Tool Choice

| Tool | Use For | Do Not Use For |
| --- | --- | --- |
| Browser plugin | Local URLs, simple navigation, screenshots, click/type flow checks in Codex App. | Console/network inspection that requires DevTools-level request details. |
| Chrome DevTools MCP | Console logs, network requests, request bodies, Lighthouse/performance traces, or active Chrome debugging sessions. | Local UI smoke checks that Browser can do directly. |
| Chrome extension tooling | Pages that require the user's Chrome profile, cookies, login state, extensions, or current authenticated tab. | Anonymous local fixture checks. |
| Playwright / Puppeteer | Deterministic scripted browser checks, reproducible screenshots, CI-style UI assertions. | Claims requiring the user's real browser profile unless configured for it. |

## Evidence Format

Use this format for UI verification evidence after the required `Verification Scope` block from `SCOPE-EVIDENCE-TEMPLATE.md`; it never replaces the scope block:

```text
UI Evidence
- Tool:
- URL / Context:
- Action:
- Observation:
- Limitation:
```

Rules:

- Stay in `verify` for UI tool-choice or UI evidence-routing prompts, even when the fixture is a static prototype. Do not replace verify's scope-first output with a prototype review or browser-only conclusion.
- Do not claim layout, color, responsiveness, hover/focus, animation, or state-transition correctness without browser/runtime evidence.
- If no UI tool is available, mark the visual or interaction claim `unverified`.
- State why a tool was chosen when switching from Browser to DevTools, extension tooling, Playwright, or Puppeteer.
- Do not bypass security or certificate interstitials as a verification shortcut.
- When the UI observation is used to attribute UAT behavior to a fix, artifact, deployed version, mutable shared environment, or rerun, follow the UI evidence with the conditional `UAT Evidence Window` from `skills/_shared/RELEASE-EVIDENCE-CLAIM.md` or cite its canonical reference. Do not duplicate the full window inside every UI check.
