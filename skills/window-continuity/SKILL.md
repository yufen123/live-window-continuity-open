---
name: window-continuity
description: Recover a saved live desktop, record a bounded window delta and role lineage, or prepare and verify an archive handoff between chat windows. Use for explicit requests to save, freeze, restore, or ACK a verifiable archive. If the user only says they want to continue later without choosing a copy-paste card or verified archive, ask which route they want and do not create either one yet.
---

# Window continuity

Use this skill only for a user's own namespace and explicitly selected materials. Keep actual user facts, fictional canon, interpretation, and permission decisions separate. Read the current user's instruction before accepting old history. The bundled script is an offline data verifier; its ACK is only a receipt, never role acceptance or task authorization.

## Resolve an ambiguous continuation request

If the user only says “help me continue this later,” “save this for later,” or equivalent language without choosing a transfer mode, ask one short routing question with both options:

1. **Copy-paste card** — a short text handoff with no file or archive.
2. **Verified archive** — a plaintext archive saved to user-controlled storage, requiring execution and a durable file route.

Do not infer one option, collect project details, write a file, or run a command until the user chooses. This gate applies even when the plugin was explicitly selected or this skill is already active.

## Privacy and storage boundary

Use the archive workflow only for fictional, explicitly de-identified, or other non-sensitive material. The exported ZIP is plaintext. Do not put private chats, real relationship histories, health or student records, credentials, or other sensitive files into it; do not copy user archives to a developer-operated site. Save only the short desktop, bounded delta, and artifacts the user deliberately selected. If a user asks to archive sensitive material, decline that capture and offer a de-identified handoff card or a minimal non-sensitive archive instead.

Run the commands for a user with no coding experience. Offer plain-language actions such as “保存当前桌面”, “准备换窗”, and “在新窗口找回存档”; tell the user where their own archive is saved, when it was last saved, and what remains unsaved. Never ask the user to operate a terminal if the agent can complete an authorized step. If this environment lacks either execution or durable user-controlled storage, mark the verified archive workflow unavailable here and offer the handoff-card workflow instead. A newly installed skill alone cannot supply a persistent private data service.

## Two discovery points

- LIVE_DESKTOP: the latest saved, still active window desktop and selected artifact bytes. Recover only the matching active window with the saved time and revision. Unsaved conversation turns cannot be recovered.
- CURRENT_CHECKPOINT: the last verified, published immutable freeze package. A new window must provide its expected generation. If it points to an older generation, return HOLD and describe it as historical.

Both live and frozen pointers are inside one self-contained archive. The local directory is only a working copy. Save the full archive to the user's own durable, access-controlled storage after any accepted change; for ChatGPT Library, use one exact stable title such as continuity__owner__project__role.zip, create once, then replace the same file identity with its expected version. In a new window resolve that exact file, reject ambiguous matches, materialize the bytes, import and verify before continuing. Never tell a user that unsynchronized local changes survived. Do not embed secrets or private project data in this shared skill.

## Workflow

1. Ask or infer a stable owner alias, project alias, role-lineage alias, mode (fictional, real_work, teaching, other), window ID, and generation. Validate user control of the selected archive using the storage account; names alone are not authentication. Keep an external stable archive title/file identity. Work only with the selected namespace.
2. Initialize using scripts/continuity.py init --store PATH --owner O --project P --role R --mode MODE --window W --generation G. This creates a local working copy; export and save it externally before calling it durable.
3. At a meaningful change, write a concise one-page desktop with current work, parked items, pending decisions, recent corrections, source cutoff and next stop. Use save-live --window W --expected-rev N --desktop PATH --source SOURCE, optionally repeating --artifact FILE for deliberately selected files. Use append-event --type TYPE --summary TEXT --source SOURCE --truth verified|claimed|inferred|candidate|fictional --accepted-by PERSON only if acceptance is evidenced. Do not capture every chat line or label a candidate accepted without evidence. Append roles/authority changes as sourced events without promoting them to permissions.
4. Run inspect then export --out ARCHIVE; update the durable copy using a guarded version write. If external save fails, retain the last published archive as authoritative and tell the user which revision remained local only. The mutable remote archive replacement needs a compare-and-swap/version guard; a filename alone does not prevent concurrent writers.
5. If local paths are lost, retrieve the archive from durable storage, import --archive ARCHIVE --store NEW_EMPTY_PATH --expected-owner O --expected-project P --expected-role R --expected-mode MODE, inspect and read-live --window W. Show saved_at, revision and what happened after the cutoff remains unknown. If bytes or references are missing or wrong, stop on the exact error.
6. On an explicit migration, inspect the local directory and the durable archive version; collect the bounded event delta and selected artifacts. freeze --window OLD --expected-rev N --expected-head-rev H --target-generation NEW. The package is verified before its pointer changes. Export and save the whole archive with a guarded version. A failed remote save is not a published handoff: reimport the last durable version into a new path for further work; leave the unsynced local freeze as a candidate and HOLD for any uncertain concurrent write.
7. For a new window, import the authoritative archive into a fresh path using the same expected namespace arguments; restore --new-window NEW --expected-generation G verifies it and prints the desktop, delta, artifact map and frozen cutoff. Stop HOLD for user review and role/task authority. Only after authorized acceptance run ack --new-window NEW --expected-generation G --expected-head-rev H, then export and save guarded again. Do not consider the old window fully retired until that durable ACK succeeds.

All commands include --store PATH; run python3 scripts/continuity.py COMMAND --help for exact flags. The local tool serializes mutations and rejects stale revisions; the external store must independently reject stale versions. Export/import verify archive entry hashes and namespace, and checkpoint/desktop/object hashes. The archive is a portable backup, not encryption; choose storage and retention appropriate to the data. If the account lacks a durable store, limit claims to the local archive operation and do not claim cross-window persistence.

## Optional conversational modules

- Status tail: end with role, overall status, current node, next step, scoped to the user's project. A tail is a routing receipt, not proof of authority.
- One-pass missing-cause scan: when a material explanation is uncertain, list a small number of plausible overlooked causes, one discriminating observation for each, and label facts versus inference. Do not write hypotheses to accepted history automatically.
- Long-term role lineage: attach sources, times, window IDs and acceptance status to role changes. For fictional play keep plot claims in the fictional domain; do not convert simulated relationship claims into real commitments.

The bundled script does not detect a window nearing its context limit, schedule backups, supply a remote server, or grant cross-account access. Do not run freeze on an active role without the user's instruction or pretend importing a package imports the prior chat transcript. If no durable user-controlled store is available, limit the claim to the locally exported archive and offer the handoff-card workflow for manual transfer.
