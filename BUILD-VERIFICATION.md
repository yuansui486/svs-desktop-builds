# macOS ARM64 验收记录

日期：2026-10-27。构建输入：`20261027_03`。

- [成功的 GitHub Actions 构建](https://github.com/yuansui486/svs-desktop-builds/actions/runs/40445233526)，耗时 21 分 24 秒。
- [正式下载 Release](https://github.com/yuansui486/svs-desktop-builds/releases/tag/macos-20261027_03)。
- 构建环境：GitHub `macos-15` ARM64，Node.js 22.14.0，Rust stable。

## 验证结果

1. 加密源码在本地和 Actions 均成功验证、还原；本地检查全部 1034 个快照文件一致，Cargo metadata 检查通过。传输边界测试覆盖篡改密文拒绝、路径越界拒绝及运行数据排除。
2. macOS 原生编译 GUI 和四套技能 runner，并完成实际 ZIP 打包。
3. 使用系统 `ditto` 解压正式 ZIP 后，完整运行资源摘要、GUI launcher、四套技能入口检查通过。
4. 四技能认证 mock 覆盖缺少登录、取消、过期、权限不足、网络失败、伪造授权、共享与显式 token。
5. 实际渲染通过：HyperFrames/GSAP 两帧视频、数字人媒体编码与探测、Remotion H.264、横竖屏字幕组件的字体/图片/音效/任务素材、PPT SpecProject + ImageSlide。
6. 完整应用移动到含空格的新目录后，预检和 GUI launcher 检查通过。
7. 创建 DMG、生成 SHA256，发布文件摘要与 GitHub Release API 返回的 SHA256 一致。

## 成品

| 文件 | 字节 | SHA256 |
| --- | ---: | --- |
| `svs-app-mac-arm64-offline.zip` | 940213635 | `21eca766981e698833579ab9190ddf17b67ef721742818a19ab4186a4d96281e` |
| `svs-app-mac-arm64.dmg` | 1045481870 | `7c0932542f1d3346937c8965a4921253d2239bf7172815edc174d13bde9515ee` |

## 验收边界

本次为完整资源版，要求系统 Node.js 22+；无限画布当前仅支持 Windows。测试使用本地素材和模拟认证，未调用真实付费云端生成服务，也未覆盖用户在实际 Mac 桌面上的全部交互。没有 Apple Developer 证书签名或公证。DMG 内需移动整个“SVS 新媒体后台”目录，不能单独移动 launcher .app。Intel Mac 不属于本次交付平台。
