from __future__ import absolute_import
from .celery import app
from .import config
from . import tasks
from . import dbobj
import sqlalchemy
from sqlalchemy.orm import sessionmaker
import sys
import os
import os.path

@app.task
def build_z3():
    raise Exception("not implemented yet")

@app.task
def benchmark_instance(result_id):
    engine = dbobj.mk_engine()
    Session = sessionmaker(bind=engine)
    session = Session()

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
    r.complete = True
    r.solver_status = result.result
    r.solver_output = result.stdout
    r.solver_stderr = result.stderr
    r.completion_time = int(round(result.runtime * 1000)) # convert to milliseconds
    r.hostname = platform.node()
    session.commit()

@app.task
def validate_instance():
    raise Exception("not implemented yet")


