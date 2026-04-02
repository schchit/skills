# Compose Patterns — Figma to Jetpack Compose Mapping

> Purpose: Map Figma properties to Jetpack Compose code.
> This is a **mapping reference**, not a Compose tutorial — the agent already knows Compose conventions.

## Layout Selection Guide

| Figma Structure | Recommended Composable |
|---|---|
| Vertical stack | Column |
| Horizontal stack | Row |
| Overlapping / z-stacking | Box |
| Repeating similar items (≥3) | LazyColumn / LazyRow |
| Page structure with top/bottom bars | Scaffold |
| Complex relative positioning | Box with Modifier.align / offset |

## Auto-layout Mapping

| Figma Property | Compose Equivalent |
|---|---|
| layoutMode: VERTICAL | Column |
| layoutMode: HORIZONTAL | Row |
| itemSpacing | Arrangement.spacedBy(X.dp) |
| padding* | Modifier.padding() |
| primaryAxisAlignItems: CENTER | verticalArrangement = Arrangement.Center |
| counterAxisAlignItems: CENTER | horizontalAlignment = Alignment.CenterHorizontally |
| layoutGrow: 1 | Modifier.weight(1f) |
| primaryAxisSizingMode: FIXED | Modifier.height/width(X.dp) |
| counterAxisSizingMode: AUTO | wrapContentWidth/Height |

## Size Conversion

- Figma px → Compose .dp (1:1)
- Figma font px → Compose .sp (1:1)

## Shadow Mapping

```kotlin
// Elevation shadow
Card(elevation = CardDefaults.cardElevation(defaultElevation = 4.dp))

// Custom shadow (Compose 1.6+)
Modifier.shadow(
    elevation = 4.dp,
    shape = RoundedCornerShape(12.dp),
    ambientColor = Color(0x1A000000),
    spotColor = Color(0x33000000)
)
```

## Gradient Mapping

```kotlin
// Linear gradient
Modifier.background(
    Brush.linearGradient(
        colors = listOf(Color(0xFFFF6B6B), Color(0xFF4ECDC4)),
        start = Offset(0f, 0f),
        end = Offset(0f, Float.POSITIVE_INFINITY)
    )
)
```

## Per-corner Radius

```kotlin
RoundedCornerShape(
    topStart = 12.dp,
    topEnd = 12.dp,
    bottomEnd = 0.dp,
    bottomStart = 0.dp
)
```
