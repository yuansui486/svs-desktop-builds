# SVS Desktop Builds

SVS 新媒体后台的 macOS Apple Silicon 构建与下载仓库。

本仓库公开构建流程及通过验证的成品。业务源码和私有依赖通过 AES-256-GCM 加密快照提供给 GitHub Actions，解密密钥仅保存在对应构建的 Actions Secret 中；这里不是业务源码的开源镜像。

## 下载与使用

从 Releases 下载 macOS ARM64 的 ZIP 或 DMG，适用于 Apple Silicon Mac。打开 DMG，将唯一的 `新媒体后台.app` 拖到 Applications 即可。ZIP 解压后同样只有一个完整 `.app`，可直接移动到应用程序目录。运行数据及共享工具保存在用户的 `~/Library/Application Support/SVS/`，替换 `.app` 更新会保留数据。旧文件夹版数据请保留原目录，暂不自动迁移。

macOS 与 Windows 均支持登录后从国内镜像自动下载共享运行资源，无需单独安装 Node.js；登录和云端 AI 服务需要联网。本次发布没有 Apple Developer 签名及公证，首次打开可能需要在系统“隐私与安全性”中确认允许。提供 lite 精简版及 offline 预置资源版，设置中可查看下载进度和检查并修复。

macOS 支持无限画布、邮箱绑定及会话恢复、设置入口隐藏、无边框浮动窗口控制和系统钥匙串保护的记住密码。

## 维护者构建

1. 从开发仓库运行 `packaging/macos/source_bundle.py` 生成、校验并上传构建输入。每个快照使用独立 Secret，不包含 Git 历史、运行数据或开发机凭据。
2. 手动触发 `Build macOS ARM64`，提供对应 `build_id`。
3. 工作流在 `macos-15` ARM64 环境中解密快照、准备平台依赖、构建并验证解压后的程序。
4. 只有验证成功后才发布 `macos-<build_id>` Release、ZIP、DMG 和 SHA256。

`source-*` prerelease 只包含加密构建输入，不是用户安装包。工作流不接受 PR 触发，不向第三方 PR 提供构建密钥，不缓存解密后的业务源码。
