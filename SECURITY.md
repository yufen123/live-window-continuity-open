# Security and privacy boundary

This experimental tool is an offline consistency checker for selected,
non-sensitive context. It is not a secure vault, identity service, authorization
system, or authenticated backup protocol.

- Archives are plaintext. Keep them in user-controlled, access-controlled storage.
- Use trusted archives. A party able to rewrite all files can recompute hashes;
  hash validity does not authenticate the creator.
- The CLI does not classify sensitive data. The agent and user must choose safe
  inputs. Do not test with credentials, private chats, health or student records.
- Local revision guards do not prevent competing remote uploads. Durable storage
  must implement its own compare-and-swap or equivalent version guard.
- Restore and ACK are data receipts, not permission to act or accept a role.
- No networking, analytics, credentials, or storage service is bundled.

The acceptance suite is not a comprehensive security audit. Untrusted-archive
resource exhaustion, hostile local filesystem races, multi-user permissions,
and cross-platform behavior need further hardening and testing before broader
trust or sensitive-data use. In particular, the importer parses the archive
manifest before checking aggregate uncompressed size; it should not be exposed
as an arbitrary public-upload service.

No private vulnerability-reporting channel is configured by this release. Do not
post secrets, personal data, or sensitive exploit details in public issues.
Use public issues only for non-sensitive reports or to request a private contact
route before sharing details.
