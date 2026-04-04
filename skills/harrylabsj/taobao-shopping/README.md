# Taobao Shopping

Taobao station-native shopping decision skill.

This skill is for users who want help shopping on Taobao itself:
- choosing between many similar listings
- judging whether a seller looks reliable
- spotting vague variants and suspicious low prices
- deciding whether to buy now, compare more, or avoid

It is intentionally different from `taobao-competitor-analyzer`.

## Use This For

- `帮我看这个淘宝商品靠不靠谱`
- `淘宝同款太多了怎么选`
- `这家淘宝店能买吗`
- `帮我筛几个淘宝候选商品`
- `淘宝买这个值不值`

## Do Not Use This For

- JD / PDD / Vipshop cross-platform price checks
- same-item comparison across marketplaces
- deciding whether to switch away from Taobao

Use `taobao-competitor-analyzer` for those.

## What It Does

- evaluates Taobao listings using visible browser evidence
- compares 2-5 candidate listings inside Taobao
- checks seller and store quality signals
- reviews variant clarity and pricing plausibility
- returns a direct recommendation instead of generic browsing notes

## Output Style

The skill is optimized to return:
- a recommendation action
- the strongest candidate listing
- key risk points
- what to compare next if the user should keep browsing
