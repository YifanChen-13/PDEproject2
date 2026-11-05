"""Reproduce the project calculations and figures in fresh output directories."""
import datetime
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent


def run(script, *args, env=None, capture_output_directory=False):
    command = [sys.executable, str(ROOT / script), *map(str, args)]
    print('\nRunning', ' '.join(command), flush=True)
    if not capture_output_directory:
        subprocess.run(command, cwd=ROOT, env=env, check=True)
        return None
    process = subprocess.Popen(command, cwd=ROOT, env=env, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT, text=True)
    output_directory = None
    for line in process.stdout:
        print(line, end='', flush=True)
        if line.startswith('OUTPUT_DIRECTORY='):
            output_directory = Path(line.strip().split('=', 1)[1])
    if process.wait() != 0:
        raise subprocess.CalledProcessError(process.returncode, command)
    if output_directory is None:
        raise RuntimeError('Stage 2 did not report its output directory')
    return output_directory


def main():
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    out = ROOT / 'reproduction_runs' / stamp
    out.mkdir(parents=True, exist_ok=False)
    env = os.environ.copy()
    env['PDE_STAGE1_OUTPUT'] = str(out / 'stage1')
    env['PDE_STAGE2_OUTPUT_ROOT'] = str(out / 'stage2_D_runs')
    run('stage1_validation.py', env=env)
    run('run_project.py', '--output-dir', out)
    run('build_report.py', '--input-root', out)
    stage2 = run('stage2_studies.py', env=env, capture_output_directory=True)
    run('verify_stage2_D.py', stage2)
    run('independent_audit.py', '--output-dir', out / 'independent_audit')
    print(f'\nReproduction output: {out}\nStage 2 output: {stage2}', flush=True)


if __name__ == '__main__':
    main()
