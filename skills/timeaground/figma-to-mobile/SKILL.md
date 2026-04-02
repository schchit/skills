---
name: figma-to-mobile
description: >
  Convert Figma designs to mobile UI code.
  Supports Android (Jetpack Compose, XML) and iOS (SwiftUI, UIKit).
  Use when a user provides a Figma link and wants mobile layout code.
  Extracts design tokens via Figma REST API, asks clarifying questions,
  then generates production-ready code files.
---

# Figma to Mobile

Convert Figma designs to mobile UI code with interactive clarification.

Supported: Android Compose, Android XML, iOS SwiftUI, iOS UIKit.

## Prerequisites

- `FIGMA_TOKEN` environment variable set (Figma > Settings > Personal Access Tokens)
- Python 3.8+ with `requests` package

## Trigger & Input

This skill activates when a user provides a Figma link.

The user may also include **inline hints** alongside the link, such as:
- Target platform: "Android XML", "Compose", "SwiftUI", "UIKit"
- Layout preferences: "use ConstraintLayout", "prefer StackView"
- Component notes: "the switch is our custom CompactSwitch", "this is a dynamic list"
- Any other context about the design

**If the user provides hints, respect them and skip the corresponding questions.**
For example, if the user says "Android XML, the 3 cards are a RecyclerView list", do NOT ask about output format or whether the cards are dynamic/static.

## Workflow

### Step 1: Fetch & Analyze

When user provides a Figma link:

1. Run `scripts/figma_fetch.py "<url>"` to get design data
2. Analyze the structure: identify sections, repeated patterns, component types
3. Note INSTANCE nodes — they indicate reusable components
4. Note gradient/shadow data — flag for the user if complex

**Figma node interpretation (apply before generating any platform code):**
- **Skip system chrome**: StatusBar, HomeIndicator, NavigationBar are iOS design placeholders — don't generate code for them. Also skip duplicate nodes at the same position (Figma artifacts)
- **Skip invisible nodes**: VECTOR/RECTANGLE with empty fills and all strokes `visible: false`, or `absoluteRenderBounds: null` — these are leftover design artifacts that render nothing
- **Container + icon = single view**: A FRAME (with background/cornerRadius) wrapping a small VECTOR/INSTANCE is one ImageView/Image, not nested layouts
- **VECTOR/ELLIPSE compositions = single asset**: Multiple small VECTOR/ELLIPSE siblings inside a FRAME are pieces of one icon — output as a single image reference, not separate views
- **RECTANGLE as background**: When a GROUP's first child is a RECTANGLE matching the GROUP's dimensions, it's a background shape, not a separate view
- **GROUP vs FRAME**: FRAME with `layoutMode` maps to structured layouts (LinearLayout, HStack, etc.); GROUP without `layoutMode` uses absolute positioning — map to ConstraintLayout constraints or explicit offsets
- **Round Figma decimals**: Round dp to nearest integer, sp to nearest 0.5. Snap near-standard values (e.g., 47.99 → 48dp)
- **Width strategy**: Don't blindly copy Figma width values — infer design intent. Elements spanning near-full screen width → `match_parent` + `marginHorizontal`. In side-by-side layouts, identify the "flexible" element (text/content) vs "fixed" element (icon/avatar) and use `0dp` + constraints for the flexible one. See xml-patterns.md "Width Strategy" for full rules.

**Page architecture analysis (Android XML specific):**
- Multiple tab labels → likely `TabLayout` + `ViewPager2`, content in Fragment layouts (strong signal, not absolute — ask if unsure)
- Tab color differences between items → selected/unselected state, use `tabSelectedTextColor` / `tabTextColor`, not hardcoded per-tab colors
- Navigation bar with back/close icon → `ImageView` (src + background), not FrameLayout wrapper
- Buttons with icon + text → prefer `LinearLayout` + `ImageView` + `TextView` over `MaterialButton` with `app:icon`
- List item with left sidebar + right content → observe multiple items to judge if equal-height or independent
- **Stacked/overlapping cards** with similar structure (same shape, offset position) → likely a card-switching interaction (swipe, stack, flip). Do NOT generate as separate static Views. Instead, ask the user: "These cards appear stacked — is this a swipe/switch interaction? If so, what's the switching behavior (left-right swipe, tap to flip, auto-play)?" The implementation (custom View, ViewPager2, third-party CardStackView, etc.) depends on the answer.

### Step 2: Confirm & Clarify

**Question priority (strict order — ask earlier questions first):**

1. **Output format** (MUST ask first unless user already specified)
   → Android XML / Compose / SwiftUI / UIKit
   This determines all subsequent analysis phrasing and code output.

