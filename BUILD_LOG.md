# PulakDrive Build and Verification Log

This log records observed commands and results only. Never include credentials, session data, plaintext keys, recovery material, private file contents, or sensitive local paths.

## 2026-11-11 — Repository instruction files

- Scope: create root-level `AGENTS.md`, `GOALS.md`, `PLANS.md`, `PROMPTS.md`, and this log, based on `PulakDrive_Phase0_Codex_Package/`.
- Application code changed: no.
- Dependencies installed: no.
- Telegram operations: none.
- Verification command: `git diff --check`.
- Result: could not run because this workspace is not a Git repository (exit 129; no `.git` directory).
- Fallback: checked each created file with `git diff --no-index --check /dev/null <file>`; no whitespace/conflict-marker diagnostics were emitted. This checks file contents but is not a substitute for a repository diff.
- Build/tests: not run; this was a documentation-only request and no build/test was requested.

## 2026-11-11 — Phase 0 architecture documentation completion

- Scope: complete Phase 0 documentation only; add runtime/API, crypto/recovery proposal, SQLite/state, Telegram adapter/research, backup/restore/failure, traceability, and ADR documents; update repository guidance and planning docs.
- Application code changed: no.
- Dependencies installed: no.
- Telegram operations or credentials: none; public documentation only.
- Personal file contents accessed: none.
- Official sources consulted (access date 2026-11-11):
  - https://core.telegram.org/api/files
  - https://core.telegram.org/api/config
  - https://core.telegram.org/api/file-references
  - https://core.telegram.org/api/terms
  - https://core.telegram.org/api/obtaining_api_id
  - https://docs.telethon.dev/en/stable/concepts/sessions.html
  - https://docs.telethon.dev/en/stable/concepts/errors.html
  - https://docs.telethon.dev/en/stable/modules/client.html
  - https://www.rfc-editor.org/rfc/rfc9106.html
  - https://csrc.nist.gov/pubs/sp/800/38/d/final
  - https://developer.apple.com/documentation/servicemanagement/smappservice
  - https://developer.apple.com/documentation/technotes/tn3137-on-mac-keychains
  - https://www.sqlite.org/wal.html
  - https://www.sqlite.org/lang_transaction.html
  - https://sqlite.org/backup.html
  - https://sqlite.org/foreignkeys.html
- Findings applied: document SQLite foreign-key activation per connection; treat Telegram upload limits as dynamic; keep Telegram file references refreshable; preserve user-approval boundary for live operations; clarify local metadata at-rest limits; mark crypto format as proposed pending independent review.
- Additional proposed resource control: 256 MiB aggregate encrypted staging cap and free-space reserve `max(256 MiB, 5% of volume)`, pending hardware/product validation.
- Verification: checked local Markdown links in newly added contracts; all resolved. Ran `git diff --no-index --check /dev/null <file>` over created/updated files; no whitespace/conflict-marker diagnostics. Normal `git diff --check` remains unavailable because there is no Git repository.
- Tests/build/resource benchmarks: not run; no implementation exists and this task authorizes documentation/planning only.
- Phase 0 gate: NOT COMPLETE. Independent crypto review, resolution of remaining design choices, final risk review, and explicit Phase 1 authorization remain outstanding.

## 2026-11-11 — Phase 0 security and architecture corrections

- Scope: documentation corrections only, following the security/architecture review request. Refined all-envelope AAD serialization; nonce crash/rollback handling; manifest key comparison and freshness limits; recovery kit/remote descriptor/channel confirmation; Argon2id/passphrase policy; native-owned WKWebView/API auth; LaunchAgent lifecycle consistency; traceability and ADR status.
- Application code/executable scaffolding: none created or modified.
- Dependencies: none installed.
- Telegram: no login, API/account/channel call, or session creation; public docs only.
- Credentials, keys, recovery secrets, personal file contents: none accessed.
- Official sources consulted (access date 2026-11-11):
  - https://www.rfc-editor.org/rfc/rfc9106.html — Argon2id v=0x13 and memory-constrained recommended parameters.
  - https://www.rfc-editor.org/rfc/rfc5869.html — HKDF salt/extract/expand and context.
  - https://csrc.nist.gov/pubs/sp/800/38/d/final — GCM/GMAC requirements and security bounds.
  - https://core.telegram.org/method/messages.getDialogs — current user dialog-list method and user-only constraint.
  - https://docs.telethon.dev/en/stable/modules/client.html — Telethon 1.45 dialog iteration, file sinks, and message retrieval API.
- Verification: checked relative Markdown links in the reviewed and related architecture documents; all links resolved. Checked whitespace/conflict-marker diagnostics in 19 changed/related Markdown files with `git diff --no-index --check /dev/null <file>`; none were emitted. The normal `git diff --check` command is unavailable because this workspace has no `.git` directory.
- Tests, builds, benchmarks, security certification: not run/performed. All design behavior remains unimplemented.
- Phase 0 gate: NOT COMPLETE. Independent crypto review, WKWebView/Keychain implementation review, final Critical/High risk review, acceptance of proposed formats, and explicit Phase 1 authorization remain outstanding.

