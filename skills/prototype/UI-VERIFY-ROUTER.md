# UI Prototype Verification Router

Target Reader: Codex running the `prototype` UI branch.
Reader Action Needed: Verify prototype visuals and interactions with the narrowest available tool.
Decision Supported: Whether prototype observations are backed by browser/runtime evidence or still unverified.
Scope: Static HTML prototypes, local URLs, browser-visible states, interactions, responsive checks, and tool limitations.
Out of Scope: Production UI QA, backend contract acceptance, or replacing `verify`.
Evidence Level: Groundwork issue #10 acceptance criteria and `skills/prototype/UI.md`.

Use this router when a prototype output makes visual or interaction claims.

| Situation | Preferred Tool | Evidence Needed |
| --- | --- | --- |
| Local static HTML or local app flow | Browser plugin | URL, state/action, screenshot or direct observation, limitation. |
| Console or network behavior affects the prototype claim | Chrome DevTools MCP | URL/context, console/network evidence, request/response detail, limitation. |
| User login or Chrome profile state is necessary | Chrome extension tooling | Tab/context, user-state dependency, action, observation, limitation. |
| Repeatable automated UI assertion is needed | Playwright / Puppeteer | Scripted action, assertion, screenshot or trace when available, limitation. |

Prototype evidence format:

```text
Browser / Runtime Evidence
- Tool:
- URL / Context:
- Action:
- Observation:
- Limitation:
```

If the tool cannot run, write `unverified` for visual and interaction claims. Do not silently replace runtime evidence with visual guesses from source code.
