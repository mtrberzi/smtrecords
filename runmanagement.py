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

        nValidations = 0
        nValidationSuccesses = 0
        nValidationFailures = 0
        nValidationErrors = 0

        invalidCases = []
        errorCases = []
        validationSolversUsed = set()

        for r in run.results:
            for v in r.validation_results:
                nValidations += 1
                validationSolversUsed.add(v.validation_solver.name)
                if not v.success_status:
                    nValidationErrors += 1
                    if r not in errorCases:
                        errorCases.append(r)
                else:
                    if v.pass_status:
                        nValidationSuccesses += 1
                    else:
                        nValidationFailures += 1
                        if r not in invalidCases:
                            invalidCases.append(r)
        print("Validated against:", end='')
        for s in validationSolversUsed:
            print(" " + s, end='')
        print("")
        print("Total number of validation checks: {}".format(nValidations))
        print("VALID: {} INVALID: {} ERROR: {}".format(nValidationSuccesses, nValidationFailures, nValidationErrors))
        if invalidCases:
            print("Invalid cases:")
            for r in invalidCases: # r : RunResult
                desc = "{} : {}".format(r.case.path, r.solver_status)
                for v in r.validation_results:
                    response = v.response
                    if r.solver_status == 'sat' and response == 'unsat':
                        response = 'unsat-with-model'
                    desc += " | {} : {}".format(v.validation_solver.name, response)
                print(desc)
        if errorCases:
            print("Errors occurred while validating:")
            for r in errorCases:
                print(r.case.path)

ignore_completion = False # debug flag. set to true to allow a resumed run to be "restarted". this will overwrite its previous results
                
def resume(session, run):
    if run.complete and not ignore_completion:
        return
    for r in run.results:
        if r.complete and not ignore_completion:
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

        if r.run.command_line.strip() != '':
            args = r.run.command_line.split(" ") # TODO this doesn't properly allow quoted args, etc
        else:
            args = []
        print(r.case.path)
        result = tasks.run_smtlib_solver(solverpath, instancepath, 20, args)
        r.complete = True
        r.solver_status = result.result
        r.solver_output = result.stdout
        r.solver_stderr = result.stderr
        r.completion_time = int(round(result.runtime * 1000)) # convert to milliseconds
        r.hostname = platform.node()
        session.commit()
    # check existence of validation entry for all runs
    for r in run.results:
        if r.complete and (r.solver_status == 'sat' or r.solver_status == 'unsat'):
            # ensure there is a validation entry for every validation solver
            for validation_solver in session.query(dbobj.ValidationSolver).order_by(dbobj.ValidationSolver.id):
                ret = session.query(dbobj.ValidationResult).filter(dbobj.ValidationResult.result_id == r.id).filter(dbobj.ValidationResult.validation_solver_id == validation_solver.id).one_or_none()
                if not ret:
                    # create entry
                    vResult = dbobj.ValidationResult(result=r, validation_solver=validation_solver, running_status=False, success_status=False, pass_status=False, response="")
                    session.add(vResult)
        session.commit()

    # perform all outstanding validation tasks
    for r in run.results:
        if r.complete and (r.solver_status == 'sat' or r.solver_status == 'unsat'):
            for validationRun in r.validation_results:
                if not validationRun.running_status:
                    # for now we run validation solvers locally; TODO celery integration
                    # construct full path to instance
                    instancepath = os.path.join(r.case.benchmark.path, r.case.path)
                    solverpath = os.path.join(config.validationsolverbase, validationRun.validation_solver.path)

                    if not os.path.isfile(instancepath):
                        print("ERROR: instance not found at {}".format(instancepath))
                        session.rollback()
                        continue
                    if not os.path.isfile(solverpath):
                        print("ERROR: validation solver binary not found at {}".format(solverpath))
                        session.rollback()
                        continue

                    # TODO add solver command line to database
                    cli = validationRun.validation_solver.command_line.split(" ") # TODO this doesn't allow quoted strings, etc.
                    args = [solverpath]
                    for x in cli:
                        args.append(x)
                    expectedResult = r.solver_status
                    testOutput = r.solver_output
                    validationResult = tasks.validate_result(args, instancepath, expectedResult, testOutput)

                    validationRun.running_status = True
                    validationRun.success_status = validationResult.validationRunSuccessful
                    validationRun.pass_status = validationResult.validationPassed
                    validationRun.response = validationResult.response

                    session.add(validationRun)
                    session.commit()
        
    # now double-check that all results are in
    done = True
    for r in run.results:
        if not r.complete:
            done = False
            break
        for v in r.validation_results:
            if not v.running_status:
                done = False
                break
    if done:
        run.complete = True
        session.commit()
