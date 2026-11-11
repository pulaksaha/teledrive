# Codex Workflow

## Operating principle

Use Codex as a disciplined engineering agent, not as an autonomous project owner. The user approves scope and phase transitions.

## Required cycle

1. **Read:** inspect `AGENTS.md`, relevant specs, ADRs, and current phase.
2. **Plan:** explain intended changes, files, risks, dependencies, and verification.
3. **Approval:** wait if the request exceeds current authorization.
4. **Implement:** make the smallest change set for the approved phase.
5. **Verify:** run focused tests, full relevant tests, static checks, and security checks.
6. **Independent review:** ask Codex to review the diff against requirements and threat model without editing first.
7. **Remediate:** fix findings and rerun tests.
8. **Close:** update docs, roadmap, ADRs, and build log; report gate status.
9. **Stop:** do not begin the next phase automatically.

## Evidence rules

- Include actual commands and outputs or concise result summaries.
- Never fabricate test results.
- Separate implemented, tested, reviewed, and unverified behavior.
- For external documentation research, record official URL, access date, and the exact claim supported.
- Treat benchmarks as measurements with hardware, OS, sample size, and methodology.

## Phase authorization

A prompt that says "plan Phase 1" is not authorization to implement Phase 1. Implementation requires explicit wording from the user, such as: "I approve Phase 1 implementation."

## Security review rules

- Use synthetic data and fake credentials.
- Never ask the user to paste OTP, 2FA, Telegram session, passphrase, recovery key, or API hash into Codex.
- Never print secrets to debug output.
- No live Telegram tests until a later phase is explicitly approved and a safe test procedure is documented.
