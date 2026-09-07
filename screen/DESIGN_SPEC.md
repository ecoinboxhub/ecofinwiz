# EcoFinwize Screen Design Spec — Conversation-First Layout

> **Date**: June 28, 2026
> **Purpose**: Defines the conversation-first UI layout for all screens, aligning with AGENTS.md, ARCHITECTURE.md, and PRODUCT_PRD.md.

---

## Color Palette (Exact Values)

| Token | Hex | Usage |
|-------|-----|-------|
| Sky-400 | `#38BDF8` | Gradient start (brand) |
| Sky-500 | `#0EA5E9` | Primary buttons, active nav, links |
| Sky-600 | `#0284C7` | Gradient end (brand) |
| Sky-50 | `#F0F9FF` | Light background, Kemi chat bubbles |
| Gold-400 | `#FBBF24` | Gradient start (Chidi brand) |
| Gold-500 | `#F59E0B` | Chidi accent, secondary buttons |
| Gold-600 | `#D97706` | Gradient end (Chidi brand) |
| Gold-50 | `#FFFBEB` | Light background, Chidi chat bubbles |
| Orange-500 | `#F97316` | Tertiary accent |
| Rose-500 | `#F43F5E` | Danger, alerts, delete |
| Gray-50 | `#F9FAFB` | Page background |
| Gray-100 | `#F3F4F6` | Card borders, dividers |
| Gray-200 | `#E5E7EB` | Input borders |
| Gray-400 | `#9CA3AF` | Muted text, inactive nav |
| Gray-500 | `#6B7280` | Body text |
| Gray-800 | `#1F2937` | Headings, primary text |
| White | `#FFFFFF` | Cards, nav background |

---

## Bottom Navigation Bar (5 Tabs — Fixed Order)

```
┌─────────┬─────────┬─────────┬─────────┬─────────┐
│  Kemi   │  Chidi  │  Home   │  Learn  │ Finance │
│  (1st)  │  (2nd)  │  (3rd)  │  (4th)  │  (5th)  │
└─────────┴─────────┴─────────┴─────────┴─────────┘
```

- **Active state**: Sky-500 (`#0EA5E9`) icon + text
- **Inactive state**: Gray-400 (`#9CA3AF`) icon + text
- **Background**: White (`#FFFFFF`) with `backdrop-filter: blur(12px)`
- **Top border**: 1px solid Gray-100 (`#F3F4F6`)
- **Safe area**: `padding-bottom: max(8px, env(safe-area-inset-bottom))`

### Tab Icons

| Tab | SVG Icon |
|-----|----------|
| Kemi | Star/sparkle icon |
| Chidi | Briefcase/business icon |
| Home | 4-square grid/dashboard icon |
| Learn | Book icon |
| Finance | Wallet icon |

---

## Screen 1: Kemi (Advisor) — Default Landing After Login

**File**: `screen.png`

**Principles**: Conversation-first. Kemi is the first thing users see after login.

**Layout**:
1. **Header**: EcoFinwize logo (left) + Notification bell + Profile avatar (right)
2. **Chat Header**: Kemi avatar (sky gradient) + "Kemi" title + "Financial Advisor" subtitle + New chat button
3. **Empty State**: Sparkle icon (sky-100 circle) + "Hi! I'm Kemi" + descriptive text + 4 suggestion chips (budgeting, saving, expenses, compound interest)
4. **Ad Banner** (visible for free tier): Gold gradient background, "Upgrade to Pro for an ad-free experience" + "Upgrade" CTA
5. **Bottom Nav**: Kemi (active, first position)

**Styling**:
- Kemi avatar: `linear-gradient(135deg, #38BDF8, #0284C7)`
- Chip hover: `#F0F9FF` background, `#BAE6FD` border
- Empty state icon: `#E0F2FE` circle with `#7DD3FC` SVG

---

## Screen 2: Login

**File**: `screen (2).png`

**Layout**:
1. **Center aligned**: EcoFinwize logo + "Welcome Back" heading + "Sign in to your account" subtext
2. **Card**: Email field (pre-filled), Password field with show/hide toggle, "Sign In" button (sky-500)
3. **Divider**: "or" between horizontal lines
4. **Google OAuth**: "Continue with Google" button with Google logo SVG
5. **Link**: "Don't have an account? Sign Up"

**Styling**:
- Background gradient: `linear-gradient(135deg, #F0F9FF, #FFFFFF, #FFFBEB)`
- Card: white, `border-radius: 16px`, `box-shadow: 0 1px 3px rgba(0,0,0,0.05)`
- Input fields: gray-50 background, gray-200 border, focus ring sky-400
- Button: sky-500 background, white text, `border-radius: 12px`

---

## Screen 3: Chidi (Mentor)

**File**: `screen (3).png`

**Principles**: Chidi as the second primary interface. Active conversation shown.

**Layout**:
1. **Header**: Standard EcoFinwize header
2. **Chat Header**: Chidi avatar (gold gradient) + "Chidi" title + "Business Mentor" subtitle + New chat button
3. **Conversation Messages** (3 messages shown):
   - Assistant: "Hi! I'm Chidi, your AI business mentor..."
   - User: "I need a business plan for my catering business"
   - Assistant: "Great! Let's get started..." (with tool dispatch result implicit)
