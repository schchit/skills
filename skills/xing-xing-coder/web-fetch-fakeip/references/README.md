# web_fetch Fake-IP Workaround

Minimal reference for the npm global install workaround.

## Use it when

- OpenClaw was installed with `npm install -g openclaw`
- Clash, Mihomo, or Surge fake-ip is enabled
- `web_fetch` is blocked as a private/internal/special-use IP

## What it does

It inserts:

```js
policy: { allowRfc2544BenchmarkRange: true }, // openclaw-fakeip-patch
```

into the bundled `web_fetch` runtime.

## Limits

- npm global installs only
- not for source builds
- does not fix cert, proxy, or env issues
- temporary workaround, not an official fix

## Quick flow

```bash
bash patch-openclaw-global-fakeip.sh status
bash patch-openclaw-global-fakeip.sh inspect
bash patch-openclaw-global-fakeip.sh apply
openclaw gateway restart
```

## Undo

```bash
bash patch-openclaw-global-fakeip.sh revert
openclaw gateway restart
```

## Script source

The bundled shell script is adapted from the original repository here:

- <https://github.com/xing-xing-coder/OpenClaw-web_fetch-Fake-IP-Workaround>
