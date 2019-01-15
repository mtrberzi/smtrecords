#!/usr/bin/env python3

import dbobj
import config

import sqlalchemy
from sqlalchemy.orm import sessionmaker
import sys

def usage():
    print("Usage: " + sys.argv[0] + " run-id")
    print("Prints to standard output a 'dump' of the given run, formatted as follows:")
    print("casename TAB status TAB runtime NEWLINE")
    print("where status is 'sat v-ok', 'unsat', 'timeout', 'unknown', 'error' and runtime is a decimal time in seconds")

if len(sys.argv) != 2:
    usage()
    sys.exit(1)

runID = None
try:
    runID = int(sys.argv[1])
except ValueError:
    print("Run ID must be numeric.")
    sys.exit(1)

engine = dbobj.mk_engine()
Session = sessionmaker(bind=engine)
session = Session()

run = session.query(dbobj.Run).filter(dbobj.Run.id == runID).one_or_none()

if run is None:
    print("Run not found.")
    sys.exit(1)

for result in run.results:
    casename = result.case.path
    status = result.solver_status
    # TODO check validation status
    if status == 'sat':
        status = 'sat v-ok'
    runtime = float(result.completion_time) / 1000.0
    print("{}\t{}\t{:.3f}".format(casename, status, runtime))
