#!/usr/bin/env python3

from smtrecords import dbobj, config

import sqlalchemy
from sqlalchemy.orm import sessionmaker
import sys
import os

def usage():
    print("Usage: " + sys.argv[0] + " [solvername]")
    print("With no arguments, print all registered solvers and the number of versions of each solver.")
    print("With one argument, print the names of all registered versions of that solver.")

if len(sys.argv) == 2 and (sys.argv[1] == '--help' or sys.argv[1] == '-h'):
    usage()
    sys.exit(1)

if len(sys.argv) > 2: # too many arguments
    usage()
    sys.exit(1)

engine = dbobj.mk_engine()
Session = sessionmaker(bind=engine)
session = Session()
    
if len(sys.argv) == 1: # called without solvername
    solvers = session.query(dbobj.Solver).all()
    print("%d solvers available:" % (len(solvers),))
    for solver in solvers:
        nVersions = session.query(dbobj.Solver, dbobj.SolverVersion).filter(dbobj.Solver.id == dbobj.SolverVersion.solver_id).filter(dbobj.Solver.id == solver.id).count()
        print("%s (%d versions)" % (solver.name, nVersions))
else: # called with solvername
    solvername = sys.argv[1]
    solver = session.query(dbobj.Solver).filter(dbobj.Solver.name == solvername).one_or_none()
    if solver is None:
        print("Solver %s not registered." % (solvername,))
        sys.exit(0)
    versions = session.query(dbobj.Solver, dbobj.SolverVersion).filter(dbobj.Solver.id == dbobj.SolverVersion.solver_id).filter(dbobj.Solver.id == solver.id).order_by(dbobj.SolverVersion.creationdate).all()
    print("%d versions of %s available:" % (len(versions), solvername))
    for xx, version in versions:
        print("%s (%s)" % (version.version, version.creationdate))
