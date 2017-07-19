#!/usr/bin/env python3

import dbobj
import config

import sqlalchemy
from sqlalchemy.orm import sessionmaker
import sys

def usage():
    print("Usage: " + sys.argv[0] + " benchmark [solvername] [version]")
    print("With one argument, list all runs of the specified benchmark.")
    print("With a solver name, list all runs of the specified solver on the given benchmark.")
    print("With a solver name and version, list all runs of that version of the solver on the given benchmark.")

if len(sys.argv) == 2 and (sys.argv[1] == '--help' or sys.argv[1] == '-h'):
    usage()
    sys.exit(1)

if len(sys.argv) > 4 or len(sys.argv) == 1:
    usage()
    sys.exit(1)

engine = dbobj.mk_engine()
Session = sessionmaker(bind=engine)
session = Session()

runs = None

if len(sys.argv) == 2: # benchmark only
    benchmarkName = sys.argv[1]
    runs = session.query(dbobj.Run).join(dbobj.Benchmark).filter(dbobj.Benchmark.name == benchmarkName).order_by(dbobj.Run.startdate).all()
elif len(sys.argv) == 3: # benchmark and solver name
    benchmarkName = sys.argv[1]
    solverName = sys.argv[2]
    runs = session.query(dbobj.Run).join(dbobj.Benchmark).filter(dbobj.Benchmark.name == benchmarkName).join(dbobj.SolverVersion, dbobj.Solver).filter(dbobj.Solver.name == solverName).order_by(dbobj.Run.startdate).all()
elif len(sys.argv) == 4: # benchmark, solver name, version
    benchmarkName = sys.argv[1]
    solverName = sys.argv[2]
    solverVersion = sys.argv[3]
    runs = session.query(dbobj.Run).join(dbobj.Benchmark).filter(dbobj.Benchmark.name == benchmarkName).join(dbobj.SolverVersion, dbobj.Solver).filter(dbobj.Solver.name == solverName).filter(dbobj.SolverVersion.version == solverVersion).order_by(dbobj.Run.startdate).all()
else:
    usage()
    sys.exit(1)

if runs is None:
    print("No results found!")
    sys.exit(0)
    
print("{} runs found:".format(len(runs)))
for run in runs:
    if not run.complete:
        print("#{} {}-{} {} Incomplete".format(run.id, run.solver_version.solver.name, run.solver_version.version, run.startdate))
    else:
        nSAT = 0
        nUNSAT = 0
        nTIMEOUT = 0
        nUNKNOWN = 0
        nERROR = 0
        totalTime = 0 # milliseconds, integer
        totalTimeWithoutTimeouts = 0 # milliseconds, integer
        for r in run.results:
            if r.solver_status == 'sat':
                nSAT += 1
            elif r.solver_status == 'unsat':
                nUNSAT += 1
            elif r.solver_status == 'timeout':
                nTIMEOUT += 1
            elif r.solver_status == 'unknown':
                nUNKNOWN += 1
            else:
                nERROR += 1
            # accumulate time
            totalTime += r.completion_time
            if r.solver_status != 'timeout':
                totalTimeWithoutTimeouts += r.completion_time
        caseDisplay = "<SAT:{} UNSAT:{} T/O:{} UNK:{} ERR:{}>".format(nSAT, nUNSAT, nTIMEOUT, nUNKNOWN, nERROR)
        timeF = float(totalTime) / 1000.0
        timeNoTimeoutF = float(totalTimeWithoutTimeouts) / 1000.0
        timeDisplay = "({:.3f}s | {:.3f}s+T/O)".format(timeNoTimeoutF, timeF)
        print("#{} {}-{} {} {} {}".format(run.id, run.solver_version.solver.name, run.solver_version.version, run.startdate, timeDisplay, caseDisplay))

