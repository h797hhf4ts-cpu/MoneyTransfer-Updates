# MoneyTransfer Update System

## Current stable client baseline

- Version: `8.3.4`
- Sequence: `803400`
- Windows Setup release: `v8.3.4`
- Setup asset: `MoneyTransfer_Setup_V8_3_4.exe`
- SHA-256: `9f546a51cd2e858f4f7d02b638befe6dbdfab2534df32fe28f20812161ed19a0`

V8.3.4 is the minimum full-installer baseline for the current updater architecture because the Windows executable embeds runtime dependencies used by PDF export (`reportlab`, `arabic-reshaper`, `python-bidi`).

## Stable feed

The installed client reads only the official Stable feed:

`https://raw.githubusercontent.com/h797hhf4ts-cpu/MoneyTransfer-Updates/main/latest.json`

The updater supports two payload modes:

1. Legacy ZIP mode using `package_url` + `sha256`.
2. `direct_files` mode using a `files` array of `{path,url,sha256}` entries.

`sequence` is authoritative when present and must always increase. Never reuse or decrease a published sequence.

## Safe publishing rule

Do not promote a new `latest.json` until all payload files have already been published and their SHA-256 hashes have been verified. Publish payload files first, verify their raw URLs, and update `latest.json` last. This prevents clients from seeing a partially published update.

For a source-only release after V8.3.4, place changed UTF-8 files under `updates/<version>/...`, calculate SHA-256 for each file, then publish a feed similar to:

```json
{
  "product": "MoneyTransfer",
  "version": "8.3.5",
  "channel": "Stable",
  "sequence": 803500,
  "schema_version": 9,
  "files": [
    {
      "path": "desktop/financial_transfer_system_v7_9_0.py",
      "url": "https://raw.githubusercontent.com/h797hhf4ts-cpu/MoneyTransfer-Updates/main/updates/v8.3.5/desktop/financial_transfer_system_v7_9_0.py",
      "sha256": "<64-hex-sha256>"
    }
  ],
  "notes_ar": [
    "وصف مختصر للتحديث."
  ]
}
```

## When direct_files must NOT be used

Do not use `direct_files` when an update requires a changed embedded Python runtime, new native/binary dependency, new PyInstaller hidden import, or a replacement of `MoneyTransfer.exe`. In those cases build a new Windows Setup and publish it as a new full installer baseline.

## Protected customer data

Update payloads must never include or replace:

- `financial_pos.db`
- `server/data`
- `server_runtime/data`
- `data`
- `backups`
- `updates/backups`
- `license.json`
- `installation.json`

The seller private RSA key and Owner Control Center must never be published in this repository or shipped with client updates.

## Security requirements

- TLS certificate verification must remain enabled.
- Every downloaded payload file must be verified with SHA-256 before installation.
- Stable feed must remain pinned to the official GitHub repository.
- Do not use hidden remote-control or backdoor behavior. Updates are software delivery only.

## Promotion checklist

Before changing `latest.json`:

- Windows application launches successfully.
- Local-first financial operations work with internet disconnected.
- Database and license survive the update.
- Pending transfers and debts retain accounting behavior.
- PDF export and Windows printing work if changed.
- Mobile bridge/pages work if changed.
- Every update payload SHA-256 is verified.
- `sequence` is greater than the currently published sequence.

`latest.json` is always the final publishing step.
