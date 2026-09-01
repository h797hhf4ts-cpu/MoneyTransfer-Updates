# MoneyTransfer V8.2.0 canonical project state

Desktop is LOCAL-FIRST. SQLite on the client is the single source for operations, balances, customer debts, pending transfers, operation log, account statements, reports, reconciliation and shift closing. Internet and the local API server are optional for these desktop functions.

Official feed:
https://raw.githubusercontent.com/h797hhf4ts-cpu/MoneyTransfer-Updates/main/latest.json

Update ordering uses monotonically increasing `sequence`; V8.2.0 = 802000. Never decrease or reuse it. Updater accepts legacy package_url+sha256 or direct `files` entries (path,url,sha256), allowing future Python/JSON updates to be published directly to GitHub without manually uploading a release ZIP.

Licensing is RSA signed and verified locally. Client includes the public key only. Seller private key stays in the private Owner Control Center. Enforced expired/invalid licenses are read-only for financial writes; viewing, reports, settings and backups remain available.

Accounting invariants:
- Incoming: selected source/counter decreases, selected electronic destination increases.
- Outgoing: selected electronic source decreases, selected counter/destination increases.
- Pending receipt: electronic destination increases immediately; counter/cash unchanged until settlement.
- Pending settlement: counter/cash decreases at delivery; commission belongs to settlement shift.
- Debt add: customer debt +amount; selected account -amount.
- Debt repayment: customer debt -amount; selected account +amount.
- Accounting-only rows must not inflate commercial volume.

Update safety:
- Never replace `financial_pos.db`, server data, `license.json`, `installation.json` or backups.
- Keep TLS verification and SHA-256 verification enabled.
- Stable feed is always the official GitHub feed.
- Future normal source updates should prefer direct-files publishing under `updates/<version>/...` plus a new `latest.json` with a higher `sequence`.
- Do not change `latest.json` to an untested build.

Current local RC artifacts prepared on 2026-09-01:
- `MoneyTransfer_Update_V8_2_0_FULL_STABILITY.zip`
- `MoneyTransfer_FULL_DEVELOPMENT_V8_2_0_FINAL_RC.zip`
- Static Python compile: PASS
- Static regression checks: PASS
- Seed SQLite integrity: PASS
- Windows GUI/installer/client migration still require laptop validation before customer delivery.

Owner Control Center remains private and separate. Never ship seller private RSA key or owner-only control tools with client builds.
