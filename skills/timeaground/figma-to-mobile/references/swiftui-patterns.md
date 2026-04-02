# SwiftUI Patterns — Figma to SwiftUI Mapping

> Purpose: Map Figma properties to SwiftUI code.
> This is a **mapping reference**, not a SwiftUI tutorial — the agent already knows SwiftUI conventions.

## Layout Selection Guide

| Figma Structure | Recommended View |
|---|---|
| Vertical stack | VStack |
| Horizontal stack | HStack |
| Overlapping / z-stacking | ZStack |
| Repeating similar items (≥3) | List / LazyVStack / LazyHStack |
| Page with navigation bar | NavigationStack + .navigationTitle |
| Scrollable content | ScrollView |

## Auto-layout Mapping

| Figma Property | SwiftUI Equivalent |
|---|---|
| layoutMode: VERTICAL | VStack |
| layoutMode: HORIZONTAL | HStack |
| itemSpacing | spacing: parameter |
| padding* | .padding() modifiers |
| primaryAxisAlignItems: CENTER | alignment parameter + Spacer() |
| counterAxisAlignItems: CENTER | alignment: .center |
| layoutGrow: 1 | .frame(maxWidth: .infinity) or Spacer() |
| primaryAxisSizingMode: FIXED | .frame(height/width: X) |

## Size Conversion

- Figma px → SwiftUI pt (1:1)
- Font sizes: .system(size:) with pt values

## Color Hex Extension (include once in generated code)

```swift
extension Color {
    init(hex: String) {
        let scanner = Scanner(string: hex)
        var rgb: UInt64 = 0
        scanner.scanHexInt64(&rgb)
        self.init(
            red: Double((rgb >> 16) & 0xFF) / 255.0,
            green: Double((rgb >> 8) & 0xFF) / 255.0,
            blue: Double(rgb & 0xFF) / 255.0
        )
    }
}
```

## Shadow Mapping

```swift
.shadow(color: Color(hex: "000000").opacity(0.1), radius: 4, x: 0, y: 2)
```

## Gradient Mapping

```swift
LinearGradient(
    colors: [Color(hex: "FF6B6B"), Color(hex: "4ECDC4")],
    startPoint: .top,
    endPoint: .bottom
)
```

## Per-corner Radius (iOS 16+)

```swift
.clipShape(UnevenRoundedRectangle(
    topLeadingRadius: 12,
    topTrailingRadius: 12,
    bottomLeadingRadius: 0,
    bottomTrailingRadius: 0
))
```
