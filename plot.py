#!/usr/bin/env python3

import dbobj
import config
import sqlalchemy
from sqlalchemy.orm import sessionmaker
import sys

import json2cactus

def usage():
    print("Usage: " + sys.argv[0] + " plot-title ID [ID ]*")
    print("Each ID is the numeric identifier of a run to include in the plot.")

if len(sys.argv) < 3:
    usage()
    sys.exit(1)

engine = dbobj.mk_engine()
Session = sessionmaker(bind=engine)
session = Session()

title = sys.argv[1]

runs = []

for sID in sys.argv[2:]:
    nID = None
    try:
        nID = int(sID)
    except ValueError:
        print("{} is not a valid numeric run identifier.".format(sID))
        sys.exit(1)
    if nID is None:
        print("{} is not a valid numeric run identifier.".format(sID))
        sys.exit(1)
    # attempt to look up the run
    result = session.query(dbobj.Run).filter(dbobj.Run.id == nID).one_or_none()
    if result is None:
        print("Run #{} does not exist in the database.".format(nID))
        sys.exit(1)
    if not result.complete:
        print("Run #{} is incomplete and can't be plotted.".format(nID))
        sys.exit(1)
    # if we have more than one run, make sure they're all from the same benchmark
    if runs:
        if result.benchmark.id != runs[0].benchmark.id:
            print("Run #{} is from a different benchmark than run #{}.".format(result.id, runs[0].id))
            sys.exit(1)

    # OK
    runs.append(result)

# Format the data for json2cactus.data2png().
# Each data point is a map with the following keys:
#  "problem" = instance name (String)
#  "result" = "sat" | "unsat" | "timeout" | "unknown" | "error" (String)
#  "solver" = solver name (String)
#  "elapsed" = runtime in seconds (Double)

formattedResults = {}

for run in runs:
    solver = "{}-{}".format(run.solver_version.solver.name, run.solver_version.version)
    formattedResults[solver] = []
    for result in run.results:
        resultObj = {}
        resultObj["solver"] = solver
        resultObj["result"] = result.solver_status
        resultObj["problem"] = result.case.path
        resultObj["elapsed"] = float(result.completion_time) / 1000.0
        formattedResults[solver].append(resultObj)

# print PNG image
sys.stdout.buffer.write(json2cactus.data2png(formattedResults.values(), title))
