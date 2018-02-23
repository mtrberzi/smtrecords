from __future__ import absolute_import
from .celeryapp import app

from . import config, tasks, dbobj

import sqlalchemy
from sqlalchemy.orm import sessionmaker
import sys
import os
import os.path
import git
import tempfile
import subprocess
import shutil
import hashlib

def sha256hash(filePath):
    try:
        with open(filePath, 'rb') as f:
            hasher = hashlib.sha256()
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
            return hasher.hexdigest()
    except Exception:
        return ""

@app.task
def build_z3(solver_name, remote, branch):
    engine = dbobj.mk_engine()
    Session = sessionmaker(bind=engine)
    session = Session()
    with tempfile.TemporaryDirectory() as tmpdirname:
        # clone remote to tmpdir
        repo = git.Repo.clone_from(remote, tmpdirname)
        if repo is None:
            raise Exception("failed to clone repository")
        if not branch in repo.remotes['origin'].refs:
            raise Exception("branch {} doesn't exist in repository".format(branch))
        # checkout the branch we want to build
        ref = repo.remotes['origin'].refs[branch]
        repo.create_head(branch, ref)
        repo.heads[branch].set_tracking_branch(ref)
        repo.heads[branch].checkout()
        # get solver information
        version = repo.head.commit.hexsha
        solverVersion = branch + "-" + version

        # check database
        existingVersion = session.query(dbobj.Solver, dbobj.SolverVersion).filter(dbobj.Solver.id == dbobj.SolverVersion.solver_id).filter(dbobj.Solver.name == solver_name).filter(dbobj.SolverVersion.version == solverVersion).one_or_none()
        if existingVersion is not None:
            return
        
        stdout_target = None
        numCPUs = 1
        # this is a really silly and paranoid check to prevent
        # hijacking of os.cpu_count() to put weird things into the command line
        try:
            if os.cpu_count() is not None:
                numCPUs = int(os.cpu_count())
                if numCPUs < 1:
                    numCPUs = 1
        except ValueError:
            numCPUs = 1
        # run config/make
        try:
            subprocess.check_call(["python", "scripts/mk_make.py"], stdout=stdout_target, cwd=tmpdirname)
            subprocess.check_call(["make", "-j", str(numCPUs)], stdout=stdout_target, cwd=os.path.join(tmpdirname, "build"))
        except subprocess.CalledProcessError as e:
            raise Exception("failed to compile Z3: {}".format(str(e)))
        # if the solver type doesn't already exist, create it
        solverClass = session.query(dbobj.Solver).filter(dbobj.Solver.name == solver_name).one_or_none()
        if solverClass is None:
            solverClass = dbobj.Solver(name=solver_name)
            session.add(solverClass)
        # now we have a Z3 binary at "tmpdirname/build/z3";
        # we can copy it to the correct path and register it
        srcPath = os.path.join(tmpdirname, "build", "z3")
        checksum = sha256hash(srcPath)
        if checksum == "":
            raise Exception("I/O error")
        dstPath = os.path.join(config.solverbase, solver_name)
        dst = os.path.join(dstPath, solver_name + "-" + solverVersion)
        try:
            os.makedirs(dstPath, exist_ok=True)
            shutil.copyfile(srcPath, dst)
            mode = os.stat(dst).st_mode
            mode |= (mode & 0o444)>>2 # copy R bits to X bits
            os.chmod(dst, mode)
        except Exception as e:
            session.rollback()
            raise Exception("I/O error: {}".format(str(e)))
        solverVersion = dbobj.SolverVersion(version=solverVersion, path=dst, checksum=checksum)
        solverClass.versions.append(solverVersion)
    # tmpdir is now deleted
    session.commit()

# Task benchmark_instance()
# Argument: result_ids -- a list of values corresponding to RunResult "id" values
# Return: None
# Effect: Performs the specified runs and writes the combined result to the database
@app.task
def benchmark_instance(result_ids):
    engine = dbobj.mk_engine()
    Session = sessionmaker(bind=engine)
    session = Session()

    for result_id in result_ids:
        # get result object from result_id
        db_result = session.query(dbobj.RunResult).filter(dbobj.RunResult.id == result_id).one()
        db_run = db_result.run
        db_case = db_result.case

        # find local path to solver and instance
        solver_binary_path = os.path.join(config.solverbase, db_run.solver_version.path)
        instance_path = os.path.join(db_case.benchmark.path, db_case.path)

        if not os.path.isfile(instancepath):
            raise Exception("instance not found at {}".format(instancepath))
        if not os.path.isfile(solverpath):
            raise Exception("solver not found at {}".format(solverpath))
        if db_run.command_line.strip() != '':
            args = db_run.command_line.split(" ") # TODO allow quoted arguments
        else:
            args = []
        timeout = 20 # TODO read from run
        result = tasks.run_smtlib_solver(solver_binary, instance_file, timeout, args)
        # unpack result object and write database
        db_result.complete = True
        db_result.solver_status = result.result
        db_result.solver_output = result.stdout
        db_result.solver_stderr = result.stderr
        db_result.completion_time = int(round(result.runtime * 1000)) # convert to milliseconds
        db_result.hostname = platform.node()
        session.add(db_result)
    session.commit()

@app.task
def validate_instance():
    raise Exception("not implemented yet")


