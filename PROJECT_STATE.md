# MoneyTransfer Project State

This file exists so a new ChatGPT conversation can continue the project without re-discovering the update architecture.

## Current stable state
- V8.0.1.1 updater bridge was successfully installed on the real application.
- V8.0.2 was then successfully installed online on the real application.
- Online update detection, SHA-256 verification, install, restart, and version registration are working.
- V8.0.2 spinner behavior: amount and commission controls have arrows on the left for +/-1.000 and arrows on the right for +/-0.050; values never go below zero; commission starts blank.

## V8.0.3 FINAL branding prepared
- Final app version prepared locally: V8.0.3 Stable.
- Approved visual direction: modern navy/teal financial-management login interface based on the generated branding mockup.
- Login screen now uses the approved visual identity panel and a live interactive login form.
- Developer shown as: أنس العمران.
- Developer contact email is embedded in the app login and sidebar.
- Developer phone is embedded in the app login and sidebar.
- Sidebar developer email and phone are clickable.
- Final source reads version from `version.json` using `app_version`.
- Fresh commercial DB remains zeroed for transactions/customers; owner-only tools and private RSA key must never ship with client builds.

## V8.0.3 local artifacts prepared
- `MoneyTransfer_Update_V8_0_3_FINAL_Branding.zip`
  - contains only update manifest, version.json, desktop source, and text-encoded login branding asset.
  - contains no SQLite database, client data, license.json, or owner private key.
  - SHA-256: `1fb4a6ff642dce08c1b8d4321d9ef0757b6a83c2c27060373f49200cb4c7264a`
- `MoneyTransfer_Setup_Builder_V8_0_3_FINAL.zip`
  - Windows one-click builder that produces `installer_output\MoneyTransfer_Setup_V8_0_3_FINAL.exe`.
  - SHA-256: `3c4dffc8f353851628fa0e6f4ce4c31269a9e70c33a59147689d0ea604cc7b02`

## Important V8.0.1.1 lessons already fixed
- A bridge package initially omitted the visible-version file, then used the wrong `version` field.
- MoneyTransfer reads `app_version`; incorrect version metadata caused the UI to fall back to V7.36.0.
- R3 fixed this using the correct `app_version` schema and an immutable package filename.
- Never reuse a release ZIP filename after changing its contents; publish a new immutable filename to avoid raw/CDN cache SHA mismatches.

## Update rules
- Do not disable SHA-256 verification.
- Do not include SQLite databases, client balances, `license.json`, or private owner keys in update ZIPs.
- Preserve client data and license during updates.
- Stable updater source is pinned inside the client to the official repository `latest.json`.
- Prefer GitHub Actions-generated ZIPs from text sources/patches over direct binary uploads through the connector.
- Every release must use `version.json` with `app_version`, `api_compatibility`, `runtime_version`, `schema_version`, and `channel`.
- Every changed release package should use a new immutable filename.

## Commercial release gates before delivery
- Re-check license enforcement on a fresh commercial install.
- Re-check expired-license read-only mode.
- Re-check renewal and clock rollback protection.
- Re-check backup/rollback and reset permissions.
- Confirm fresh-install first launch and login UI.
- Confirm a full online update cycle preserves data and license.
- Never ship the private Owner Control Center or private RSA key to clients.

## Owner Control Center
- Keep it private and separate from client distribution.
- It tracks products, customer/business details, phone/email, installation ID, plan, expiry, notes, activation token, renewal history, and owner-signed password reset tokens.
