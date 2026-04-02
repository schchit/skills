# UIKit Patterns — Figma to UIKit Mapping

> Purpose: Map Figma properties to UIKit code.
> This is a **mapping reference**, not a UIKit tutorial — the agent already knows UIKit conventions.

## Layout Selection Guide

| Figma Structure | Recommended Approach |
|---|---|
| Simple vertical/horizontal stack | UIStackView |
| Complex / relative positioning | Auto Layout (NSLayoutConstraint) |
| Repeating similar items (≥3) | UITableView / UICollectionView |
| Scrollable content | UIScrollView |

## Auto-layout Mapping

| Figma Property | UIKit Equivalent |
|---|---|
| layoutMode: VERTICAL | UIStackView axis=.vertical |
| layoutMode: HORIZONTAL | UIStackView axis=.horizontal |
| itemSpacing | stackView.spacing |
| padding | layoutMargins + isLayoutMarginsRelativeArrangement |
| primaryAxisAlignItems: CENTER | distribution = .equalCentering |
| counterAxisAlignItems: CENTER | alignment = .center |
| layoutGrow: 1 | setContentHuggingPriority(.defaultLow) |
| primaryAxisSizingMode: FIXED | heightAnchor/widthAnchor constraint |

## Size Conversion

- Figma px → UIKit pt (1:1)
- Font sizes: .systemFont(ofSize:) with pt values

## Color Hex Extension (include once in generated code)

```swift
extension UIColor {
    convenience init(hex: String) {
        let scanner = Scanner(string: hex)
        var rgb: UInt64 = 0
        scanner.scanHexInt64(&rgb)
        self.init(
            red: CGFloat((rgb >> 16) & 0xFF) / 255.0,
            green: CGFloat((rgb >> 8) & 0xFF) / 255.0,
            blue: CGFloat(rgb & 0xFF) / 255.0,
            alpha: 1.0
        )
    }
}
```

## Layout Approach

1. Set `translatesAutoresizingMaskIntoConstraints = false`
2. Use `NSLayoutConstraint.activate([])`
3. Prefer UIStackView for linear layouts (reduces constraint count)
4. Use direct constraints for complex/absolute positioning

## Shadow Mapping

```swift
view.layer.shadowColor = UIColor(hex: "000000").cgColor
view.layer.shadowOpacity = 0.1
view.layer.shadowRadius = 4
view.layer.shadowOffset = CGSize(width: 0, height: 2)
```

## Gradient Mapping

```swift
let gradientLayer = CAGradientLayer()
gradientLayer.colors = [UIColor(hex: "FF6B6B").cgColor, UIColor(hex: "4ECDC4").cgColor]
gradientLayer.startPoint = CGPoint(x: 0.5, y: 0)
gradientLayer.endPoint = CGPoint(x: 0.5, y: 1)
gradientLayer.frame = view.bounds
view.layer.insertSublayer(gradientLayer, at: 0)
```

## Per-corner Radius

```swift
view.layer.cornerRadius = 12
view.layer.maskedCorners = [.layerMinXMinYCorner, .layerMaxXMinYCorner]  // top only
```
