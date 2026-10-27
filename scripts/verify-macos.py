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
work = Path(tempfile.mkdtemp(prefix='svs-macos-verify-'))
subprocess.run(['ditto', '-x', '-k', str(archive), str(work / 'extracted')], check=True)
app = work / 'extracted' / 'svs-app'
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
run([app / '新媒体后台.app/Contents/MacOS/launch', '--help'])
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
lite = work / 'lite/svs-app'
assert not (lite / 'runtime/dependencies').exists()
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
moved = work / 'moved app resources'
app.rename(moved)
run([moved / 'svs-runner', 'preflight-runtime', '--json'])
run([moved / '新媒体后台.app/Contents/MacOS/launch', '--help'])
print('PASS: macOS ARM64 package integrity, entrypoints, four local render paths and relocation')
