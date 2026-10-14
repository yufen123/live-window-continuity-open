#!/usr/bin/env bash
set -u

release_root="$(cd "$(dirname "$0")/.." && pwd)"
continuity="$release_root/skills/window-continuity/scripts/continuity.py"
fixtures="$release_root/tests/fixtures"
test_root="$(mktemp -d)"
passes=0

pass() {
  passes=$((passes + 1))
  printf 'PASS %s\n' "$1"
}

fail() {
  printf 'FAIL %s\n%s\n' "$1" "$2" >&2
  exit 1
}

expect_ok() {
  label="$1"
  needle="$2"
  shift 2
  output=$(PYTHONDONTWRITEBYTECODE=1 python3 -B "$continuity" "$@" 2>&1)
  status=$?
  if [ "$status" -ne 0 ] || [[ "$output" != *"$needle"* ]]; then
    fail "$label" "$output"
  fi
  pass "$label"
}

expect_hold() {
  label="$1"
  needle="$2"
  shift 2
  output=$(PYTHONDONTWRITEBYTECODE=1 python3 -B "$continuity" "$@" 2>&1)
  status=$?
  if [ "$status" -eq 0 ] || [[ "$output" != *"$needle"* ]] || [[ "$output" != *'"state": "HOLD"'* ]]; then
    fail "$label" "$output"
  fi
  pass "$label"
}

expect_ok init '"state": "ACTIVE"' init \
  --store "$test_root/working" --owner demo-owner --project starlight-library \
  --role librarian --mode fictional --window W01 --generation G01

expect_ok save-live-g01 '"revision": 1' save-live \
  --store "$test_root/working" --window W01 --expected-rev 0 \
  --desktop "$fixtures/desktop_g01.md" --artifact "$fixtures/blue_tree_note.txt" \
  --source fictional-fixture-g01

expect_ok append-event-g01 '"revision": 2' append-event \
  --store "$test_root/working" --window W01 --expected-rev 1 \
  --type DISCOVERY --summary 'The traveler found the unfinished atlas.' \
  --source fictional-fixture-g01 --truth fictional

expect_hold live-is-not-checkpoint STALE_POINTER_FOR_CUTOVER inspect \
  --store "$test_root/working" --expected-generation G01

expect_ok export-live 'archive_live_g01.zip' export \
  --store "$test_root/working" --out "$test_root/archive_live_g01.zip"
unzip -t "$test_root/archive_live_g01.zip" >/dev/null || fail archive-live-integrity 'unzip failed'
pass archive-live-integrity

expect_ok import-live '"revision": 2' import \
  --store "$test_root/recovered_live" --archive "$test_root/archive_live_g01.zip" \
  --expected-owner demo-owner --expected-project starlight-library \
  --expected-role librarian --expected-mode fictional

expect_ok read-recovered-live 'unfinished atlas' read-live \
  --store "$test_root/recovered_live" --window W01

expect_ok save-live-g02 '"revision": 3' save-live \
  --store "$test_root/working" --window W01 --expected-rev 2 \
  --desktop "$fixtures/desktop_g02.md" --artifact "$fixtures/blue_tree_note.txt" \
  --source fictional-fixture-g02

expect_ok append-correction '"revision": 4' append-event \
  --store "$test_root/working" --window W01 --expected-rev 3 \
  --type CORRECTION --summary 'The observatory is parked, not active.' \
  --source fictional-fixture-g02 --truth fictional

expect_ok freeze-g02 PUBLISHED_NOT_ACKED freeze \
  --store "$test_root/working" --window W01 --expected-rev 4 \
  --expected-head-rev 0 --target-generation G02

expect_hold old-window-write PUBLISHED_NOT_ACKED save-live \
  --store "$test_root/working" --window W01 --expected-rev 5 \
  --desktop "$fixtures/desktop_g02.md" --source forbidden-old-window-write

expect_ok export-frozen 'archive_frozen_g02.zip' export \
  --store "$test_root/working" --out "$test_root/archive_frozen_g02.zip"

expect_ok import-frozen PUBLISHED_NOT_ACKED import \
  --store "$test_root/recovered_frozen" --archive "$test_root/archive_frozen_g02.zip" \
  --expected-owner demo-owner --expected-project starlight-library \
  --expected-role librarian --expected-mode fictional

expect_hold wrong-generation STALE_POINTER_FOR_CUTOVER restore \
  --store "$test_root/recovered_frozen" --new-window W02 --expected-generation G03

expect_ok restore-g02 VERIFIED_AWAITING_ACK restore \
  --store "$test_root/recovered_frozen" --new-window W02 --expected-generation G02

expect_ok ack-g02 '"active_window": "W02"' ack \
  --store "$test_root/recovered_frozen" --new-window W02 \
  --expected-generation G02 --expected-head-rev 1

expect_ok post-ack-save '"state": "ACTIVE"' save-live \
  --store "$test_root/recovered_frozen" --window W02 --expected-rev 6 \
  --desktop "$fixtures/desktop_g02.md" --artifact "$fixtures/blue_tree_note.txt" \
  --source fictional-post-ack

expect_ok post-ack-inspect '"state": "ACTIVE"' inspect \
  --store "$test_root/recovered_frozen" --expected-generation G02

expect_hold stale-revision REVISION_CONFLICT save-live \
  --store "$test_root/recovered_frozen" --window W02 --expected-rev 6 \
  --desktop "$fixtures/desktop_g02.md" --source stale-write

expect_hold wrong-namespace NAMESPACE_MISMATCH import \
  --store "$test_root/wrong_namespace" --archive "$test_root/archive_frozen_g02.zip" \
  --expected-owner intruder --expected-project starlight-library \
  --expected-role librarian --expected-mode fictional

cp "$test_root/archive_frozen_g02.zip" "$test_root/corrupt.zip"
truncate -s -1 "$test_root/corrupt.zip"
expect_hold corrupt-archive INVALID_ARCHIVE import \
  --store "$test_root/corrupt_import" --archive "$test_root/corrupt.zip" \
  --expected-owner demo-owner --expected-project starlight-library \
  --expected-role librarian --expected-mode fictional

printf 'OFFLINE_ACCEPTANCE %s/22 PASS\n' "$passes"
printf 'TEST_ROOT %s\n' "$test_root"
