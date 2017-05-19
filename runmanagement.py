import dbobj
import config

import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import MultipleResultsFound
import sys
import os
import os.path
import platform

import tasks

# report(run):
# takes a Run DB Object and prints to stdout a report on its status

def report(session, run):
    print("Run %s, test set %s, solver %s-%s" % (run.id, run.benchmark.name, run.solver_version.solver.name, run.solver_version.version))
    if not run.complete:
        nTests = 0
        nComplete = 0
        nPending = 0
        for r in run.results:
            nTests += 1
            if r.complete:
                nComplete += 1
            else:
                nPending += 1
        print("Status: pending (%d/%d cases complete, %d pending)" % (nComplete, nTests, nPending))
    else:
        print("Status: complete")
        nCases = 0
        nSAT = 0
        nUNSAT = 0
        nTIMEOUT = 0
        nUNKNOWN = 0
        nERROR = 0
        totalTime = 0 # milliseconds, integer
        totalTimeWithoutTimeouts = 0 # milliseconds, integer
        for r in run.results:
            nCases += 1
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
        print("Total number of cases: {}".format(nCases))
        print("SAT: {} UNSAT: {}".format(nSAT, nUNSAT))
        print("Timeout: {} Unknown: {} Error: {}".format(nTIMEOUT, nUNKNOWN, nERROR))
        timeF = float(totalTime) / 1000.0
        timeNoTimeoutF = float(totalTimeWithoutTimeouts) / 1000.0
        print("Total time: (without timeouts) {:.3f} (with timeouts) {:.3f}".format(timeNoTimeoutF, timeF))
        # TODO validation report
            
def resume(session, run):
    if run.complete:
        return
    for r in run.results:
        if r.complete:
            pass
        # for now we run every solver locally; TODO celery integration
        # construct full path to instance
        instancepath = os.path.join(r.case.benchmark.path, r.case.path)
        solverpath = os.path.join(config.solverbase, r.run.solver_version.path)

        # check if instance and solver both exist
        if not os.path.isfile(instancepath):
            print("ERROR: instance not found at {}".format(instancepath))
            session.rollback()
            continue

        if not os.path.isfile(solverpath):
            print("ERROR: solver not found at {}".format(solverpath))
            session.rollback()
            continue
        
        args = r.run.command_line.split(" ")
        result = tasks.run_smtlib_solver(solverpath, instancepath, 20, args)
        r.complete = True
        r.solver_status = result.result
        r.solver_output = result.stdout
        r.solver_stderr = result.stderr
        r.completion_time = int(round(result.runtime * 1000)) # convert to milliseconds
        r.hostname = platform.node()
        session.commit()
    # now double-check that all results are in
    done = True
    for r in run.results:
        if not r.complete:
            done = False
            break
    if done:
        run.complete = True
        session.commit()
