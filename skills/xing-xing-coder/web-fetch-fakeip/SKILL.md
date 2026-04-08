---
name: web-fetch-fakeip
description: Temporary workaround for web_fetch failures caused by SSRF blocking under Clash, Mihomo, or Surge fake-ip mode on npm global installs. Use when web_fetch reports private or internal IP blocking and you need a reversible patch without editing config or rebuilding from source.
---

# web_fetch Fake-IP Workaround

Apply a small, reversible patch so `web_fetch` works under TUN + fake-ip environments that resolve through `198.18.0.0/15`.

## Best fit

Use this skill when:

- OpenClaw was installed with `npm install -g openclaw`
- You use Clash, Mihomo, or Surge with fake-ip enabled
- `web_fetch` fails with private/internal/special-use IP blocking
- You want a quick workaround before an upstream fix lands

## Not for

- Source-built OpenClaw
- Certificate problems
- Proxy rule or port mistakes
- Missing proxy environment variables

## What changes

The script finds the bundled `web_fetch` call to `fetchWithWebToolsNetworkGuard({...})` and inserts:

```js
policy: { allowRfc2544BenchmarkRange: true }, // openclaw-fakeip-patch
```

This only opens the RFC2544 benchmark range used by common fake-ip setups.

## Workflow

```bash
bash patch-openclaw-global-fakeip.sh status
bash patch-openclaw-global-fakeip.sh inspect
bash patch-openclaw-global-fakeip.sh apply
openclaw gateway restart
```

Then retry the failing `web_fetch` request.

## Revert

```bash
bash patch-openclaw-global-fakeip.sh revert
openclaw gateway restart
```

## Notes

- Safe to run repeatedly
- Creates backup files on apply/revert
- After OpenClaw upgrades, rerun if needed

## Resources

- `scripts/patch-openclaw-global-fakeip.sh`
- `references/README.md`
