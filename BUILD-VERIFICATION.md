# macOS 功能对齐验收

日期：2026-10-27；构建输入 `20261027_04`，替代旧的完整资源版 `20261027_03`。

- [成功构建与完整日志](https://github.com/yuansui486/svs-desktop-builds/actions/runs/40455489117)
- [正式下载](https://github.com/yuansui486/svs-desktop-builds/releases/tag/macos-20261027_04)

## 已实现

macOS ARM64 与 Windows 使用相同的后台资源管理器：登录后从固定国内镜像自动下载 Node、Chrome、FFmpeg/FFprobe、Remotion 和 HyperFrames，各技能共用工具，无需安装系统 Node；提供 lite/offline、进度、重试、完整校验及修复。Mac 无限画布复用绑定、会话恢复、首页拦截、设置入口隐藏和浮动窗口控制；WKWebView 使用独立非持久会话。记住密码使用 Keychain 保护的 AES-256-GCM 密钥，文件中仅保存密文。

## 实际验证

在 GitHub macos-15 ARM64 环境完成：

- skill-core 29 项、skill-packager 11 项测试，包括归档权限、真实符号链接、链接逃逸、损坏/缺失检测及续传。
- 正式压缩包解压后完整预检，四技能认证 mock 和入口检查。
- 无系统 Node 路径下实际渲染 HyperFrames、数字人媒体、口播横竖屏字体/图片/音效/字幕组件，以及 PPT SpecProject + ImageSlide。
- 精简版从空缓存经国内镜像安装全部模块并完成预检；破坏 FFmpeg 后断网从已验证缓存修复。
- 带空格目录迁移后预检和 launcher 运行通过。
- macOS Keychain 凭据保存、恢复、账号隔离、损坏拒绝与清除测试通过。
- 3 项画布 Rust 测试及 17 项 WebKit 网页导航、身份校验、账号入口隐藏、重载测试通过。
- 真实 WKWebView 子窗口测试通过：会话注入、网页显示、隐藏账号操作、无边框、三个悬浮控件、最小化/恢复/最大化、窗口激活、首页导航阻断与遮罩。
- DMG 创建、正式发布完成，Release 文件 SHA256 与 GitHub API 摘要一致。

## 文件

| 文件 | 字节 | SHA256 |
| --- | ---: | --- |
| svs-app-mac-arm64-lite.zip | 439981191 | b0c61f00250125391ba7b694c99f58605ddb25fd227d887523e14faa64f2bcac |
| svs-app-mac-arm64-offline.zip | 816442093 | c538e7185d79764b3dbe6b86337b811ffea84b9d586adb587bc26ad770e1b92f |
| svs-app-mac-arm64.dmg | 465084517 | 389722e6f9488d3798992fba5aa9d70b6b554924a8a509c38aefe28956eda701 |

精简 ZIP 相对上一版 940213635 字节缩小约 53.2%；DMG 采用精简版。下载后依赖仍会占用磁盘。

## 验收边界

仅支持 Apple Silicon。没有 Apple Developer 签名或公证。DMG 需复制整个程序目录后运行。原生画布和认证测试使用本地模拟站点/账号，未使用真实验证码完成线上绑定，也未调用真实付费云端服务；测试通过不等于覆盖所有线上操作或用户机器环境。主界面其余业务沿用共同实现，未逐项重跑全部真实账号流程。
