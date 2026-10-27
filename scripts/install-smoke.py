"""Install the released DMG as a user would and launch its real login window."""
import json
import os
from pathlib import Path
import plistlib
import subprocess
import sys
import tempfile

dmg = Path(sys.argv[1]).resolve()
work = Path(tempfile.mkdtemp(prefix='svs-drag-install-')).resolve()
mount = work / 'mounted'
support = Path.home() / 'Library/Application Support/SVS'
assert not support.exists(), 'This smoke test requires a fresh macOS runner'
subprocess.run(['hdiutil', 'attach', str(dmg), '-mountpoint', str(mount), '-nobrowse', '-readonly'], check=True)
app = work / 'Applications/新媒体后台.app'
try:
    visible = {p.name for p in mount.iterdir() if not p.name.startswith('.')}
    assert visible == {'新媒体后台.app', 'Applications'}, visible
    assert (mount / 'Applications').is_symlink()
    assert os.readlink(mount / 'Applications') == '/Applications'
    info = plistlib.loads((mount / '新媒体后台.app/Contents/Info.plist').read_bytes())
    assert info['CFBundlePackageType'] == 'APPL'
    assert info['CFBundleExecutable'] == 'launch'
    app.parent.mkdir()
    subprocess.run(['ditto', str(mount / '新媒体后台.app'), str(app)], check=True)
finally:
    subprocess.run(['hdiutil', 'detach', str(mount)], check=True)

subprocess.run(['codesign', '--verify', '--deep', '--strict', str(app)], check=True)
swift = work / 'launch.swift'
swift.write_text(r'''
import AppKit
import CoreGraphics
import Foundation
let url = URL(fileURLWithPath: CommandLine.arguments[1])
let screenshot = CommandLine.arguments[2]
var launched: NSRunningApplication? = nil
var succeeded = false
let config = NSWorkspace.OpenConfiguration()
config.activates = true
config.createsNewApplicationInstance = true
NSWorkspace.shared.openApplication(at: url, configuration: config) { app, error in
    if let error = error { fputs("Launch failed: \(error)\n", stderr); exit(1) }
    launched = app
}
let deadline = Date().addingTimeInterval(120)
let timer = Timer.scheduledTimer(withTimeInterval: 1, repeats: true) { _ in
    if succeeded { return }
    guard let app = launched else {
        if Date() > deadline { fputs("LaunchServices timed out\n", stderr); exit(1) }
        return
    }
    if app.isTerminated { fputs("Application exited before showing a window\n", stderr); exit(1) }
    let windows = CGWindowListCopyWindowInfo([.optionOnScreenOnly, .excludeDesktopElements], kCGNullWindowID) as? [[String: Any]] ?? []
    for window in windows {
        let pid = (window[kCGWindowOwnerPID as String] as? NSNumber)?.int32Value
        let layer = (window[kCGWindowLayer as String] as? NSNumber)?.intValue
        let bounds = window[kCGWindowBounds as String] as? [String: CGFloat] ?? [:]
        if pid == app.processIdentifier && layer == 0 && (bounds["Width"] ?? 0) >= 500 && (bounds["Height"] ?? 0) >= 300 {
            print("PASS: LaunchServices opened the installed app, visible window PID \(app.processIdentifier), bounds \(bounds)")
            succeeded = true
            DispatchQueue.main.asyncAfter(deadline: .now() + 3) {
                let capture = Process()
                capture.executableURL = URL(fileURLWithPath: "/usr/sbin/screencapture")
                capture.arguments = ["-x", screenshot]
                try? capture.run(); capture.waitUntilExit()
                app.terminate()
                DispatchQueue.main.asyncAfter(deadline: .now() + 2) { if !app.isTerminated { app.forceTerminate() }; exit(0) }
            }
            return
        }
    }
    if Date() > deadline { app.forceTerminate(); fputs("No visible application window within 120 seconds\n", stderr); exit(1) }
}
RunLoop.main.run()
''', encoding='utf-8')
evidence = Path(os.environ['RUNNER_TEMP']) / 'install-evidence'
evidence.mkdir(exist_ok=True)
subprocess.run(['swift', str(swift), str(app), str(evidence / 'installed-app.png')], check=True, timeout=240)
installations = [p for p in (support / 'installations').iterdir() if not p.name.startswith('.')]
assert len(installations) == 1
installed = installations[0]
assert (installed / '.svs-managed').read_text() == installed.name
assert (installed / 'drafts').resolve() == support / 'data/drafts'
assert (installed / 'runtime/dependencies').resolve() == support / 'data/runtime/dependencies'
assert list(app.parent.iterdir()) == [app], 'Installed app must have no external sibling payload'
subprocess.run(['codesign', '--verify', '--deep', '--strict', str(app)], check=True)
(evidence / 'result.json').write_text(json.dumps({'status': 'passed', 'bundle': info['CFBundleIdentifier'], 'visible_window': True, 'bundle_signature_unchanged': True}, indent=2))
print('PASS: drag-install single app, eject DMG, launch real login window, stable data, app seal unchanged')
