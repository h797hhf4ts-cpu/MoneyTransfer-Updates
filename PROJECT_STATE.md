# MoneyTransfer Project State

This file exists so a new ChatGPT conversation can continue the project without re-discovering the update architecture.

## Current test target
- Current installed test client: V8.0.1 isolated client build.
- Final target online update: V8.0.2 TEST.
- Intended UI change: amount and commission controls have arrows on the left for +/-1.000 and arrows on the right for +/-0.050; values never go below zero; commission starts blank.

## What happened on 2026-09-01
- A first V8.0.2 binary upload was incomplete on GitHub (1542 bytes instead of the correct 106986 bytes).
- The client SHA-256 protection correctly blocked that bad package before installation.
- Do not disable SHA-256 verification.
- Direct opaque/base64 upload through the connector proved unreliable, so the update process was redesigned to avoid that failure mode.

## New verified two-stage update path
### Stage 1: updater bridge
- Root `latest.json` CURRENTLY points to V8.0.1.1 updater bridge.
- Package: `releases/MoneyTransfer_Update_V8_0_1_1_Updater_Bridge.zip`
- Current SHA-256 is stored in root `latest.json`.
- GitHub Actions workflow `build-bridge-update.yml` completed successfully.
- Bridge source: `bridge/update_engine_v2.py`.
- The bridge adds deterministic `text_patch.json` support. It validates exact match counts and aborts before changing installed files if the expected source text is not found.
- The bridge update does not include databases or client financial data.

### Stage 2: V8.0.2 verified text patch
- Package already built successfully: `releases/MoneyTransfer_Update_V8_0_2_Verified_TextPatch.zip`.
- Candidate feed data is stored at `patch_v802/latest-v802.json`.
- Current package SHA-256: `d38db4fe7defa28b0f58b2d44d7f6914bcc120c9433876037f9e686486c1c97d`.
- GitHub Actions workflow `build-v802-patch.yml` completed successfully.
- Patch source: `patch_v802/text_patch.json`.
- The patch was generated against V8.0.1 RC3 and locally verified to transform the desktop source exactly into the prepared V8.0.2 TEST source.
- It also installs `version.json` as V8.0.2.
- IMPORTANT: do not switch root `latest.json` to V8.0.2 until the test client has successfully installed the V8.0.1.1 updater bridge.

## Immediate next step
1. On the isolated V8.0.1 client, run the normal online update check.
2. It should offer V8.0.1.1 from the official locked Stable feed.
3. Install it and allow the app to restart.
4. After confirming restart, copy the contents of `patch_v802/latest-v802.json` into root `latest.json`.
5. Run update check again; it should offer V8.0.2.
6. Install V8.0.2 and verify restart, data/license preservation, and spinner behavior.

## Update rules
- Do not disable SHA-256 verification.
- Do not include SQLite databases, client balances, `license.json`, or private owner keys in update ZIPs.
- Preserve client data and license during updates.
- Stable updater source is pinned inside the client to the official repository `latest.json`.
- Prefer GitHub Actions-generated ZIPs from text sources/patches over direct binary uploads through the connector.

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
