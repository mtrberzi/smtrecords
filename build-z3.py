#!/usr/bin/env python3

# build-z3.py: automatically clone, build, and test Z3
# Basic usage: build-z3.py [options] [branch-name]
# branch-name defaults to "develop" if not provided.

import git
import optparse
import tempfile
import os
import sys
import os.path
import subprocess

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

### entry point
scriptbase=os.path.dirname(os.path.realpath(__file__))

usage = "usage: %prog [options] [branch-name]"
parser = optparse.OptionParser(usage)
parser.add_option("-b", "--build-only", action="store_true", dest="build_only", default=False, help="only build and register the solver; don't run any tests")
parser.add_option("-q", "--quiet", action="store_false", dest="verbose", default=True, help="don't print status messages to stdout")
parser.add_option("-r", "--remote", dest="remote", default="https://github.com/mtrberzi/z3", help="URI of repository to clone")
parser.add_option("-s", "--solver", dest="solverName", default="z3str3-testing", help="name of solver to register (defaults to '%default')")
parser.add_option("-j", "--jobs", dest="jobs", default="2", help="number of concurrent 'make' jobs to use when compiling (default %default)")
parser.add_option("-t", "--test-arguments", dest="testargs", default="-T:20 smt.string_solver=z3str3", help="extra argument string to pass to test binary (default '%default')")

(options, args) = parser.parse_args()
branch = "develop"
if len(args) == 0:
    pass # use default branch
elif len(args) == 1:
    branch = args[0]
else:
    parser.error("incorrect number of arguments")
    
with tempfile.TemporaryDirectory() as tmpdirname:
    if options.verbose:
        print("Cloning {} to {}".format(options.remote, tmpdirname))
    # clone remote repo to tmpdir
    repo = git.Repo.clone_from(options.remote, tmpdirname)
    if repo is None:
        eprint("Failed to clone repository")
        sys.exit(1)
    if not branch in repo.remotes['origin'].refs:
        eprint("Branch {} does not exist in repository".format(branch))
        sys.exit(1)
    # checkout the branch we want to build
    ref = repo.remotes['origin'].refs[branch]
    repo.create_head(branch, ref)
    repo.heads[branch].set_tracking_branch(ref)
    repo.heads[branch].checkout()
    version = repo.head.commit.hexsha
    solverVersion = branch + "-" + version
    stdout_target = None
    if not options.verbose:
        stdout_target = subprocess.DEVNULL
    # run config script and make
    try:
        subprocess.check_call(["python", "scripts/mk_make.py"], stdout=stdout_target, cwd=tmpdirname)
        subprocess.check_call(["make", "-j", options.jobs], stdout=stdout_target, cwd=os.path.join(tmpdirname, "build"))
    except subprocess.CalledProcessError as e:
        eprint("Failed to compile Z3.")
        sys.exit(1)
    # now we should have a Z3 binary at tmpdirname/build/z3
    # so, we should be able to call new-solver.py to register it
    try:
        subprocess.check_call(["./new-solver.py", options.solverName, solverVersion, os.path.join(tmpdirname, "build", "z3")], stdout=stdout_target, cwd=scriptbase)
    except subprocess.CalledProcessError as e:
        eprint("Failed to register solver.")
        sys.exit(1)
    if options.build_only:
        sys.exit(0)
# tmpdir is now deleted.

# now run tests
try:
    subprocess.check_call(["./run-solver.py", options.solverName, solverVersion, "all", options.testargs], stdout=stdout_target, cwd=scriptbase)
except subprocess.CalledProcessError as e:
    eprint("An error occurred while running tests.")
    sys.exit(1)
