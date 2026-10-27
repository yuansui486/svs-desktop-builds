"""Run the published application, with source cwd and development overrides removed."""
import json
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

source, archive = map(lambda p: Path(p).resolve(), sys.argv[1:])
work = Path(tempfile.mkdtemp(prefix='svs-macos-verify-')).resolve()
subprocess.run(['ditto', '-x', '-k', str(archive), str(work / 'extracted')], check=True)
bundle = work / 'extracted' / '新媒体后台.app'
assert list((work / 'extracted').iterdir()) == [bundle], 'ZIP must contain one app only'
launcher = bundle / 'Contents/MacOS/launch'
assert launcher.read_bytes()[:4] == bytes.fromhex('cffaedfe'), 'Launcher must be native Mach-O'
subprocess.run(['codesign', '--verify', '--deep', '--strict', str(bundle)], check=True)
support = work / 'Application Support/SVS'
app = Path(subprocess.check_output([str(launcher), '--prepare-only', '--data-dir', str(support)], text=True).strip())
assert app.parent == support / 'installations'
assert (app / 'runtime/dependencies').resolve() == support / 'data/runtime/dependencies'
bundle_digest = hashlib.sha256((bundle / 'Contents/Resources/payload.zip').read_bytes()).hexdigest()
assert bundle_digest == (bundle / 'Contents/Resources/payload.sha256').read_text().strip()
env = {k: v for k, v in os.environ.items() if not k.startswith(('SVS_', 'UA2_')) and k != 'SKILL_ROOT'}
env.update(ONECOLLEAGUE_HOME=str(work / 'home'), SVS_NO_LOGIN_UI='1')
manifest = json.loads((app / 'runtime/dependencies.json').read_text())
deps = {m['id']: app / 'runtime/dependencies' / m['id'] / hashlib.sha256(json.dumps(m, ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()[:16] for m in manifest['modules']}
node = deps['node'] / 'bin/node'
env['PATH'] = ':'.join([str(node.parent), str(deps['media']), '/usr/bin', '/bin', '/usr/sbin', '/sbin'])

def run(args, capture=False):
    result = subprocess.run(list(map(str, args)), cwd=work, env=env, check=True, text=True, stdout=subprocess.PIPE if capture else None, timeout=600)
    return result.stdout

report = json.loads(run([app / 'svs-runner', 'preflight-runtime', '--json'], True))
assert report['status'] == 'ok'
assert Path(report['skill_root']).resolve() == (app / 'runtime').resolve()
run([app / 'svs-gui', '--help'])
for relative in ['illustration-video-maker/tools/bin/runner', 'num-people/tools/bin/num-people-runner', 'ppt-video-create/tools/bin/ppt-runner']:
    run([app / 'skills' / relative, 'check-env'])
tests = source / 'crates/svs-gui/tests'
run([node, tests / 'integrated-skills-auth-smoke.mjs', app])
run([node, tests / 'integrated-media-smoke.mjs', app])
modules = deps['remotion'] / 'node_modules'
env['SVS_TEST_ASSETS'] = str(app / 'runtime/assets')
chrome = deps['chrome'] / 'chrome-headless-shell'
env['SVS_TEST_CHROME'] = str(chrome)
run([node, tests / 'external-runtime-render-smoke.cjs', modules, work])
run([node, tests / 'component-resource-render-smoke.cjs', modules, work])
ppt = run([app / 'skills/ppt-video-create/tools/bin/ppt-runner', 'check-env'], True)
view = next(line.split('packaged Remotion runtime: ', 1)[1].strip() for line in ppt.splitlines() if 'packaged Remotion runtime: ' in line)
run([node, tests / 'ppt-shared-runtime-smoke.cjs', view, modules, work])
# Lite starts from an empty dependency directory, with no system Node on PATH.
subprocess.run(['cargo', 'build', '--release', '-p', 'skill-packager', '--example', 'dependencies'], cwd=source, check=True)
lite_zip = archive.with_name('svs-app-mac-arm64-lite.zip')
run(['/usr/bin/ditto', '-x', '-k', lite_zip, work / 'lite'])
lite_bundle = work / 'lite/新媒体后台.app'
lite_launcher = lite_bundle / 'Contents/MacOS/launch'
lite = Path(run([lite_launcher, '--prepare-only', '--data-dir', work / 'lite-support'], True).strip())
assert not list((lite / 'runtime/dependencies').iterdir())
env['PATH'] = '/usr/bin:/bin:/usr/sbin:/sbin'
helper = source / 'target/release/examples/dependencies'
run([helper, 'install', lite])
run([lite / 'svs-runner', 'preflight-runtime', '--json'])
for m in manifest['modules']:
    assert (lite / deps[m['id']].relative_to(app) / '.ready').is_file()
print('PASS: lite installation from domestic mirrors, no system Node, all resources verified')
# Corrupt FFmpeg, then recover from the verified cache with networking disabled.
tool = lite / deps['media'].relative_to(app) / 'ffmpeg'
original = hashlib.sha256(tool.read_bytes()).hexdigest()
with tool.open('r+b') as stream:
    stream.seek(100); value = stream.read(1); stream.seek(100); stream.write(bytes([value[0] ^ 1]))
env.update(HTTP_PROXY='http://127.0.0.1:9', HTTPS_PROXY='http://127.0.0.1:9', ALL_PROXY='http://127.0.0.1:9')
run([helper, 'repair', lite])
assert hashlib.sha256(tool.read_bytes()).hexdigest() == original
run([lite / 'svs-runner', 'preflight-runtime', '--json'])
print('PASS: damaged resource repaired from local cache without network')
# Replace the app with another edition (different payload identity), retain account/data/tools.
data = support / 'data'
(data / 'svs-login.dat').write_bytes(b'test encrypted credential placeholder')
(data / 'drafts/keep.txt').write_text('user draft')
(data / 'runtime/memory/keep.txt').write_text('user preference')
upgraded = Path(run([lite_launcher, '--prepare-only', '--data-dir', support], True).strip())
assert upgraded != app
assert (upgraded / 'runtime/dependencies').resolve() == (app / 'runtime/dependencies').resolve()
assert (data / 'svs-login.dat').read_bytes() == b'test encrypted credential placeholder'
assert (upgraded / 'drafts/keep.txt').read_text() == 'user draft'
assert (upgraded / 'runtime/memory/keep.txt').read_text() == 'user preference'
run([upgraded / 'svs-runner', 'preflight-runtime', '--json'])
# Moving the single .app, including launching from a read-only mounted volume, is sufficient.
moved = work / 'Applications/新媒体后台.app'
moved.parent.mkdir()
bundle.rename(moved)
assert Path(run([moved / 'Contents/MacOS/launch', '--prepare-only', '--data-dir', support], True).strip()) == app
subprocess.run(['hdiutil', 'create', '-srcfolder', str(moved.parent), '-format', 'UDRO', str(work / 'readonly.dmg')], check=True)
mount = work / 'mounted'
subprocess.run(['hdiutil', 'attach', str(work / 'readonly.dmg'), '-mountpoint', str(mount), '-nobrowse', '-readonly'], check=True)
try:
    installed = Path(run([mount / '新媒体后台.app/Contents/MacOS/launch', '--prepare-only', '--data-dir', work / 'readonly-support'], True).strip())
    run([installed / 'svs-gui', '--help'])
finally:
    subprocess.run(['hdiutil', 'detach', str(mount)], check=True)
assert hashlib.sha256((moved / 'Contents/Resources/payload.zip').read_bytes()).hexdigest() == bundle_digest
subprocess.run(['codesign', '--verify', '--deep', '--strict', str(moved)], check=True)
print('PASS: single native app, read-only volume, upgrade preserves credentials/drafts/memory/shared tools, bundle unchanged')
print('PASS: macOS ARM64 package integrity, entrypoints, four local render paths and relocation')
