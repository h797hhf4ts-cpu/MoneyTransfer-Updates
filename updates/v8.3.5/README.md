# MoneyTransfer V8.3.5

Combined local-first hotfix for operation edit/cancel and pending incoming transfer save.

- Cancelling a transaction restores all affected account balances.
- Commission added by the cancelled transaction is removed.
- Cancelled transaction and its audit reversal are excluded from financial statements, reports, and shift commission totals.
- Pending incoming transfer dialog keeps Save visible and supports F5 / Ctrl+Enter.
- Customer DB, license, installation identity, and backups are not replaced.
