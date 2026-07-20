# Android Wallpaper Content

Public staging content for `jzh000119/android-wallpaper-app`.

- Runtime catalog: `content/v1/releases/2026-07-20.3/release.json`
- Runtime channel configuration: `content/v1/channels/2026-07-20.1/channel-config.json`
- Source: The Metropolitan Museum of Art Open Access
- Rights gate: every item must be marked public domain and retain its source and license evidence
- Production boundary: this GitHub Pages repository is for development acceptance only; the Android release must use the domestic COS/CDN configuration

`2026-07-20.3` additionally contains one self-authored, parameter-only dynamic fixture. Its
`.lwp` package is signed with the development key whose public-key SHA-256 fingerprint is
`d9ab0e13f3d39caf8ee30dcaf550a98925041c3cddd58227758a6788e000ec8c`.
The signed manifest binds the scene bytes and the fallback-image SHA-256, so an asset replacement
cannot be accepted by the Android runtime while retaining the old signature.
The private key is intentionally outside this repository. Production must use a separately
protected signing process and a production key rotation plan.

Generated assets are immutable and named by SHA-256. Do not replace files inside an existing release ID.

## Channel configuration

Channel configuration is a separate immutable endpoint, rather than an additive field in a catalog
release. This preserves compatibility with Android clients that intentionally parse
`release.json` strictly: those older clients do not fetch this endpoint, while newer clients can
use the configuration for channel labels, filters, sorting, layout, and visibility.

Build a new configuration from a reviewed input file with:

```text
python3 tools/build_channel_config.py \
  --input tools/channel-config/2026-07-20.1.json \
  --config-id 2026-07-20.1 \
  --output content/v1/channels/2026-07-20.1/channel-config.json
```

The publisher refuses to overwrite an existing output. Run its contract tests before a release:

```text
python3 -m unittest tools/test_build_channel_config.py
```
