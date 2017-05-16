#!/usr/bin/env python3

import dbobj
import config

import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import MultipleResultsFound
import sys
import os
import os.path
import hashlib
import re

# Note that this command isn't idempotent; it's perfectly fair to run the same version of a solver
# on a benchmark multiple times.

## Entry point

if len(sys.argv) < 4:
    print("Usage: " + sys.argv[0] + " solver-name solver-version benchmark-name [solver-arguments...]")
    sys.exit(1)

solverName = sys.argv[1]
solverVersionName = sys.argv[2]
benchmarkName = sys.argv[3]
solverArguments = []
for i in range(4, len(sys.argv)):
    solverArguments.append(sys.argv[i])

engine = dbobj.mk_engine()
Session = sessionmaker(bind=engine)
session = Session()

# check if this solver, version, and benchmark exist

solver = None
benchmark = None

try:
    solver = session.query(dbobj.Solver, dbobj.SolverVersion).filter(dbobj.Solver.id == dbobj.SolverVersion.solver_id, dbobj.Solver.name == solverName, dbobj.SolverVersion.version == solverVersionName).one_or_none()
    if solver is None:
        print("No solver %s with version %s was found." % (solverName, solverVersionName))
        session.rollback()
        sys.exit(1)
    # unpack (Solver, SolverVersion)
    solver = solver[1]
    benchmark = session.query(dbobj.Benchmark).filter(dbobj.Benchmark.name == benchmarkName).one_or_none()
    if benchmark is None:
        print("No benchmark %s found." % (benchmarkName,))
        session.rollback()
        sys.exit(1)
except MultipleResultsFound as e:
    print("Database inconsistency detected, multiple benchmarks/solvers found!")
    print(e)
    session.rollback()
    sys.exit(1)
   
# create Run object
#solverRun = dbobj.Run(solver_version = solver, benchmark = benchmark, command_line = " ".join(solverArguments), complete=False)
solverRun = dbobj.Run(benchmark=benchmark, solver_version=solver, command_line="")
# create a Result object for each case
for benchmarkCase in benchmark.cases:
    result = dbobj.RunResult(run = solverRun, case = benchmarkCase, complete=False, solver_status=None, solver_output=None, solver_stderr=None, completion_time=None)

session.commit()
print("Scheduled run of %s for %s-%s." % (benchmarkName, solverName, solverVersionName))

# TODO launch celery tasks