## 2026-11-12 — Targeted Phase 0 security and consistency corrections

- Scope: documentation-only correction pass. The current workspace root was identified and the planning package was located at `PulakDrive_Phase0_Codex_Package/`; no `.git` directory exists at or under this root.
- Pre-edit state recorded before modifications with SHA-256 (`shasum -a 256`): root `AGENTS.md` `12fd108b36c1777e848fc6be7b302d3506ef59114ecb5a114758342f4ce8ec96`; `GOALS.md` `24b13f64d285abd8d791fba5d16980fc30a73a2a2e3c6b74b280c2b350a9c911`; `PLANS.md` `962b2a2a0c4620997f98fa7a22c5600a8a95a6312e484e0240607ad349f7a556`; `PROMPTS.md` `d3625ee5db8b7aefc6c75d136b7832834b79c78e643c3446ab001eef422ffdb5`; package `AGENTS.md` `beddb1901f2f7ae2fd3fac170fc1ef595d73507efdc1edda4e4f3e5e13ff2c64`; `CRYPTO_AND_RECOVERY.md` `047700becc32789e7b2f67f2fc758a544898ef37b28a98586d0b31de8fd0d1f4`; ADR-0007 `2325468b7b2016f032a74bee8a181167328003365fc72d559afad52ae5a17afd`; `PHASE_0_TRACEABILITY.md` `ef095006f45a4824ece9d66f863a9137a07eea6349955b4fc303db9aae7b2c5b`; `SQLITE_SCHEMA_AND_STATES.md` `37c47aaacd4a30c2389802aa68aab624d86bd4a124425e7a97101fcf89b572dd`; `DATA_MODEL.md` `083e80761aa264b3993bb215ff56c4f7ad6ecbceb11f24ae7c7db10f9bc0cc15`.
- Corrections documented: proposed v2 one-use AES-GCM key hierarchy and exact HKDF contexts; explicit direct-VMK-GCM ambiguous rollback analysis; exact recovery HKDF specification and pending deterministic expected values; Unicode 15.1/Argon2 interoperability requirements; one canonical fixed-12-byte chunk nonce encoding and exact lengths; chunk/manifest/descriptor remote association tables and commit invariants.
- Public standard referenced: https://www.rfc-editor.org/rfc/rfc5869.html — HKDF-Extract/Expand definitions and conformance-vector requirement (accessed 2026-11-12).
- Public Unicode source referenced: https://www.unicode.org/Public/15.1.0/ucd/NormalizationTest.txt and https://www.unicode.org/reports/tr15/ — pinned Unicode normalization version and conformance-data requirement (accessed 2026-11-12).
- Application code, scripts, tests, executable SQL, dependencies, Telegram operations, credentials, secrets, and unrelated personal files: none accessed or created.
- Verification: searched the documentation package for stale direct VMK/DEK GCM use, nonce-length variants, old version labels, direct chunk/manifest remote-object relationships, and phase-status contradictions. Remaining matches are explicit v1 supersession/withdrawal notes or the single fixed 12-byte v2 field; no conflicting active specification found. `git diff --check` could not run because the workspace root is not a Git repository (exit 129). Fallback `git diff --no-index --check /dev/null <file>` checked 10 Markdown files; no whitespace/conflict-marker diagnostics were emitted.
- Phase 0 gate: NOT COMPLETE. Independent cryptographic review, human approval of proposed v2 format, expected-vector generation/verification, Argon2/Unicode vectors and M1 benchmark, SQLite CHECK/trigger implementation tests, remaining architecture/security review, and human checkpoint-export policy decisions are outstanding. Phase 1 not started.

## 2026-11-12 — Final Phase 0 documentation corrections