4. **Input Bar**: Text field + Send button (gold gradient)
5. **Ad Banner**: "Upgrade to Pro for unlimited AI chats"
6. **Bottom Nav**: Chidi (active, second position)

**Styling**:
- Chidi avatar: `linear-gradient(135deg, #FBBF24, #D97706)`
- User message bubble: gold (`#F59E0B`) background, white text
- Assistant bubble: gray-100 (`#F3F4F6`) background, gray-800 text
- Send button: gold gradient matching Chidi brand

---

## Screen 4: Dashboard (Home)

**File**: `screen (4).png`

**Principles**: Snapshot view. Third tab, supports the conversation agents.

**Layout**:
1. **Header**: Standard header with notification bell (unread dot active)
2. **Welcome**: "Welcome back, [Name]!"
3. **Tip Card**: Sky gradient, "Finance Tip" label + daily tip text
4. **Summary Grid**: 2-column cards — Budget (remaining + progress bar) + Savings (progress + gold bar)
5. **Quick Actions**: 6 action cards in 3-column grid (Add Transaction, Set Budget, Create Goal, AI Advisor, Learn, Business)
6. **Recent Transactions**: 3 items with type icons (income green/expense rose)
7. **Bottom Nav**: Home (active, third position)

**Styling**:
- Tip card: `linear-gradient(135deg, #0EA5E9, #0284C7)`
- Progress bars: 6px height, `border-radius: 999px`
- Action card colors: sky-50/sky-500, gold-50/gold-500, orange-50/orange-500, rose-50/rose-500
- Transaction type colors: green-50/green-500 (income), rose-50/rose-500 (expense)

---

## Screen 5: Learning Hub

**File**: `screen (5).png`

**Layout**:
1. **Header**: Standard header
2. **Title**: "Learning Hub" + "Courses, articles & resources"
3. **Progress Card**: Circle progress indicator (3/12 completed) + "8 lessons completed" + Badge chips
4. **Tab Bar**: Courses (active) | Articles | News
5. **Featured Course**: Full-width card "Personal Finance 101" with book icon, description, lessons count, level badge
6. **Course Grid**: 2-column grid — "Smart Saving" (8 lessons, Beginner) + "Start Your Business" (15 lessons, Intermediate)
7. **Bottom Nav**: Learn (active, fourth position)

**Styling**:
- Course image area: sky gradient (`#E0F2FE` to `#BAE6FD`)
- Tab bar: gray-100 background, active tab white with shadow
- Badges: sky-100 background, sky-700 text

---

## Screen 6: Finance (Budgets)

**File**: `screen (6).png`

**Layout**:
1. **Header**: Standard header
2. **Title**: "Finance" + "Budgets & Transactions"
3. **Balance Card**: Sky gradient card showing "Monthly Budget" ₦450,000 with spent/remaining/transactions breakdown
4. **Tab Bar**: Budgets (active) | Transactions | Savings
5. **Budget List**: 3 items — Food & Drinks (65%, sky bar), Transport (45%, gold bar), Utilities (80%, rose bar)
6. **Quick Add**: "Add Budget" + "Add Transaction" dashed-border buttons
7. **Bottom Nav**: Finance (active, fifth position)

**Styling**:
- Balance card: `linear-gradient(135deg, #0EA5E9, #0284C7)`
- Budget progress bars: colored per category (sky, gold, rose)
- Budget items: white card, 14px font, category dot indicators
- Quick add: dashed border `#D1D5DB`, hover color `#0EA5E9`

---

## Conversation-First Alignment Checklist

| Requirement | Source | Status |
|-------------|--------|--------|
| Kemi is default after login | AGENTS.md §2, PRODUCT_PRD §3.1 | ✅ Kemi tab first |
| Chidi in navigation | ARCHITECTURE §1 | ✅ Chidi tab second |
| Dashboard is supporting view | AGENTS.md §3 | ✅ Third tab |
| Nav order: Kemi > Chidi > Home > Learn > Finance | PRODUCT_PRD §3 | ✅ 5-tab bottom bar |
| Same theme preserved | tailwind.config.js | ✅ Exact colors used |
| Chat is primary instead of forms | PRODUCT_PRD §2 | ✅ Kemi/Chidi are first 2 tabs |
| All financial tools accessible via chat | AGENTS.md §8 | ✅ Action dispatch in service layer |

---

## Mobile (Flutter) Differences

The Flutter mobile app mirrors the same 5-tab layout. Differences:
- Uses Material 3 bottom nav (`BottomNavigationBar`)
- Colors: `AppTheme.sky` (#0EA5E9), `AppTheme.gold` (#F59E0B)
- Screens: `AdvisorScreen()` (index 0), `MentorScreen()` (index 1), `DashboardScreen()` (index 2), `LearningScreen()` (index 3), `BudgetScreen()` (index 4)
- API calls use `ApiService` singleton instead of Axios
