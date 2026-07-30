# Android Wallpaper Content

Public staging content for `jzh000119/android-wallpaper-app`.

- 运行时目录：`content/v1/releases/2026-07-30.5/release.json`
- 运行时内容：28 个 static 与 3 个 live；末尾两个 VC-09E development 动态条目的静态回退和缩略图
  复用 `.2` 已审核的 AI WebP
- 频道指针：`content/v1/channels/current.json` 仍为 `2026-07-30.3`，本次 catalog 发布不修改它
- 权利闸门：The Met 与 CMA 条目必须保留可核验的 public-domain/CC0 记录；项目原创 AI 条目必须
  保留生成条款记录、可见 AI 标签、人工复核、精确 asset hash、非独占/非绝对清权表述与下架状态
- 生产边界：GitHub Pages 仅用于 development 验收；Android 正式版本必须使用国内 COS/CDN 配置

`2026-07-30.5` 逐项保留 `.4` 的前 29 项：28 项已审核的 static（20 项 The Met Open Access、6 项
项目原创 AI-assisted、2 项 Cleveland Museum of Art Open Access CC0）和 1 项既有 signed live fixture。
仅在末尾追加 `vc09e-cloud-ocean-flow` 与 `vc09e-rain-neon-glimmer` 两项已签名 development live，
故总数为 28 static + 3 live。`.5` 运行时目录只包含 `release.json` 与两个 `.lwp`，不复制历史图片；
新动态的 fallback/thumbnail URL 保持指向 `.2` 的 SHA 命名 WebP。
该 release 的 raw SHA-256 为
`968ca83bbc9e492e8aef09a26aed1f5a87ead7b5eed8206e43f3f763c7ca2396`（48,716 bytes）。

本次 `.4` 发布直接逐字节采用应用仓 `build/catalog/2026-07-30.4` 的受审产物；运行时目录只包含
`release.json` 与这 4 个 WebP，不包含 draft manifest 或旧版本资产。项目原创的 6 个 WebP 仍与
Android Debug APK 中的资源逐字节相同；同步选择器识别其 6 个 canonical content ID，不会预取
重复的 1,261,962 bytes（约 1.20 MiB），APK 内置原图仍是运行时卡片。

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

`.4` 则由应用仓固定证据提交
`3a456a6f50d72b2119712a772dc9c4719d526950` 中的受控、CMA 专用构建器
`tools/catalog/build_cma_vc09d_release.py` 生成：它以 `.2` baseline、冻结的
`cma-vc09d-review-2026-07-30.4.json`、来源快照和经验证的受控 ORIGINAL 为输入，导出
`build/catalog/2026-07-30.4`。内容仓只逐字节发布该受审输出，不手工组装 `.4` release。

`.5` 同样不手工组装 JSON，也不在内容仓生成或签名包。应用仓的受审公开 draft 为
`app/src/test/resources/catalog/catalog-release-2026-07-30.5.json`，两个公开 Base64 fixture 解码后分别是：

```text
ca71e4b56bc2da5e315df33f24688fc5432ceac163f89964fe1b4b9b66db62eb.lwp = 1,037 bytes
f4335246e0689fd787fc161133bc7dd7dbee61683d4c05e6b0ff5e31721bc118.lwp = 1,060 bytes
```

发布只能通过 `tools/publish_vc09e_development_release.py`：它验证 manifest/包的固定 SHA-256 和字节数，
拒绝符号链接、额外包和已存在的 release ID，随后逐字节复制 `release.json` 与两个 `.lwp`。它不接收、
读取或写入私钥，也不改 `channels/current.json`。发布器使用示例（输入为已审核的公开 builder 输出）：

```text
vc09e_tmp=$(mktemp -d)
base64 -D -i ../android-wallpaper-app/contracts/fixtures/vc09e-cloud-ocean-flow-v1.lwp.b64 \
  -o "$vc09e_tmp/ca71e4b56bc2da5e315df33f24688fc5432ceac163f89964fe1b4b9b66db62eb.lwp"
base64 -D -i ../android-wallpaper-app/contracts/fixtures/vc09e-rain-neon-glimmer-v1.lwp.b64 \
  -o "$vc09e_tmp/f4335246e0689fd787fc161133bc7dd7dbee61683d4c05e6b0ff5e31721bc118.lwp"
python3 tools/publish_vc09e_development_release.py \
  --manifest ../android-wallpaper-app/app/src/test/resources/catalog/catalog-release-2026-07-30.5.json \
  --package "$vc09e_tmp/ca71e4b56bc2da5e315df33f24688fc5432ceac163f89964fe1b4b9b66db62eb.lwp" \
  --package "$vc09e_tmp/f4335246e0689fd787fc161133bc7dd7dbee61683d4c05e6b0ff5e31721bc118.lwp"
```

新增动态条目的 `origin` 是 `aiGenerated`，保留各自 AI 回退条目的可见标签、生成元数据、OpenAI 输出条款、
人工复核与下架状态；它们不是 CC0、公共领域、独占权利或绝对清权。其 development 签名公钥 SHA-256
fingerprint 为 `3858c1920c417fbd32b66a5df2eb976f2a006a6548350f95c26e9cc15b5288a3`，仅用于开发验收。

`.5` 仍复用最早在 `2026-07-20.3` 发布的 signed、self-authored parameter-only dynamic fixture。其
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

### `.3 + .2` 原始发布证据

以下 raw config、catalog SHA 和频道计数是 `.3` config 首次随 `.2` catalog 发布时的证据：

```text
config bytes = 1,273
config SHA-256 =
6126ff406089700f8f1296b9a2c765232e7f275c61bc5b6be1b86a137fb4943d
catalog release = 2026-07-30.2
catalog SHA-256 =
9a008233650cf5a5d67b7a3d53c50505e515ed8ed26a07fca92e89458b7d8eca
public matches = anime 6 / oriental 21 / landscape 14 / birds-and-flowers 5 / night 3
```

以下命令是上述 `.3 + .2` 原始发布的可复现记录。真正需要发布新的频道配置时，必须从应用仓根目录
调用冻结的跨端发布器，而不是使用此仓历史
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

### `.3 + .4` 独立投影复核

`.4` 不重发 `.3` config，也不推进 `current.json` 指针。应用仓固定证据提交
`3a456a6f50d72b2119712a772dc9c4719d526950` 中的
`content/reviews/vc09d-channel-projection-2026-07-30.4.json` 独立绑定 `.3` 的 raw config SHA
`6126ff406089700f8f1296b9a2c765232e7f275c61bc5b6be1b86a137fb4943d` 与 `.4` catalog raw SHA
`c865bd4c6701e80d5668a2d060446c766b6aea2f6361570d32f5d3978eb5828b`，并冻结运行时频道计数：
anime 6 / oriental 23 / landscape 16 / birds-and-flowers 5 / night 3。这是独立的 `.3 + .4`
投影复核，不是 config 发布操作。

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

运行内容仓离线回归：

```text
python3 -m unittest tools.test_catalog_release tools.test_build_channel_config
```
