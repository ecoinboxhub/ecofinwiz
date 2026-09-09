# iOS — Build & Publish

EcoFinwize has a full iOS target (`Runner`) with bundle id **`com.finwize.finwize`** and
display name **EcoFinwize**. Everything is wired for **GitHub Actions CI** on macOS —
no Mac needed on your side.

## Build on CI

Go to the repo → **Actions → "iOS Build & Publish" → Run workflow**.

- `codesign`: `false` → builds an **unsigned `.ipa`** and uploads it as a run artifact.
  This proves the app compiles for a real iPhone target. The artifact link is unique per run.
- `codesign`: `true` → signs with your Apple certificate + provisioning profile (requires
  the secrets below) and emits a **signed, installable `.ipa`**.
- `upload_appstore` (with signing): uploads the `.ipa` to **App Store Connect / TestFlight**.

The iOS binary is configured for the **production backend** already
(`FLUTTER_APP_FLAVOR=production`, API `https://ecofinwiz-api.onrender.com/api/v1`).

## Permanent / public link

iOS has no publicly-hosted direct-download URL like `.apk`. Distribution goes through
**TestFlight** (beta, email-invite links) or the **App Store** (public URL after approval):

1. Create an **Apple Developer Program** account (US$99/yr).
2. In **App Store Connect**: new app, bundle id `com.finwize.finwize`.
3. In the repo **Settings → Secrets and variables → Actions** add:
   - `APPLE_CERT_BASE64` — distribution certificate `.p12` as base64
   - `APPLE_CERT_PASSWORD` — `.p12` passphrase
   - `APPLE_PROVISIONING_PROFILE_BASE64` — App Store distribution `.mobileprovision` as base64
   - `APPLE_TEAM_ID` — team id (e.g. `X8ABCDEF12`)
   - `APPLE_ID` + `APPLE_APP_SPECIFIC_PASSWORD` — needed only for `upload_appstore`
4. Run the workflow with `codesign=true` + `upload_appstore=true`.
5. In App Store Connect → TestFlight, add testers — each gets a **permanent TestFlight invite link**.
6. After App Store review approval, the public link becomes
   `https://apps.apple.com/app/id<APPSTORE_APP_ID>`.

Until step 6 is completed the Android APK remains the always-available permanent download:
`https://ecofinwiz.vercel.app/downloads/ecofinwiz.apk`

## Local notes (macOS developer)

```bash
cd mobile
flutter pub get
flutter build ios --release --no-codesign          # compile check
flutter build ios --release                        # signed (Xcode signing configured)
```

## Quality gates run in the workflow

- `flutter analyze`
- `flutter test`
- device-target release compile — proof in the workflow runs: https://github.com/ecoinboxhub/ecofinwiz/actions/workflows/ios.yml