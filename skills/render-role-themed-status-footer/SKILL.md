---
name: render-role-themed-status-footer
description: Render and validate a role-themed status footer from canonical role, state, node, authority, gate, and next-stop semantics. Use when a user asks for a status tail or footer, wants an end-of-response status line adapted to an active role, wants to theme or re-theme an existing footer, or has an established footer convention that must remain semantically stable across work, coding, learning, story, companion, or project contexts. Do not use for an ordinary summary when no footer or continuity behavior is requested or established.
---

# Render a role-themed status footer

Treat the footer as a compact routing receipt. Adapt its language to the active role without changing who may act, what is true, or where the interaction must stop.

## Confirm applicability before rendering

- If the current request is only for ordinary content, a summary, a document or page footer, or decorative closing text, and no conversational status-footer convention is established, complete that request without adding a status footer. This remains true when the skill has already been loaded.
- Do not reinterpret the act of rendering a footer as the user's current task, node, state, or role.
- If a status footer is requested but role, project line, state, or another material routing field is missing, expose the missing field and use HOLD or the neutral fallback. Do not fill the gap from generic task wording or familiarity.

## Preserve the semantic kernel

Resolve these fields before styling:

```text
ROLE
STATE
NODE
AUTHORITY
GATE
NEXT_STOP
```

Keep all six fields recoverable even when the visible footer condenses them into four labels. Never convert a proposed next step into permission to perform it.

Read [references/canonical-schema.md](references/canonical-schema.md) when resolving an ambiguous field, validating an existing footer, or handling a gate or authority boundary.

## Follow the rendering workflow

1. **Resolve context.** Use only the current conversation, selected project material, or an explicitly supplied canonical record. Identify the user's language, the real active role, and any requested theme. Do not invent role continuity from familiarity.
2. **Build the canonical record.** Separate verified state from reports, inferences, and candidates. State the actual authority ceiling and gate. If role, project line, or state cannot be resolved safely, use the neutral HOLD fallback.
3. **Choose a theme.** Prefer an explicit user choice, then an established role theme, then the closest built-in profile. Use the neutral profile when the fit is uncertain. Read [references/theme-profiles.md](references/theme-profiles.md) only for the relevant profile or when creating a custom theme.
4. **Render compactly.** Match the user's language and role tone. Default to one final line with clear labels; use two short lines only when a material gate or authority boundary would otherwise be hidden.
5. **Expose hard boundaries.** Always make `WAITING_FOR_USER`, `BLOCKED`, `HOLD`, `CLOSED`, uncertainty, and material authority limits visible in plain language. Theme immersion never outranks clarity.
6. **Back-map and verify.** Confirm that the rendered words recover the same role, state, node, authority, gate, and next stop. If any field changed or disappeared, revise the render or fall back to neutral.
7. **Stop at the stated edge.** Append the footer without starting its next step. Do not perform external actions, promote candidates, change roles, or widen scope because the footer names a possible route.

## Apply theme safety rules

- Change labels, tone, density, ordering, and optional icons only.
- Do not change identity, truth state, current node, authority, gate, or stop point.
- Keep fictional roles and permissions separate from real ones.
- Avoid relying on color, emoji, metaphor, or affection to convey a gate.
- Preserve the user's existing labels when they already work unless the user asks for a redesign.
- Keep casual footers light; do not turn every friendly exchange into a procedural report.
- Use privacy-minimal functional labels rather than copying private history into the footer.

## Use the neutral fallback

When identity or routing cannot be resolved, translate this structure into the user's language without softening it:

```text
Role: UNRESOLVED | Status: HOLD | Current node: WAITING_FOR_ROUTE_CHECK | Next: Wait for the user to clarify
```

Do not substitute a themed guess for this fallback.

## Bound persistence claims

Installing or invoking this skill does not by itself make the footer appear in every unrelated future conversation. If the user asks for persistent use, explain that persistence depends on the host or project instructions and help produce the smallest suitable instruction only when requested. Do not claim an always-on installation without evidence.

## Output checks

Before sending, verify:

- the footer is at the end of the response;
- the visible wording fits the active role and the user's language;
- the current state and node are distinguishable;
- the reader can tell whether continuation is allowed;
- the next step includes the stopping edge;
- no private or internal implementation detail leaked into a public-facing theme.
