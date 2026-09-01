# MoneyTransfer Project State

This file exists so a new ChatGPT conversation can continue the project without re-discovering the update architecture.

## Current test target
- Current installed test client: V8.0.1 isolated client build.
- Target online update: V8.0.2 TEST.
- Intended UI change: amount and commission controls have arrows on the left for +/-1.000 and arrows on the right for +/-0.050; values never go below zero; commission starts blank.
- Local verified update ZIP size: 106986 bytes.
- Required SHA-256: e1608c69a8d9f28ee3dc59d1326ee04364dc18004465c3d4ae17c426b5ef8701.
- Expected published filename: releases/MoneyTransfer_Update_V8_0_2_TEST_Spinner.zip.

## Update rules
- Do not disable SHA-256 verification.
- Do not include SQLite databases, client balances, license.json, or private owner keys in update ZIPs.
- Preserve client data and license during updates.
- Stable updater source is pinned inside the client to the official repository latest.json.
- A failed SHA-256 test on 2026-09-01 was caused by an incomplete GitHub binary (1542 bytes instead of 106986 bytes). The updater correctly blocked installation.
- Use .github/workflows/build-v802-upload.yml to reconstruct the binary from base64 chunks under v802_payload/, verify exact size and SHA-256, then publish it.

## Commercial release gates before delivery
- Re-check license enforcement on a fresh commercial install.
- Re-check expired-license read-only mode.
- Re-check renewal and clock rollback protection.
- Re-check backup/rollback and reset permissions.
- Complete one full online update test: detection -> download -> SHA-256 -> backup -> install -> restart -> data/license preserved.
- Never ship the private Owner Control Center or private RSA key to clients.

## Owner Control Center
- Keep it private and separate from client distribution.
- It tracks products, customer/business details, phone/email, installation ID, plan, expiry, notes, activation token, renewal history, and owner-signed password reset tokens.
