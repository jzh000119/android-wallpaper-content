# Android Wallpaper Content

Public staging content for `jzh000119/android-wallpaper-app`.

- Runtime catalog: `content/v1/releases/2026-07-30.2/release.json`
- Runtime channel configuration pointer: `content/v1/channels/current.json` (`2026-07-30.3`)
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

当前不可变配置位于
`content/v1/channels/2026-07-30.3/channel-config.json`，其 `current.json` 指针逐字节相同：

```text
config bytes = 1,273
config SHA-256 =
6126ff406089700f8f1296b9a2c765232e7f275c61bc5b6be1b86a137fb4943d
catalog release = 2026-07-30.2
catalog SHA-256 =
9a008233650cf5a5d67b7a3d53c50505e515ed8ed26a07fca92e89458b7d8eca
public matches = anime 6 / oriental 21 / landscape 14 / birds-and-flowers 5 / night 3
```

新版发布必须从应用仓根目录调用冻结的跨端发布器，而不是使用此仓历史
`tools/build_channel_config.py`。后者不具备 UTF-16、signed `Long` 和完整 wire 边界的等价
验证，不能用于新的受审配置。

```text
cd ../android-wallpaper-app
python3 -m tools.catalog.publish_channel_config \
  --input ../android-wallpaper-content/tools/channel-config/2026-07-30.3.json \
  --content-root ../android-wallpaper-content \
  --catalog ../android-wallpaper-content/content/v1/releases/2026-07-30.2/release.json \
  --projection-review content/reviews/vc09c-channel-projection-2026-07-30.3.json \
  --expected-catalog-release-id 2026-07-30.2 \
  --expected-catalog-sha256 9a008233650cf5a5d67b7a3d53c50505e515ed8ed26a07fca92e89458b7d8eca \
  --expected-public-channel-count anime=6 \
  --expected-public-channel-count oriental=21 \
  --expected-public-channel-count landscape=14 \
  --expected-public-channel-count birds-and-flowers=5 \
  --expected-public-channel-count night=3 \
  --output ../android-wallpaper-content/content/v1/channels/2026-07-30.3/channel-config.json \
  --current-output ../android-wallpaper-content/content/v1/channels/current.json
```

发布器会严格解析不可信 ChannelConfig 和 CatalogRelease raw JSON，拒绝非法 UTF-8/BOM、重复键、
NaN/Infinity、超过 64 层、越界整数和孤立 surrogate；只接受精确映射到受控 content checkout 的
`content/v1/releases/<releaseId>/release.json`、
`content/v1/channels/<configId>/channel-config.json` 与 `channels/current.json`，并拒绝受控内容树中的
软链接。`content-root` 本身和其下 `content/v1/channels`、`content/v1/releases` 都按段
检查；release 目录、catalog 最终文件与已存在 config 目录出现软链接、非目录或非普通文件均失败。每个
public 频道都必须在当前 API 36 eligible static 目录中命中，`any/all`
严格区分大小写，且审定 release ID、raw SHA-256、每频道匹配数和 `catalogOrder` ID 序列必须一致。
`--projection-review` 是独立受审输入，固定 config/catalog 的 raw SHA 与每个 public 频道完整的有序
content ID；发布器先逐项比对它，再允许任何输出写入，不会从同一 config/catalog 的运行时重算结果中自证。

immutable 文件通过 macOS/Linux atomic no-replace rename 写入，随后才替换可变指针。该开发发布器
的信任边界仍是单个可信本地发布者：锁和二次 pointer 检查保护协作调用，不宣称能够抵抗恶意本机
进程、共享对象存储并发或生产发布攻击。若进程在 immutable 写入后、pointer 替换前崩溃，重试只会接管
regular、单硬链接且 SHA-256 与候选逐字节相同的孤儿 immutable 文件；不同内容或不安全文件类型绝不
删除、覆盖或接管。`channels/.channel-config-publish.lock` 是被 `.gitignore` 精确忽略的 persistent
regular/单硬链接 advisory `fcntl.flock` 锁：未持锁的残留文件可以复用，进程被终止后内核自动释放锁，
不以旧文件阻断 orphan 恢复；不支持 `fcntl` 时发布器 fail closed。GitHub Pages 仍仅是 development
staging。

运行发布器自身离线回归：

```text
python3 -m unittest tools.catalog.test_publish_channel_config
```
