# Finwize Mobile — UI/UX Humanization & Design-System Update Prompt

> **Target**: `mobile/` Flutter app (Android APK). **Repo root**: `C:\Users\ibrah\Documents\Gemini\Fellow_AI_Fintech_NextGen_Leaders_Fellowship_2026\Finwize`
> **Reference screens**: `C:\Users\ibrah\Documents\Gemini\Fellow_AI_Fintech_NextGen_Leaders_Fellowship_2026\Finwize\screen\pinterest screens`
> **Run all Flutter commands from `mobile/`** using `& "C:\src\flutter\bin\flutter.bat" ...`

---

## 1. Your role

You are a senior Flutter mobile engineer and UI/UX designer. Your job is to give the Finwize mobile app a cohesive, warm, human, premium fintech design — one that could belong to a top-tier African fintech (think PalmPay, Cowrywise, UBA). Remove every trace of "AI-template" styling and machine-like wording. Do NOT change app functionality, API contracts, or navigation logic — this is a pure design + copy humanization pass.

## 2. Product context

Finwize (brand: **EcoFinwize**) is a conversational financial-guidance platform for African youths, freelancers, SMEs, students, and public-service workers. Three human advisors — **Kemi** (personal finance), **Chidi** (business mentor), **Musa** (investment) — plus budgets, savings, transactions, learning, calculators, world markets, business tools, profile. Low-bandwidth and accessibility-first.

## 3. New color system (MANDATORY)

Replace every hardcoded color and every token in `mobile/lib/config/theme.dart` with this palette. It is derived from the reference screens **"Finance Mobile UI UX (1).jpg"** (primary mint/teal family) and **"Investing Mobile App UI_UX Design.jpg"** (warm sage neutrals), with a humanized warm gold retained from the existing brand.

| Token | Hex | Usage |
|---|---|---|
| `primary` / deep teal | `#0E6F73` | Brand color, primary buttons, active nav, links, progress fill |
| `primaryDark` | `#094D53` | Header/dark surfaces, bottom sheets, gradient deep end |
| `mint` / accent | `#5FD0B3` | Positive highlights, hero accents, secondary buttons, toggle-on |
| `mintSoft` | `#E5F4EF` | Tinted cards, chips, avatar backgrounds, success-badge bg |
| `gold` / premium | `#D9A441` | Savings, premium/Pro plan, badges, secondary accent |
| `goldSoft` | `#FBF0DC` | Premium card tints, empty-state highlights |
| `ink` / text | `#123334` | Primary text (replaces `#1F2937`) |
| `muted` | `#5E7371` | Secondary text (replaces `#6B7280`) |
| `softMuted` | `#93A7A3` | Tertiary/hints (replaces `#9CA3AF`) |
| `bg` / page | `#F6F9F7` | Scaffold background, warm off-white (replaces `#F9FAFB`) |
| `surface` | `#FFFFFF` | Cards, inputs, sheets |
| `border` | `#E3EBE7` | Card/input borders (replaces `#E5E7EB`, `#F3F4F6`) |
| `success` / up | `#2F9E7F` | Positive change, gains, savings-up |
| `error` / down | `#C65D5A` | Negative change, errors, delete (replaces harsh rose) |
| Gradients | `tealMint [ #0E6F73 → #5FD0B3 ]`, `gold [ #D9A441 → #E8B84F ]`, `mint [ #5FD0B3 → #2F9E7F ]` | Hero banners, empty states, buttons |

**Rules**
- Delete ALL old Tailwind-style tokens (`0xFF0EA5E9`, `0xFFF59E0B`, `0xFFF97316`, `0xFFF43F5E`, `0xFF10B981`, `0xFF1F2937`, `0xFF6B7280`, `0xFF9CA3AF`, `0xFFF9FAFB`, `0xFFE5E7EB`, `0xFFF3F4F6`, `0xFFE0F2FE`, `0xFFFEF3C7`, `0xFFD1FAE5`, `0xFFFEF2F2`, `0xFFFFEDD5`, `0xFFFFE4E6`, `0xFF38BDF8`, `0xFFFB7185`, `0xFFFBBF24`, `0xFFFB923C`, `0xFF34D399`, `0xFF059669`).
- Expose semantic names in `AppTheme` (as `static const Color`) and `AppColors` (as `List<Color>` gradients). All screens must reference these tokens — no inline hex anywhere except the token definitions.
- Ensure AA contrast: body text uses `ink`/`muted` on `surface`/`bg` only.

## 4. Spacing, margins, corners (MANDATORY)

Enforce a consistent 8-pt grid across every screen:
- Screen padding: **20** (auth/hero screens may use 24)
- Inline gaps between siblings: 8 / 12 / 16 / 24
- Section gaps: 24
- Card inner padding: **16**
- Corner radii: cards **16**, inputs & chips **12**, buttons **12**, avatars/icon-tiles **14–16**
- Icon sizes: 24 default, 20 compact, 40–64 hero/empty-state
- Buttons: minimum height 48, full-width on primary CTAs
- Use `EdgeInsets` constants or named consts; no magic values
- Add **Semantics / Key tags** to interactive & data elements for the QA golden harness and accessibility, e.g. `Key('market_row_ngx')`, `Semantics(label: 'NGX All-Share Index, up 0.58%')` on market rows, `Key('quick_action_markets')` on dashboard chips, `Key('chat_input')` on advisor text fields. Do not break existing `find.text(...)` selectors used by tests.

