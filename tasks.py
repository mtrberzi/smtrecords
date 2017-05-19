from __future__ import absolute_import

import os
import tempfile
import shutil
import subprocess
import time
import stat
import signal

def get_process_children(pid):
    p = subprocess.Popen('ps --no-headers -o pid --ppid %d' % pid, shell = True,stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    stdout, stderr = p.communicate()
    return [int(p) for p in stdout.split()]
        
# Run a command with a timeout, after which it will be forcibly killed.
def run(args, cwd = None, shell = False, kill_tree = True, timeout = -1, env = None):
    class Alarm(Exception):
        pass
    def alarm_handler(signum, frame):
        raise Alarm
    p = subprocess.Popen(args, shell = shell, cwd = cwd, stdout = subprocess.PIPE, stderr = subprocess.PIPE, env = env)
    if timeout != -1:
        signal.signal(signal.SIGALRM, alarm_handler)
        signal.alarm(timeout)
    try:
        stdout, stderr = p.communicate()
        stdout = stdout.decode(encoding='ascii')
        stderr = stderr.decode(encoding='ascii')
        if timeout != -1:
            signal.alarm(0)
    except Alarm:
        pids = [p.pid]
        if kill_tree:
            pids.extend(get_process_children(p.pid))
        for pid in pids:
            # process might have died before getting to this line
            # so wrap to avoid OSError: no such process
            try:
                os.kill(pid, signal.SIGKILL)
            except OSError:
                pass
        return -9, '', ''
    return p.returncode, stdout, stderr

class TestResult:
    def __init__(self, testname, runtime, result):
        self.testname = testname
        self.runtime = runtime
        self.result = result
        self.stdout = None
        self.stderr = None


def run_smtlib_solver(z3file, testfile, timeout=20, extraArguments = []):
    runtime = 0.0
    result = ''
    verify = ''
    solveroutput = ''
    solverstderr = ''
    error = ''

    try:
        startTime = time.time()
        args = [z3file]
        for extra in extraArguments:
            args.append(extra)
        args.append(testfile)
        (exitCode, output, errors) = run(args, timeout=timeout)
        solveroutput = output
        solverstderr = errors
        endTime = time.time()
        runtime = round( float(endTime - startTime), 3)
        if len(output) == 0 or exitCode == -9:
            result = 'timeout'
        else:
            lines = output.split("\n")
            errlines = errors.split("\n")

            combined_lines = ""
            for line in lines:
                combined_lines += " " + line
            for line in errlines:
                combined_lines += " " + line    
            
            lines = [line for line in lines if line.strip()]
            # check result status
            for line in lines:
                if line.startswith('(error'):
                    result = 'error'
                    error = combined_lines
                    break
                if 'unsat' in line:
                    result = 'unsat'
                    error = ''
                    break
                elif 'sat' in line:
                    result = 'sat'
                    error = ''
                    break
                elif 'unknown' in line:
                    result = 'unknown'
                    error = ''
                    break
                elif 'timeout' in line:
                    result = 'timeout'
                    error = ''
                    break
                else:
                    result = 'error'
                    error = combined_lines
                    break
    except Exception as e:
        result = 'crash'
        error = str(e)
        raise e
        
    result = TestResult(testfile, runtime, result)
    result.stdout = solveroutput
    result.stderr = solverstderr
    return result

