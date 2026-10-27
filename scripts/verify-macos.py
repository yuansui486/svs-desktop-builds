"""Run the published application, with source cwd and development overrides removed."""
import json
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
run(['node', tests / 'integrated-skills-auth-smoke.mjs', app])
run(['node', tests / 'integrated-media-smoke.mjs', app])
modules = app / 'runtime/remotion/node_modules'
env['SVS_TEST_ASSETS'] = str(app / 'runtime/assets')
chrome = next(modules.glob('.remotion/chrome-headless-shell/mac-arm64/**/chrome-headless-shell'))
env['SVS_TEST_CHROME'] = str(chrome)
run(['node', tests / 'external-runtime-render-smoke.cjs', modules, work])
run(['node', tests / 'component-resource-render-smoke.cjs', modules, work])
ppt = run([app / 'skills/ppt-video-create/tools/bin/ppt-runner', 'check-env'], True)
view = next(line.split('packaged Remotion runtime: ', 1)[1].strip() for line in ppt.splitlines() if 'packaged Remotion runtime: ' in line)
run(['node', tests / 'ppt-shared-runtime-smoke.cjs', view, Path(view) / 'node_modules', work])
moved = work / 'moved app resources'
app.rename(moved)
run([moved / 'svs-runner', 'preflight-runtime', '--json'])
run([moved / '新媒体后台.app/Contents/MacOS/launch', '--help'])
print('PASS: macOS ARM64 package integrity, entrypoints, four local render paths and relocation')