## 5. AI-trace removal (MANDATORY checklist)

Replace every AI/robot reference with warm, human phrasing and iconography:

| File | Change |
|---|---|
| `lib/screens/landing_screen.dart` | Badge "AI-Powered Financial Guidance" → **"Financial guidance you can trust"**; headline "Powered by AI" → **"Built for your financial future"**; remove `Icons.auto_awesome` sparkle icon |
| `lib/screens/dashboard_screen.dart` | Quick-action "AI Advisor" → **"Kemi"** (use `Icons.forum_outlined`); daily-tip `Icons.auto_awesome` → `Icons.lightbulb_outline` |
| `lib/screens/advisor_screen.dart` | AppBar `Icons.auto_awesome` → `Icons.forum`; empty-state robot `Icons.smart_toy` (64px) → warm avatar circle with `Icons.waving_hand` or `Icons.forum` in `mintSoft` |
| `lib/screens/mentor_screen.dart`, `lib/screens/investment_screen.dart` | Mirror the advisor changes; consistent persona iconography |
| `lib/screens/business_plan_screen.dart` | "get an AI-generated plan" → **"get a detailed plan ready for your bank"**; `Icons.auto_awesome` → `Icons.description_outlined` |
| `lib/screens/learning_screen.dart` | `Icons.auto_awesome` → track/content icon (`Icons.menu_book_outlined`) |
| `lib/screens/markets_screen.dart` | Keep functionality; restyle with new tokens; ensure disclaimer copy stays visible |
| Any remaining `smart_toy`, `auto_awesome`, `robot`, "AI-", "chatbot", "Powered by AI", "artificial intelligence" strings | Remove or humanize |

## 6. Screen-by-screen polish

Apply the design system to ALL screens under `mobile/lib/screens/` (auth, chat, dashboard, budget, transactions, savings, learning, articles, news, forum, calculators, markets, business plan/tasks/invoices, profile, notifications, pricing, admin). Humanize microcopy (plain language, warm tone), fix inconsistent paddings, align every card/input/chip to the tokens above, and keep **all existing functionality and navigation intact**.

## 7. Mobile app icon (MANDATORY)

1. Redesign `mobile/assets/icon/finwize_icon.svg` (1024×1024, rounded square) using the new palette: deep-teal→mint gradient background (`#0E6F73 → #5FD0B3`), a simple, human, memorable mark (e.g., an upward "growth" leaf/coin motif) in warm gold (`#D9A441`) and white. No robots, no sparkles, no text.
2. Render `app_icon.png` and `icon_master.png` at 1024×1024 from the SVG (keep files identical/synced).
3. Regenerate the Android launcher set in `mobile/android/app/src/main/res/`: `mipmap-{mdpi,hdpi,xhdpi,xxhdpi,xxxhdpi}/ic_launcher.png`, `ic_launcher_round.png`, `ic_launcher_foreground.png`, `launch_image.png` (respect each density's expected pixel size; adaptive-icon foreground must leave the outer ~25% safe).
4. Update `res/values/colors.xml`: `ic_launcher_background` → `#0E6F73`, `launch_background` → `#F6F9F7`.
5. Verify the icon renders via the golden harness (it will appear on relevant screenshots) and that the debug APK still builds.

## 8. Verification — Definition of Done

After every change, from `mobile/`:
1. `& "C:\src\flutter\bin\flutter.bat" analyze` → **0 errors** (only pre-existing info-level lints allowed).
2. `& "C:\src\flutter\bin\flutter.bat" test test/screenshots/screenshots_test.dart --update-goldens` then `& "C:\src\flutter\bin\flutter.bat" test test/screenshots/qa_capture_test.dart --update-goldens` to regenerate ALL goldens with the new theme (expected — every screenshot changes).
3. `& "C:\src\flutter\bin\flutter.bat" test` → **all tests pass** (73+). If a test asserts a color, copy string, or icon that legitimately changed, update the assertion to match the new design.
4. `& "C:\src\flutter\bin\flutter.bat" build apk --debug` → builds successfully.
5. Copy the regenerated screenshots to `C:\Users\ibrah\Documents\Gemini\Fellow_AI_Fintech_NextGen_Leaders_Fellowship_2026\Finwize\QA_artifacts\screenshots\` and rebuild `QA_artifacts\finwize_app_demo.mp4` from the updated frames (46 PNGs, title + 44 shots + end; 412×892, 30 fps, xfade chain offset 2.5 s, duration 0.5 s — reuse `C:\Users\ibrah\AppData\Local\Temp\opencode\build_video.py`).

## 9. Constraints

- **Do NOT** touch backend, API routes, models, or business logic.
- **Do NOT** change screen navigation, routes, or the 6-tab shell structure.
- **Do NOT** remove, rename, or relocate test files.
- Keep the app human, low-bandwidth-friendly, accessible (WCAG AA), and true to the African-fintech identity. When unsure, choose warmth, clarity, and accessibility over decoration.

## 10. Report

End with a concise summary: files changed, icon assets regenerated, tests run (counts), goldens regenerated, and confirmation that no functionality was altered.