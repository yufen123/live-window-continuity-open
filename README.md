# Live Window Continuity

Carry a small, selected piece of non-sensitive context between chat windows.

Three skills provide role-aware status footers, copy-paste handoff cards, and
verified plaintext archives. An offline Python command-line tool checks archive
contents, namespaces, revisions, generations, and checkpoint history.

## Status

This is experimental source release v0.1.4-rc.1, based on plugin v0.1.3.
Artwork and optional icon references are omitted pending provenance review.
Released under the MIT License, copyright (c) 2026 Yufen Li. Host marketplace
submission is a separate decision. This is not an official OpenAI product or a
claim of marketplace approval.

## Choose a workflow

- **Status footer:** show the current role, state, authority, gate, and next stop.
- **Handoff card:** create a short note to paste into another chat; no archive required.
- **Verified archive:** save selected non-sensitive materials, then verify them in
  a new working location before continuing. Recovery does not grant authority.

Example requests:

- “Make a short copy-paste handoff card and stop after the card.”
- “Save this fictional project's selected desktop and note in a verified archive.”
- “Restore this archive for the expected generation and stop before ACK.”

## Requirements and limits

The archive tool uses Python's standard library and POSIX file locking (`fcntl`).
It was tested here on Linux with Python 3.12. Native Windows is not supported by
the current locking implementation. The acceptance runner also uses Bash,
`unzip`, and `truncate`; other operating systems were not tested.

A compatible agent host must load the skills and provide execution for archive
operations. The repository includes the implementation, not a hosted service.
Persistent cross-window recovery additionally needs user-controlled durable
storage with access control and guarded version replacement. A local working
directory alone is not durable storage. No storage adapter is bundled.

Archives are plaintext, not encrypted or authenticated signatures. Hashes detect
inconsistency; they do not establish who created an archive. Use only trusted,
user-controlled archives and fictional or explicitly de-identified data.
The tool does not automatically remember chats, recover unsaved turns, detect
context limits, schedule backups, or carry permissions into another window.

## Run the offline check

From this repository's root:

```sh
bash tests/run_offline_acceptance.sh
python3 skills/window-continuity/scripts/continuity.py --help
```

The candidate passes 22/22 offline acceptance cases. Host behavior test prompts
are in `tests/HOST_TEST_CASES.json`; they are not automated by the shell runner.
Installation and end-to-end host behavior have not been rerun for this candidate.

## Build a review package

```sh
python3 scripts/build_package.py
```

The build includes only `plugin.json`, `LICENSE`, and `skills/`. It produces a
review ZIP in `build/`; it does not install, upload, publish, or select a license.
Use the destination host's supported plugin import flow if available. Host
compatibility must be checked before calling a build installable there.

## Privacy

Never include credentials, full private transcripts, real relationship histories,
health or student records, or third-party sensitive material. Runtime stores and
user archives are not product source and must never be committed. See `SECURITY.md`.

## License

MIT License. Copyright (c) 2026 Yufen Li. See [LICENSE](LICENSE).
