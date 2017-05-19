#!/usr/bin/env python3

from __future__ import absolute_import
import dbobj
import config
import sqlalchemy
from sqlalchemy.orm import sessionmaker
import sys
import runmanagement

if len(sys.argv) != 2:
    print("Usage: {} run-id".format(sys.argv[0]))
    sys.exit(1)

engine = dbobj.mk_engine()
Session = sessionmaker(bind=engine)
session = Session()
    
runID = None
try:
    runID = int(sys.argv[1])
except ValueError:
    print("Run ID must be numeric.")
    sys.exit(1)

solverRun = session.query(dbobj.Run).filter(dbobj.Run.id == runID).one_or_none()
if solverRun is None:
    print("Run {} not found.".format(runID))
    sys.exit(1)

print("Resuming run {}: {} for {}-{}.".format(solverRun.id, solverRun.benchmark.name, solverRun.solver_version.solver.name, solverRun.solver_version.version))

runmanagement.resume(session, solverRun)
print("Complete.")
runmanagement.report(session, solverRun)


