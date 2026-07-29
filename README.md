# Android Wallpaper Content

Public staging content for `jzh000119/android-wallpaper-app`.

- Runtime catalog: `content/v1/releases/2026-07-30.2/release.json`
- Runtime channel configuration pointer: `content/v1/channels/current.json`
- Reviewed sources: The Metropolitan Museum of Art Open Access and six project-original,
  AI-assisted development assets
- Rights gate: The Met items must remain verified public-domain/CC0 records; project-original AI
  items must retain their generation-terms record, visible AI label, human review, exact asset
  hash, non-exclusive/non-absolute-clearance wording, and takedown state
- Production boundary: this GitHub Pages repository is for development acceptance only; the Android release must use the domestic COS/CDN configuration

`2026-07-30.2` contains 26 reviewed static wallpapers: 20 The Met Open Access items and six
project-original AI-assisted items. The six project-original files are byte-identical to the
WebP assets already bundled in the Android Debug APK. The same exact object is used for thumbnail
and original, avoiding another lossy encoding. The Android sync selector recognizes their six
canonical content IDs and does not prefetch these duplicate 1,261,962 bytes (about 1.20 MiB);
the APK-bundled originals remain the runtime cards.

The AI entries record OpenAI service/output terms plus project review; they are not CC0, public
domain, exclusive rights, absolute clearance, or proof that third-party rights cannot exist.
Their source landing URL documents the generation service rather than serving as a public work
page. A real complaint contact, production rights page, target-jurisdiction review, reverse-image
search, store compliance, and production CDN remain release gates.

The mixed-source release is built from the reviewed record in the app repository; it is not
assembled by manually editing `release.json`. Run it from a Python environment installed from
the app repository's `backend/pyproject.toml`, because the publisher fully decodes each WebP with
Pillow:

```text
python3 ../android-wallpaper-app/tools/catalog/build_vc01_release_extension.py \
  --base-release content/v1/releases/2026-07-30.1/release.json \
  --review ../android-wallpaper-app/content/reviews/vc01-controlled-review-2026-07-30.2.json \
  --asset-root ../android-wallpaper-app/app/src/main/assets \
  --release-id 2026-07-30.2 \
  --asset-base-url https://jzh000119.github.io/android-wallpaper-content/content/v1/releases/2026-07-30.2/assets/ \
  --output content/v1/releases/2026-07-30.2 \
  --published-at 1785356253000
```

The release also reuses the signed, self-authored parameter-only dynamic fixture first published
in `2026-07-20.3`. Its
`.lwp` package is signed with the development key whose public-key SHA-256 fingerprint is
`d9ab0e13f3d39caf8ee30dcaf550a98925041c3cddd58227758a6788e000ec8c`.
The signed manifest binds the scene bytes and the fallback-image SHA-256, so an asset replacement
cannot be accepted by the Android runtime while retaining the old signature.
The private key is intentionally outside this repository. Production must use a separately
protected signing process and a production key rotation plan.

Published assets are immutable and named by SHA-256. Do not replace files inside an existing
release ID.

## Channel configuration

Channel configuration is a separate endpoint, rather than an additive field in a catalog release.
This preserves compatibility with Android clients that intentionally parse `release.json`
strictly: those older clients do not fetch this endpoint, while newer clients can use the
configuration for channel labels, filters, sorting, layout, and visibility. Each versioned file
is immutable; `content/v1/channels/current.json` is the intentionally mutable pointer that lets
newer clients discover a later reviewed configuration without an APK update.

Build a new configuration from a reviewed input file with:

```text
python3 tools/build_channel_config.py \
  --input tools/channel-config/2026-07-20.1.json \
  --config-id 2026-07-20.1 \
  --output content/v1/channels/2026-07-20.1/channel-config.json \
  --current-output content/v1/channels/current.json
```

The publisher refuses to overwrite an existing output. Run its contract tests before a release:

```text
python3 -m unittest tools/test_build_channel_config.py
```

When updating `current.json`, the publisher requires both a new `configId` and a strictly newer
`publishedAtEpochMillis`; it refuses to publish the immutable output if the mutable pointer would
move backward or rewrite the same ID.
