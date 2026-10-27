# macOS 单应用安装验收

日期：2026-10-27；构建输入 `20261027_05`。

- [应用构建与功能验证](https://github.com/yuansui486/svs-desktop-builds/actions/runs/40462574469)
- [恢复成品上传与再次安装验证](https://github.com/yuansui486/svs-desktop-builds/actions/runs/40465909949)
- [下载单应用安装包](https://github.com/yuansui486/svs-desktop-builds/releases/tag/macos-20261027_05)

## 安装行为

ZIP 仅包含 `新媒体后台.app`。DMG 根只有该应用与 Applications 快捷方式；复制应用、弹出 DMG 后可正常打开登录窗口。应用包只读，用户数据位于 `~/Library/Application Support/SVS/data/`；版本化运行载荷位于同级 installations。替换应用保留账号文件、素材、草稿、任务、偏好、共享工具和缓存。旧版本部署暂保留，防止运行任务和旧路径引用失效，会占用额外磁盘。

## 已完成验证

在 GitHub macos-15 ARM64 环境完成：

- skill-core 31 项、skill-packager 11 项测试；包含并发部署、中断后重试、同版本复用、升级数据保留、载荷损坏拒绝及归档权限。
- 发布 ZIP 顶层唯一 `.app`、原生 Mach-O 启动器、Info.plist、图标及 ad-hoc 包签名校验。
- 单 `.app` 改名移动、从只读磁盘部署成功；运行后包签名保持有效。
- 用系统 LaunchServices 启动复制后的正式应用，检测到 1040×681 可见窗口，并保存实际登录界面截图。
- 不同载荷升级后凭据文件、草稿、memory 保留，工具目录仍指向同一稳定位置。
- 四技能入口、认证 mock 与本地视频渲染通过，覆盖 HyperFrames、数字人媒体、口播横竖屏组件与 PPT。
- 无系统 Node 路径下，精简版从国内镜像空缓存安装全部模块；损坏 FFmpeg 后断网修复成功。
- Keychain 凭据保存恢复、3 项画布 Rust 测试、17 项 WebKit 网页保护测试通过。
- 原生 WKWebView 会话注入、账号操作隐藏、浮动窗口控件、窗口激活及首页拦截通过。

首次构建的路径比较检查因 macOS `/var` 与 `/private/var` 别名失败；规范化测试路径后全部功能与安装测试通过。发布步骤遇到 GitHub integration HTTP 403，使用已有维护者授权建立标签和草稿；恢复工作流只接受原构建指定 SHA 且所有功能/安装步骤成功的成品，在重新生成 DMG 并再次安装验证后上传。未重新编译或修改已验证 ZIP。

## 边界

适用于 Apple Silicon Mac、macOS 14 及以上。应用使用 ad-hoc 签名，没有 Apple Developer 签名及公证。旧文件夹版数据暂不自动迁移，请保留旧目录。原生画布与认证测试使用本地模拟账号/站点，未调用真实付费云端生成，也未逐项重跑真实账号的全部业务流程。

## 成品摘要

Release 的 GitHub SHA256 与发布校验文件逐项一致。

| 文件 | 字节 | SHA256 |
| --- | ---: | --- |
| svs-app-mac-arm64-lite.zip | 439788630 | 991ae19ae4a2dcbd14b76f5ba240a7fc4220eb19fcdb1d93d11f76c2110d14c8 |
| svs-app-mac-arm64-offline.zip | 808198371 | cebee5c7822306bdb591a74d080479f12ce629a4a6676bbf1b3a3eec2623fb82 |
| svs-app-mac-arm64.dmg | 441752517 | 8e29bebea975a7d961ab720ffd66265ac4d655bd667d05515e3bc1ddd5353bbc |
