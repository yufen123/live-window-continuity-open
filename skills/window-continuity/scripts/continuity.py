#!/usr/bin/env python3
"""Portable, offline window-continuity ledger. No network or role authorization."""

import argparse
import contextlib
import datetime as dt
import fcntl
import hashlib
import json
import os
import re
import sys
import tempfile
import zipfile
from pathlib import Path

SCHEMA = 1
MODES = ("fictional", "real_work", "teaching", "other")
TRUTH = ("verified", "claimed", "inferred", "candidate", "fictional")
SAFE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,79}$")
MAX_OBJECT = 20 * 1024 * 1024
MAX_ARCHIVE = 150 * 1024 * 1024


class Hold(Exception):
    def __init__(self, reason, detail=""):
        super().__init__(reason)
        self.reason, self.detail = reason, detail


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def valid(value, name):
    if not SAFE.fullmatch(value) or value in (".", ".."):
        raise Hold("INVALID_IDENTIFIER", name)
    return value


def canonical(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def atomic(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".writing-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


@contextlib.contextmanager
def locked(store):
    store.parent.mkdir(parents=True, exist_ok=True)
    with open(str(store) + ".lock", "a+b") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        yield


def state_path(store):
    return store / "state.json"


def read_json(path):
    try:
        return json.loads(path.read_bytes())
    except (FileNotFoundError, ValueError, UnicodeDecodeError) as exc:
        raise Hold("MISSING_OR_INVALID_RECORD", str(path)) from exc


def load(store):
    state = read_json(state_path(store))
    if state.get("schema") != SCHEMA:
        raise Hold("SCHEMA_MISMATCH", str(state.get("schema")))
    return state


def object_ref(store, data):
    if len(data) > MAX_OBJECT:
        raise Hold("ARTIFACT_TOO_LARGE", str(len(data)))
    key = digest(data)
    path = store / "objects" / key
    if path.exists():
        if digest(path.read_bytes()) != key:
            raise Hold("OBJECT_HASH_MISMATCH", key)
    else:
        atomic(path, data)
    return {"sha256": key, "bytes": len(data)}


def verify_ref(store, ref):
    key = ref.get("sha256", "")
    if not re.fullmatch(r"[0-9a-f]{64}", key):
        raise Hold("INVALID_OBJECT_REF", str(key))
    path = store / "objects" / key
    try:
        data = path.read_bytes()
    except FileNotFoundError as exc:
        raise Hold("MISSING_OBJECT", key) from exc
    if len(data) != ref.get("bytes") or digest(data) != key:
        raise Hold("OBJECT_HASH_MISMATCH", key)
    return data


def checkpoint(store, key):
    if not re.fullmatch(r"[0-9a-f]{64}", key or ""):
        raise Hold("INVALID_CHECKPOINT", str(key))
    path = store / "checkpoints" / (key + ".json")
    try:
        data = path.read_bytes()
    except FileNotFoundError as exc:
        raise Hold("MISSING_CHECKPOINT", key) from exc
    if digest(data) != key:
        raise Hold("CHECKPOINT_HASH_MISMATCH", key)
    try:
        return json.loads(data)
    except ValueError as exc:
        raise Hold("INVALID_CHECKPOINT", key) from exc


def verify(store, state):
    live = state.get("live")
    if live is not None:
        verify_ref(store, live["desktop"])
        for label, ref in live["artifacts"].items():
            valid(label, "artifact label")
            verify_ref(store, ref)
    pointer = state["checkpoint"]
    key, seen = pointer["id"], set()
    expected_end, expected_generation = pointer["event_end"], pointer["generation"]
    while key is not None:
        if key in seen:
            raise Hold("CHECKPOINT_CYCLE", key)
        seen.add(key)
        package = checkpoint(store, key)
        if package["namespace"] != state["namespace"] or package["target_generation"] != expected_generation:
            raise Hold("CHECKPOINT_IDENTITY_MISMATCH")
        verify_ref(store, package["desktop"])
        for ref in package["artifacts"].values():
            verify_ref(store, ref)
        start, end = package["event_start"], package["event_end"]
        if not 0 <= start <= end == expected_end <= len(state["events"]):
            raise Hold("INVALID_EVENT_CURSOR")
        if state["events"][start:end] != package["delta"]:
            raise Hold("DELTA_MISMATCH")
        key, expected_end, expected_generation = package["parent_checkpoint"], start, package["origin_generation"]
    if expected_end != 0:
        raise Hold("INVALID_EVENT_CURSOR")
    return True


def output(**kwargs):
    print(json.dumps(kwargs, ensure_ascii=False, sort_keys=True))


def check_writer(state, window, rev):
    valid(window, "window")
    if state["phase"] not in ("ACTIVE", "ACKED"):
        raise Hold("PUBLISHED_NOT_ACKED")
    if state["active_window"] != window:
        raise Hold("WRONG_ACTIVE_WINDOW", state["active_window"])
    if state["revision"] != rev:
        raise Hold("REVISION_CONFLICT", str(state["revision"]))


def init(args):
    for label in ("owner", "project", "role", "window", "generation"):
        valid(getattr(args, label), label)
    store = args.store
    with locked(store):
        if store.exists():
            raise Hold("STORE_EXISTS", str(store))
        store.mkdir(mode=0o700)
        state = {
            "schema": SCHEMA,
            "namespace": {"owner": args.owner, "project": args.project, "role_lineage": args.role, "mode": args.mode},
            "active_window": args.window, "generation": args.generation,
            "phase": "ACTIVE", "revision": 0, "live": None, "events": [],
            "checkpoint": {"revision": 0, "id": None, "generation": None, "event_end": 0},
        }
        atomic(state_path(store), canonical(state))
    output(state="ACTIVE", revision=0, namespace=state["namespace"], stop="HOLD")


def save_live(args):
    with locked(args.store):
        state = load(args.store)
        check_writer(state, args.window, args.expected_rev)
        names = {}
        for source in args.artifact:
            name = valid(Path(source).name, "artifact label")
            if name in names:
                raise Hold("DUPLICATE_ARTIFACT", name)
            names[name] = source
        desktop = Path(args.desktop).read_bytes()
        selected = {name: Path(path).read_bytes() for name, path in names.items()}
        desktop_ref = object_ref(args.store, desktop)
        artifacts = {name: object_ref(args.store, content) for name, content in selected.items()}
        state["revision"] += 1
        state["phase"] = "ACTIVE"
        state["live"] = {"window": args.window, "generation": state["generation"], "saved_at": now(),
                         "desktop": desktop_ref, "artifacts": artifacts, "source": args.source}
        atomic(state_path(args.store), canonical(state))
    output(state="ACTIVE", revision=state["revision"], saved_at=state["live"]["saved_at"],
           artifact_labels=list(artifacts), stop="HOLD")


def append_event(args):
    with locked(args.store):
        state = load(args.store)
        check_writer(state, args.window, args.expected_rev)
        if len(args.summary) > 2000 or len(args.source) > 500:
            raise Hold("EVENT_TOO_LONG")
        event = {"window": args.window, "generation": state["generation"], "at": now(),
                 "type": valid(args.type, "event type"), "summary": args.summary, "source": args.source,
                 "truth": args.truth, "accepted_by": args.accepted_by}
        state["events"].append(event)
        state["revision"] += 1
        state["phase"] = "ACTIVE"
        atomic(state_path(args.store), canonical(state))
    output(state="ACTIVE", revision=state["revision"], event_index=len(state["events"]) - 1, stop="HOLD")


def read_live(args):
    with locked(args.store):
        state = load(args.store)
        live = state["live"]
        if live is None:
            raise Hold("NO_SAVED_DESKTOP")
        verify(args.store, state)
        if state["phase"] == "PUBLISHED_NOT_ACKED" or live["window"] != args.window:
            raise Hold("HISTORICAL_ONLY", "Use restore with the expected frozen generation")
        text = verify_ref(args.store, live["desktop"]).decode("utf-8")
        output(state=state["phase"], revision=state["revision"], saved_at=live["saved_at"],
               source=live["source"], desktop=text, artifact_labels=list(live["artifacts"]),
               stop="HOLD")


def freeze(args):
    valid(args.target_generation, "target generation")
    with locked(args.store):
        state = load(args.store)
        check_writer(state, args.window, args.expected_rev)
        head = state["checkpoint"]
        if head["revision"] != args.expected_head_rev:
            raise Hold("HEAD_REVISION_CONFLICT", str(head["revision"]))
        if state["live"] is None or state["live"]["window"] != args.window:
            raise Hold("NO_SAVED_DESKTOP")
        if args.target_generation == state["generation"]:
            raise Hold("TARGET_IS_CURRENT")
        verify(args.store, state)
        package = {"schema": SCHEMA, "namespace": state["namespace"],
                   "origin_window": args.window, "origin_generation": state["generation"],
                   "target_generation": args.target_generation, "created_at": now(),
                   "parent_checkpoint": head["id"], "source_live_rev": state["revision"],
                   "desktop": state["live"]["desktop"], "artifacts": state["live"]["artifacts"],
                   "event_start": head["event_end"], "event_end": len(state["events"]),
                   "delta": state["events"][head["event_end"]:], "stop": "HOLD"}
        content = canonical(package)
        key = digest(content)
        path = args.store / "checkpoints" / (key + ".json")
        if path.exists() and path.read_bytes() != content:
            raise Hold("CHECKPOINT_HASH_MISMATCH", key)
        atomic(path, content)
        checkpoint(args.store, key)
        if args.interrupt_before_publish:
            raise Hold("PREPARED_NOT_PUBLISHED", key)
        head.update({"revision": head["revision"] + 1, "id": key,
                     "generation": args.target_generation, "event_end": len(state["events"])})
        state["phase"] = "PUBLISHED_NOT_ACKED"
        state["revision"] += 1
        atomic(state_path(args.store), canonical(state))
    output(state=state["phase"], checkpoint=key, head_revision=head["revision"],
           target_generation=args.target_generation, stop="HOLD")


def restore(args):
    with locked(args.store):
        state = load(args.store)
        verify(args.store, state)
        head = state["checkpoint"]
        if head["id"] is None or head["generation"] != args.expected_generation:
            raise Hold("STALE_POINTER_FOR_CUTOVER", str(head["generation"]))
        package = checkpoint(args.store, head["id"])
        if state["phase"] != "PUBLISHED_NOT_ACKED":
            raise Hold("HISTORICAL_ONLY", state["phase"])
        if args.new_window == package["origin_window"]:
            raise Hold("NEW_WINDOW_REQUIRED")
        valid(args.new_window, "new window")
        text = verify_ref(args.store, package["desktop"]).decode("utf-8")
        output(state="VERIFIED_AWAITING_ACK", checkpoint=head["id"], head_revision=head["revision"],
               namespace=state["namespace"], origin_generation=package["origin_generation"],
               target_generation=package["target_generation"], desktop=text, delta=package["delta"],
               artifacts=package["artifacts"], source_cutoff=package["created_at"], stop="HOLD")


def ack(args):
    with locked(args.store):
        state = load(args.store)
        verify(args.store, state)
        head = state["checkpoint"]
        if state["phase"] != "PUBLISHED_NOT_ACKED" or head["revision"] != args.expected_head_rev:
            raise Hold("ACK_CONFLICT", str(head["revision"]))
        if head["generation"] != args.expected_generation:
            raise Hold("STALE_POINTER_FOR_CUTOVER", str(head["generation"]))
        package = checkpoint(args.store, head["id"])
        valid(args.new_window, "new window")
        if args.new_window == package["origin_window"]:
            raise Hold("NEW_WINDOW_REQUIRED")
        state["active_window"] = args.new_window
        state["generation"] = args.expected_generation
        state["phase"] = "ACKED"
        state["revision"] += 1
        state["live"] = {"window": args.new_window, "generation": state["generation"], "saved_at": now(),
                         "desktop": package["desktop"], "artifacts": package["artifacts"],
                         "source": "checkpoint:" + head["id"]}
        atomic(state_path(args.store), canonical(state))
    output(state="ACKED", revision=state["revision"], active_window=args.new_window,
           warning="Role and task authority require separate user confirmation", stop="HOLD")


def inspect(args):
    with locked(args.store):
        state = load(args.store)
        verify(args.store, state)
        head = state["checkpoint"]
        if args.expected_generation and head["generation"] != args.expected_generation:
            raise Hold("STALE_POINTER_FOR_CUTOVER", str(head["generation"]))
        output(state=state["phase"], revision=state["revision"], namespace=state["namespace"],
               active_window=state["active_window"], generation=state["generation"],
               live_saved_at=state["live"]["saved_at"] if state["live"] else None,
               head_revision=head["revision"], checkpoint=head["id"],
               frozen_generation=head["generation"], event_count=len(state["events"]), stop="HOLD")


def export_archive(args):
    with locked(args.store):
        state = load(args.store)
        verify(args.store, state)
        entries = {}
        for path in args.store.rglob("*"):
            if path.is_symlink():
                raise Hold("SYMLINK_IN_STORE", str(path))
            if path.is_file():
                name = path.relative_to(args.store).as_posix()
                if name != "state.json" and not (name.startswith("objects/") or name.startswith("checkpoints/")):
                    raise Hold("UNEXPECTED_STORE_FILE", name)
                entries[name] = path.read_bytes()
        if sum(map(len, entries.values())) > MAX_ARCHIVE:
            raise Hold("ARCHIVE_TOO_LARGE")
        manifest = {"schema": SCHEMA, "exported_at": now(), "namespace": state["namespace"],
                    "files": {name: {"bytes": len(data), "sha256": digest(data)} for name, data in sorted(entries.items())}}
        args.out.parent.mkdir(parents=True, exist_ok=True)
        fd, temp = tempfile.mkstemp(prefix=".archive-", dir=args.out.parent)
        try:
            with os.fdopen(fd, "wb") as handle, zipfile.ZipFile(handle, "w", zipfile.ZIP_DEFLATED) as archive:
                for name, data in sorted(entries.items()):
                    archive.writestr(name, data)
                archive.writestr("archive_manifest.json", canonical(manifest))
            os.replace(temp, args.out)
        finally:
            if os.path.exists(temp):
                os.unlink(temp)
        output(state=state["phase"], archive=str(args.out), sha256=digest(args.out.read_bytes()),
               revision=state["revision"], stop="HOLD")


def import_archive(args):
    if args.store.exists():
        raise Hold("STORE_EXISTS", str(args.store))
    with locked(args.store):
        try:
            with zipfile.ZipFile(args.archive) as archive:
                infos = archive.infolist()
                names = [info.filename for info in infos]
                if len(names) != len(set(names)) or "archive_manifest.json" not in names:
                    raise Hold("INVALID_ARCHIVE_ENTRIES")
                manifest = json.loads(archive.read("archive_manifest.json"))
                expected = manifest["files"]
                if manifest.get("schema") != SCHEMA or set(names) != set(expected) | {"archive_manifest.json"}:
                    raise Hold("INVALID_ARCHIVE_MANIFEST")
                if sum(info.file_size for info in infos) > MAX_ARCHIVE:
                    raise Hold("ARCHIVE_TOO_LARGE")
                contents = {}
                for name in expected:
                    parts = Path(name).parts
                    if (len(parts) != 1 or name != "state.json") and (
                        len(parts) != 2 or parts[0] not in ("objects", "checkpoints")
                    ):
                        raise Hold("INVALID_ARCHIVE_PATH", name)
                    if name != "state.json" and not (
                        re.fullmatch(r"[0-9a-f]{64}", parts[-1]) or
                        (parts[0] == "checkpoints" and re.fullmatch(r"[0-9a-f]{64}\.json", parts[-1]))
                    ):
                        raise Hold("INVALID_ARCHIVE_PATH", name)
                    data = archive.read(name)
                    if len(data) != expected[name]["bytes"] or digest(data) != expected[name]["sha256"]:
                        raise Hold("ARCHIVE_HASH_MISMATCH", name)
                    contents[name] = data
        except (zipfile.BadZipFile, KeyError, ValueError) as exc:
            raise Hold("INVALID_ARCHIVE", str(exc)) from exc
        temp = Path(tempfile.mkdtemp(prefix=".import-", dir=args.store.parent))
        try:
            for name, data in contents.items():
                atomic(temp / name, data)
            state = load(temp)
            if manifest["namespace"] != state["namespace"]:
                raise Hold("NAMESPACE_MISMATCH")
            expected_namespace = {"owner": args.expected_owner, "project": args.expected_project,
                                  "role_lineage": args.expected_role, "mode": args.expected_mode}
            if state["namespace"] != expected_namespace:
                raise Hold("NAMESPACE_MISMATCH")
            verify(temp, state)
            os.replace(temp, args.store)
        finally:
            if temp.exists():
                import shutil
                shutil.rmtree(temp)
    output(state=state["phase"], revision=state["revision"], namespace=state["namespace"],
           archive_sha256=digest(args.archive.read_bytes()), stop="HOLD")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    def command(name):
        p = sub.add_parser(name)
        p.add_argument("--store", required=True, type=Path)
        return p
    p = command("init")
    for name in ("owner", "project", "role", "window", "generation"):
        p.add_argument("--" + name, required=True)
    p.add_argument("--mode", choices=MODES, required=True)
    p.set_defaults(handler=init)
    p = command("save-live")
    p.add_argument("--window", required=True)
    p.add_argument("--expected-rev", type=int, required=True)
    p.add_argument("--desktop", required=True)
    p.add_argument("--artifact", action="append", default=[])
    p.add_argument("--source", required=True)
    p.set_defaults(handler=save_live)
    p = command("append-event")
    p.add_argument("--window", required=True)
    p.add_argument("--expected-rev", type=int, required=True)
    p.add_argument("--type", required=True)
    p.add_argument("--summary", required=True)
    p.add_argument("--source", required=True)
    p.add_argument("--truth", choices=TRUTH, required=True)
    p.add_argument("--accepted-by")
    p.set_defaults(handler=append_event)
    p = command("read-live")
    p.add_argument("--window", required=True)
    p.set_defaults(handler=read_live)
    p = command("inspect")
    p.add_argument("--expected-generation")
    p.set_defaults(handler=inspect)
    p = command("freeze")
    p.add_argument("--window", required=True)
    p.add_argument("--expected-rev", type=int, required=True)
    p.add_argument("--expected-head-rev", type=int, required=True)
    p.add_argument("--target-generation", required=True)
    p.add_argument("--interrupt-before-publish", action="store_true", help=argparse.SUPPRESS)
    p.set_defaults(handler=freeze)
    p = command("restore")
    p.add_argument("--new-window", required=True)
    p.add_argument("--expected-generation", required=True)
    p.set_defaults(handler=restore)
    p = command("ack")
    p.add_argument("--new-window", required=True)
    p.add_argument("--expected-generation", required=True)
    p.add_argument("--expected-head-rev", type=int, required=True)
    p.set_defaults(handler=ack)
    p = command("export")
    p.add_argument("--out", required=True, type=Path)
    p.set_defaults(handler=export_archive)
    p = command("import")
    p.add_argument("--archive", required=True, type=Path)
    for name in ("owner", "project", "role"):
        p.add_argument("--expected-" + name, required=True)
    p.add_argument("--expected-mode", required=True, choices=MODES)
    p.set_defaults(handler=import_archive)
    args = parser.parse_args()
    try:
        args.handler(args)
    except Hold as exc:
        output(state="HOLD", reason=exc.reason, detail=exc.detail, stop="HOLD")
        return 2
    except (OSError, UnicodeError, TypeError) as exc:
        output(state="HOLD", reason="IO_OR_ENCODING_ERROR", detail=str(exc), stop="HOLD")
        return 2
    except (KeyError, IndexError, ValueError) as exc:
        output(state="HOLD", reason="INVALID_RECORD", detail=str(exc), stop="HOLD")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