2. **Structural ambiguities** (only ask what you're genuinely unsure about)
   → "These N items look similar — dynamic list or fixed layout?"
   → "This area: single image asset or icon-on-background combo?"

3. **Component choices** (only if platform-relevant)
   → "Any custom components to use? (otherwise I'll use platform defaults)"

**Rules for questions:**
- Skip any question the user already answered via inline hints
- Max 3-5 questions total, fewer is better
- Each question gives concrete options with one-line pros/cons
- Every question includes an open option: "or tell me more about this"
- Use natural language, no JSON or technical dumps
- If everything is clear (user gave full context + simple structure), skip Step 2 entirely

**Confidence guide — when to ask vs. when to just generate:**
- ≥3 sibling nodes with similar structure → likely a list → ASK (dynamic vs static)
- INSTANCE nodes sharing same componentId → reusable component → MENTION but can default
- Single clear hierarchy, no ambiguity → high confidence → SKIP questions, go to Step 3
- Gradient/complex shadow in design → MENTION in summary ("I see a gradient here, I'll approximate it as X")

### Step 3: Generate Code

After user confirms (or if no questions needed), generate code files.

**Output rules (absolute — never break these):**
- **Colors**: Before hardcoding, search `res/values/colors.xml` (and `res/values/colors_*.xml` if present) for a matching hex value. If found, use the resource reference (e.g. `@color/primary`). If not found, write hex directly (`android:textColor="#0F0F0F"` / `Color(0xFF0F0F0F)`).
- **Strings**: Before hardcoding, search `res/values/strings.xml` for matching text content. If found, use the resource reference (e.g. `@string/notification_settings`). If not found, write text directly (`android:text="通知设置"`).
- **Dimensions**: write values directly (`android:textSize="17sp"`). Dimension resources are rarely worth matching.
- **Lists**: output main layout + separate item layout file. Do NOT generate Adapter/ViewHolder.
- **Resource matching priority**: Use project-defined `@color/` and `@string/` when an exact match exists. Hardcode everything else for instant preview. Never create new resource definitions — only reference existing ones.

**Drawable resources — generate, don't placeholder:**
- **Shape drawables** (backgrounds, outlines, tracks): Generate the actual XML shape drawable code based on Figma data (color, cornerRadius, stroke, gradient). Output each as a separate file with `📄 drawable/filename.xml` header.
- **Icons/vectors**: Use `figma_fetch.py --export-svg <node-ids>` to export SVG from Figma API, then convert to Android Vector Drawable XML. The simplified JSON includes an `"id"` field on every node — use these IDs for export. Output each as `📄 drawable/ic_name.xml`.
- **Photos/bitmaps**: These cannot be generated — use `@drawable/placeholder` and note what image is needed.
- **Goal**: The generated code should be copy-pasteable and immediately render a close approximation of the design, not a blank screen with placeholders.

**Platform guidelines (the agent already knows these — this is a reminder to follow them strictly):**
- **Android XML**: Material Design 3. ConstraintLayout as default for any non-trivial layout. 8dp grid. Min touch target 48dp. MaterialCardView/MaterialSwitch over legacy.
- **Android Compose**: Material3 composables. Modifier chains. LazyColumn for lists. Scaffold for pages.
- **iOS SwiftUI**: Apple HIG. NavigationStack, List, VStack/HStack/ZStack. Safe areas. System fonts.
- **iOS UIKit**: Apple HIG. AutoLayout (NSLayoutConstraint or StackView). UITableView/UICollectionView for lists. Safe areas.

**Handling special visual properties:**
- **Gradients**: generate platform-appropriate gradient code (GradientDrawable / Brush.linearGradient / LinearGradient / CAGradientLayer). If gradient is complex, add a comment noting it may need visual tuning.
- **Shadows**: use platform shadow APIs. Note if the design shadow differs from default elevation shadow.
- **Per-corner radius**: use platform-specific per-corner APIs when radii differ.

Read platform-specific mapping details from:
- Android Compose → references/compose-patterns.md
- Android XML → references/xml-patterns.md
- iOS SwiftUI → references/swiftui-patterns.md
- iOS UIKit → references/uikit-patterns.md

If multiple files are needed, output each with a clear filename header:
```
📄 activity_notification_settings.xml
[code]

📄 item_expert_notification.xml
[code]
```

### Step 4: Iterate

After showing code, ask briefly:
> Matches the design? Any adjustments?

**The user can then give feedback to refine the output.** Common iterations:
- "间距大了" → adjust specific spacing
- "Switch 换成我们的 CustomSwitch" → swap component
- "把标题栏去掉" → remove section
- "换成 Compose 版本" → regenerate in different format
- "颜色不对，这里应该是 #333333" → fix specific values

Continue iterating until the user is satisfied. Each round only regenerates the changed parts, not the entire file (unless the user asks for full regeneration).

## Error Handling

- **FIGMA_TOKEN not set** (script outputs `FIGMA_TOKEN_NOT_SET`) → do NOT ask user to run commands. Instead:
  1. Tell the user you need a Figma Personal Access Token
  2. Tell them where to get it: Figma → avatar (top-left) → Settings → Security → Personal Access Tokens
  3. Ask them to paste the token in chat
  4. Once they provide it (starts with `figd_`), write it to the project root `.env` file: `echo 'FIGMA_TOKEN=figd_xxx' >> .env`
  5. Retry the figma_fetch command — it will read from `.env` automatically
- **FIGMA_TOKEN invalid** (API returns 403/401) → token may have expired or been revoked. Ask user to regenerate and paste new token. Update `.env` file.
- **Invalid URL** → show valid URL example: `https://www.figma.com/design/<fileKey>/<name>?node-id=<id>`
- **API error** → show error message, suggest checking network/proxy
- **Node too large (>200 children)** → suggest selecting a smaller frame
- **Depth auto-increased** → the script auto-retries with deeper depth if it detects truncated children. Inform user if this happens ("I needed to fetch deeper to get all details").
