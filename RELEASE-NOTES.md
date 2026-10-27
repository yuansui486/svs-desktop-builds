适用于 Apple Silicon Mac（ARM64），本轮构建环境为 macOS 15。

- ZIP：解压完整目录后打开“新媒体后台.app”。
- DMG：把整个“SVS 新媒体后台”文件夹拖到 Applications，再打开其中的应用入口。
- 需要系统 Node.js 22+；登录和云端服务仍需联网。
- 保留所有运行资源，当前不是 Windows 式自动下载精简版。
- 未使用 Apple Developer 证书签名或公证。

发布前自动验证完整资源摘要、四技能入口及本地最小视频渲染。未在 CI 调用真实付费云端生成服务。