- Scope: Markdown planning corrections only. Read the repository governance/planning documents and current crypto, schema, data-model, decision, threat, recovery, traceability, and phase-plan documents. Pre-edit SHA-256 state was recorded in the task session before changes; no Git repository is present at the workspace root, so a Git diff cannot represent this baseline.
- Changed the proposed envelope registry to distinguish framing `wire_version` from tag-1 `crypto_format_version`; only `(2,2)` is currently registered. Fixed chunk encoding remains the single 12-byte nonce representation with trailing 16-byte GCM tag; no deployed v2 bytes exist.
- Specified a strict 188-byte portable checkpoint record and exact proposed HKDF-SHA-256/HMAC-SHA-256 derivation and preimage. No expected PulakDrive checkpoint vector was fabricated; generation and independent verification remain pending. Defined proposed checkpoint ancestry/fork/withholding behavior and export policy while leaving human UX choices open.
- Replaced the three-association-table logical remote-location model with one `remote_object_binding` proposal, keyed by `remote_object_id`, with typed target groups, restrictive relationships, kind consistency checks/triggers, and confirmed-reference commit semantics. This is not executable SQL or an approved migration.
- Updated ADR-0007, decision register, threat model, backup/restore behavior, traceability, data model, schema specification, and phase plan to preserve proposed-vs-accepted status. Phase 0 remains incomplete and Phase 1 remains unauthorized.
- Official SQLite references consulted (2026-11-12): [Foreign Key Support](https://www.sqlite.org/foreignkeys.html) documents that foreign-key enforcement must be enabled per connection and describes composite keys; [CREATE TRIGGER](https://www.sqlite.org/lang_createtrigger.html) documents row-trigger behavior. These sources support the logical enforcement proposal but do not validate an unimplemented schema.
- Restrictions: no application code, executable SQL, scripts, tests, dependencies, Telegram access, credentials/secrets, or unrelated personal files were used or created.
- Verification performed: searched target documentation for stale `chunk_remote`, `manifest_remote`, and `vault_descriptor_remote` model references; checked version namespace definitions and checkpoint serialization for cross-document consistency; ran Markdown whitespace/conflict-marker checks on every changed Markdown file using `git diff --no-index --check /dev/null <file>` because `git diff --check` cannot run without a Git repository. No tests, builds, benchmarks, crypto vector computations, or independent security review were performed.
- Phase 0 acceptance: NOT COMPLETE. Independent cryptographic review, generated and verified recovery/checkpoint/normalization vectors, 8 GB M1 Argon2 benchmark, SQLite CHECK/trigger implementation tests, remaining architecture/security review, and human checkpoint-export policy decisions are outstanding. No cryptographic correctness or certification is claimed.

## 2026-11-14 — Phase 1 Milestone 1 development-foundation continuation

- Authorization: limited to the requested Milestone 1 foundation work. Existing Phase 0 review gates and all blocked production functionality remain unchanged.
- Recovery: inspected the existing Git repository, governance and Phase 0 architecture documents, implementation, tests, dependency declarations, and generated paths before editing. Preserved the existing uncommitted work; no commit, staging, reset, clean, or push was performed.
- Repository hygiene: consolidated `.gitignore` rules for virtual environments, Swift/npm build output, Python caches, coverage output, environment files, and logs. Verified that `.venv`, `.build`, `node_modules`, `dist`, and tool caches are ignored while source remains visible.
- Python: retained the existing domain behavior, resolved all Ruff findings, configured deterministic pytest-asyncio fixture scope, and corrected the PEP 517 backend to `setuptools.build_meta`. Direct runtime and development dependencies remain exactly pinned and consistent.
- Python lock limitation: an experimental transitive hash-lock generation command could not resolve the package index in the restricted environment. No hashes were fabricated and no incomplete lockfile was retained.
- Shared contracts: aligned enum values, snake-case serialized field names, required fields, and nullable backup timestamp with the actual Pydantic models. Added protocol-version assumptions without generating an API client.
- Frontend: reduced the dashboard to deterministic mock-only data showing an unconfigured vault and no completed backup. Removed simulated successful-backup states and contradictory ready/empty-vault states. Added four Vitest checks, including serialized contract keys and protection against falsely reporting backup success.
- Automation: root build, test, and lint scripts resolve the repository root from the script path, stop on the first failure, require the project Python virtual environment, use `npm ci`, and do not delete user data or modify Git state.
- Documentation: updated `README.md` to distinguish approved target architecture from implemented functionality and to record setup, commands, deferrals, and known limitations accurately.
- Toolchain observed: Swift 6.1.2, Python 3.12.14, Node.js 26.5.0, npm 11.17.0.
- Final component verification after documentation:
  - `cd apps/macos && swift test` — 6 tests passed.
  - `cd services/core && .venv/bin/python -m pytest && .venv/bin/python -m ruff check .` — 52 tests passed; Ruff passed with zero findings.
  - `cd apps/web && npm ci && npm run typecheck && npm run lint && npm test && npm run build` — installation, typecheck, ESLint, 4 Vitest tests, and Vite build passed. Build output was 0.40 kB HTML, 3.13 kB CSS, and 147.83 kB JavaScript before gzip.
- Final root verification, invoked by absolute path from outside the repository:
  - `scripts/build.sh` — passed: Swift build, Python `compileall`, clean npm install, TypeScript check, and Vite build.
  - `scripts/test.sh` — passed: 6 Swift + 52 Python + 4 frontend = 62 tests.
  - `scripts/lint.sh` — passed: Ruff, TypeScript, and ESLint.
- Install notices: npm reported upstream deprecation/support notices for pinned development dependencies and two pending install-script approvals. The explicit `npm ci` audit reported 19 dependency findings (7 low, 9 moderate, 1 high, and 2 critical); no unreviewed automatic or forced upgrade was applied. Installation and all requested frontend checks succeeded.
- Repository checks: `git diff --check` passed; generated dependency, build, and cache paths were confirmed ignored; the index is unchanged with no staged files. The working tree retains the recovered uncommitted foundation files plus the `.gitignore` modification.
- Restricted operations: no Telegram/account/channel access, credentials, keys, recovery data, private file contents, production cryptography, Keychain integration, bearer authentication, WKWebView bridge, LaunchAgent registration, filesystem monitoring, SQLite schema, backup, synchronization, or restore implementation.
- Milestone status: the user-authorized Phase 1 Milestone 1 development-foundation tasks are complete and verified. This does not close or supersede the outstanding Phase 0 architecture and security approval gates.