# MoneyTransfer V8.3.4 canonical project state

Desktop is LOCAL-FIRST. SQLite on the client is the single source for operations, balances, customer debts, pending transfers, operation log, account statements, reports, reconciliation and shift closing. Internet and the local API server are optional for these desktop functions.

Official Stable feed:
https://raw.githubusercontent.com/h797hhf4ts-cpu/MoneyTransfer-Updates/main/latest.json

Client download metadata:
https://raw.githubusercontent.com/h797hhf4ts-cpu/MoneyTransfer-Updates/main/client-download.json

Current full-installer baseline:
- Version: `8.3.4`
- Sequence: `803400`
- Schema: `9`
- Release tag: `v8.3.4`
- Asset: `MoneyTransfer_Setup_V8_3_4.exe`
- SHA-256: `9f546a51cd2e858f4f7d02b638befe6dbdfab2534df32fe28f20812161ed19a0`
- Release is published as Stable/Latest and passed Windows installation/runtime smoke testing before customer delivery.

Update ordering uses monotonically increasing `sequence`; never decrease or reuse it. Updater accepts legacy `package_url + sha256` or direct `files` entries (`path`, `url`, `sha256`). Future source-only updates after V8.3.4 may use direct-files publishing under `updates/<version>/...` and must update `latest.json` only after all payload files are published and verified.

V8.3.4 is a full-installer baseline because its embedded Windows runtime includes PDF dependencies (`reportlab`, `arabic-reshaper`, `python-bidi`). Do not attempt to upgrade pre-V8.3.4 clients to V8.3.4 using direct-files only; direct-files cannot replace embedded EXE runtime dependencies.

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
- For a new update, publish payload files first, verify raw URLs and hashes, then update `latest.json` last.
- Do not change `latest.json` to an untested or incomplete build.
- If an update changes embedded runtime dependencies, native/binary dependencies, PyInstaller requirements or `MoneyTransfer.exe`, publish a new full Setup baseline instead of direct-files.

V8.3.4 Windows validation completed on 2026-09-01:
- Installer built and launched successfully.
- Existing-data/new-data setup choice tested successfully.
- Server-runtime import blocker fixed by adding `verify_owner_reset_token`.
- Setup asset published to GitHub release `v8.3.4`.
- Client Setup SHA-256 verified against the published GitHub asset.

Owner Control Center remains private and separate. Never ship seller private RSA key or owner-only control tools with client builds.

See `UPDATE_SYSTEM.md` and `update-system/stable-baseline.json` for the current publishing protocol.
