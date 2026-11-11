# Codex Prompt 03 — Independent phase verification

Act as an independent QA and security reviewer. Do not edit files during the first review pass.

Review the current diff and implementation against:
- `AGENTS.md`;
- the phase's acceptance criteria;
- product requirements;
- architecture and ADRs;
- security threat model;
- data integrity and sync protocol.

Check:
1. Scope creep and unauthorized future-phase behavior.
2. Data-loss and corruption paths.
3. Authentication, authorization, secret handling, and logging.
4. Error handling, retries, idempotency, and crash recovery.
5. Test quality and missing negative tests.
6. Resource and disk bounds.
7. Documentation accuracy versus actual behavior.

Run or inspect relevant tests only when authorized and safe. Do not access Telegram or real user data unless separately authorized.

Return findings ranked Critical / High / Medium / Low, with exact file/line references, exploit or failure scenario, impact, and recommended fix. Then map every acceptance criterion to PASS / FAIL / NOT TESTED with evidence. Do not declare PASS if mandatory criteria are untested.
