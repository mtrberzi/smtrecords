#!/usr/bin/env python3

from __future__ import absolute_import

from smtrecords import dbobj, config, runmanagement

import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import MultipleResultsFound
import sys
import os
import os.path

#from celery import Celery
#import tasks

#import runmanagement

# Note that this command isn't idempotent; it's perfectly fair to run the same version of a solver
# on a benchmark multiple times.

## Entry point

if len(sys.argv) < 4:
    print("Usage: " + sys.argv[0] + " solver-name solver-version benchmark-name [solver-arguments...]")
    print("If benchmark name is 'all', solver will be run on all registered benchmarks.")
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

#celeryApp = Celery('smtrecords', include=['smtrecords.tasks'])
#celeryApp.config_from_object('celeryconfig')

# check if this solver, version, and benchmark exist

solver = None
benchmark = None
runAllBenchmarks = (benchmarkName == 'all')

try:
    solver = session.query(dbobj.Solver, dbobj.SolverVersion).filter(dbobj.Solver.id == dbobj.SolverVersion.solver_id, dbobj.Solver.name == solverName, dbobj.SolverVersion.version == solverVersionName).one_or_none()
    if solver is None:
        print("No solver %s with version %s was found." % (solverName, solverVersionName))
        session.rollback()
        sys.exit(1)
    # unpack (Solver, SolverVersion)
    solver = solver[1]
    if runAllBenchmarks:
        pass
    else:
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

if runAllBenchmarks:
    allBenchmarks = session.query(dbobj.Benchmark)
    if allBenchmarks == []:
        print("No benchmarks are available.")
        session.rollback()
        sys.exit(1)
    runs = []
    for benchmark in allBenchmarks:
        # create Run object
        solverRun = dbobj.Run(benchmark=benchmark, solver_version=solver, command_line=" ".join(solverArguments), complete=False)
        runs.append(solverRun)
        # create a Result object for each case
        for benchmarkCase in benchmark.cases:
            result = dbobj.RunResult(run = solverRun, case = benchmarkCase, complete=False, solver_status=None, solver_output=None, solver_stderr=None, completion_time=None, hostname=None)
        session.commit()
        print("Scheduled run of {} for {}-{} (ID {}).".format(benchmark.name, solverName, solverVersionName, solverRun.id))
    for run in runs:
        runmanagement.resume(session, run)
else:
    # create Run object
    solverRun = dbobj.Run(benchmark=benchmark, solver_version=solver, command_line=" ".join(solverArguments), complete=False)
    # create a Result object for each case
    for benchmarkCase in benchmark.cases:
        result = dbobj.RunResult(run = solverRun, case = benchmarkCase, complete=False, solver_status=None, solver_output=None, solver_stderr=None, completion_time=None, hostname=None)

    session.commit()
    print("Scheduled run of {} for {}-{} (ID {}).".format(benchmarkName, solverName, solverVersionName, solverRun.id))

    # since we've created the entries for the run, we can use the resumption mechanism to start it for real

    runmanagement.resume(session, solverRun)
    print("Complete.")
    runmanagement.report(session, solverRun)
