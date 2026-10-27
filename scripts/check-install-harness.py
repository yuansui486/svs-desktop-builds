"""Check the window-observation harness independently of the lengthy product build."""
import ast
from pathlib import Path
import plistlib
import subprocess
import tempfile

work = Path(tempfile.mkdtemp(prefix='svs-harness-')).resolve()
tree = ast.parse(Path(__file__).with_name('install-smoke.py').read_text())
code = next(n.value for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, str) and 'import AppKit' in n.value)
helper = work / 'observe.swift'
helper.write_text(code)
subprocess.run(['swiftc', '-typecheck', str(helper)], check=True)
fixture = work / 'Fixture.app'
contents = fixture / 'Contents'
(contents / 'MacOS').mkdir(parents=True)
(contents / 'Info.plist').write_bytes(plistlib.dumps({'CFBundleExecutable': 'fixture', 'CFBundleIdentifier': 'com.onecolleague.svs.install-fixture', 'CFBundleName': 'Install Fixture', 'CFBundlePackageType': 'APPL'}))
source = work / 'fixture.swift'
source.write_text('''import AppKit
let app = NSApplication.shared
app.setActivationPolicy(.regular)
let window = NSWindow(contentRect: NSRect(x: 50, y: 50, width: 700, height: 500), styleMask: [.titled, .closable], backing: .buffered, defer: false)
window.title = "Installation test fixture"
window.makeKeyAndOrderFront(nil)
app.activate(ignoringOtherApps: true)
app.run()
''')
subprocess.run(['swiftc', str(source), '-o', str(contents / 'MacOS/fixture')], check=True)
subprocess.run(['swift', str(helper), str(fixture), str(work / 'fixture.png')], check=True, timeout=240)
print('PASS: installation harness compiles, launches via LaunchServices and observes a real native window')
