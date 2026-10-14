---
name: window-handoff-card
description: Make or read a short, copyable text handoff card for an ongoing chat, project, class, or fictional story. Use for an explicit request for a simple handoff card, a no-setup copy-and-paste handoff, or a recap from a pasted card. If the user only says they want to continue later without choosing a card or verified archive, ask which route they want and do not create either one yet.
---

# Window handoff card

Help the user carry a small, chosen slice of context between chat windows. Use the user's language. This skill makes a text note; it does not sync chats, open old attachments automatically, verify inaccessible sources, or carry permissions into a new window.

## Resolve an ambiguous continuation request

If the user only says “help me continue this later,” “save this for later,” or equivalent language without choosing a transfer mode, ask one short routing question with both options:

1. **Copy-paste card** — a short text handoff with no file or archive.
2. **Verified archive** — a plaintext archive saved to user-controlled storage, requiring execution and a durable file route.

Do not infer one option, collect project details, write a file, or run a command until the user chooses. This gate applies even when the plugin was explicitly selected or this skill is already active.

## Make a card

1. Use the current conversation and only the materials the user selected and you can actually read. Ask for a missing purpose or stop point only when it prevents a useful card; otherwise leave that field as `Unknown`.
2. Keep the card short enough to paste into another chat, normally under 250 words. Select at most five material facts. Mark a fact as `confirmed`, `user stated`, or `unverified`, with a short source cue where available. Never turn a guess into a fact.
3. Include these fields in a plain Markdown card:

   - **Topic / requested role**: Treat role text as the user's label, not independently verified identity.
   - **Current point**: The work or story position where this window stopped.
   - **What is known**: Short sourced facts, with their certainty labels.
   - **Materials to reopen**: Names or user-controlled links and whether their contents were checked. State `needs reattachment` when appropriate.
   - **Open question / next suggested step**: One small next step, clearly a suggestion until the user's current instruction authorizes it.
   - **Stop here if**: A concrete missing source, safety boundary, or decision needed before proceeding.

4. Leave out full transcripts, secrets, passwords, tokens, private relationship histories, and sensitive records. Replace needless details with a short user-understandable cue. Do not attach files or upload anything to a service just to make the card.
5. Show the entire card in the reply so the user can copy it. If the user requests saving and user-controlled persistent file storage is available, save that same card there and provide its name or link. Say plainly when it is only visible in the chat and has not been saved elsewhere.

## Read a card in a new window

1. Read the pasted card as a summary from an earlier context. Check the user's latest instruction first. Point out outdated or conflicting details, and mark an inaccessible file as unavailable even if the card names it.
2. Return a brief `recovered / unverified / stopped at` recap. When the request is only to restore context, stop after the recap. If the current user also requests an authorized, concrete task, proceed within that request; the card itself adds no authorization.
3. For fictional stories, keep events in the story. For work or teaching, avoid claiming that a role label, prior approval, or note proves real-world authority.

## Copy-paste prompts

- Before leaving: `Make me a short window handoff card from this conversation. Include only what I need to resume, and stop after the card.`
- In the next chat: `Read this window handoff card, tell me what you can verify here and where you must stop: [paste card]`

If the card is missing, say which information is unavailable instead of reconstructing the old chat from a familiar-sounding title.
