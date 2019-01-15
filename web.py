from __future__ import absolute_import

from flask import Flask, g, render_template, url_for
from . import dbobj
from . import config
from . import json2cactus
import sqlalchemy
from sqlalchemy.orm import sessionmaker
import sys
import os
import io
import base64

def get_db_session():
    if 'db' not in g:
        engine = dbobj.mk_engine()
        Session = sessionmaker(bind=engine)
        g.db = Session()
    return g.db

def close_db_session(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def cactus_plot(title, runs):
    if runs:
        # Format the data for json2cactus.data2png().
        # Each data point is a map with the following keys:
        #  "problem" = instance name (String)
        #  "result" = "sat" | "unsat" | "timeout" | "unknown" | "error" (String)
        #  "solver" = solver name (String)
        #  "elapsed" = runtime in seconds (Double)

        formattedResults = {}

        for run in runs:
            solver = "#{} {}-{}".format(run.id, run.solver_version.solver.name, run.solver_version.version)
            formattedResults[solver] = []
            for result in run.results:
                resultObj = {}
                resultObj["solver"] = solver
                resultObj["result"] = result.solver_status
                resultObj["problem"] = result.case.path
                resultObj["elapsed"] = float(result.completion_time) / 1000.0
                formattedResults[solver].append(resultObj)

        # print PNG image
        png = json2cactus.data2png(formattedResults.values(), title)
        plot_url = base64.b64encode(png).decode()
        #return '<img src="data:image/png;base64,{}">'.format(plot_url)
        return plot_url
    else:
        return ""        

        
## Flask app startup
app = Flask(__name__)
app.teardown_appcontext(close_db_session)
##

@app.route('/benchmarks')
def all_benchmarks():
    session = get_db_session()
    benchmarks = session.query(dbobj.Benchmark).order_by(dbobj.Benchmark.id).all()
    return render_template('benchmarks.html', benchmarks=benchmarks)

@app.route('/benchmark/<int:bmID>')
def show_benchmark(bmID):
    return "???"

@app.route('/run/<int:runID>')
def show_run(runID):
    session = get_db_session()
    run = session.query(dbobj.Run).filter(dbobj.Run.id == runID).one_or_none()
    if run:
        plot = cactus_plot(title="Run #{}".format(run.id), runs=[run])
    else:
        plot = None
    return render_template('run.html', run=run, cactus_plot=plot)

@app.route('/runs')
def all_runs():
    session = get_db_session()
    runs = session.query(dbobj.Run).order_by(dbobj.Run.startdate.desc()).all()
    return render_template('runs.html', desc="all runs", runs=runs)

@app.route('/')
def root():
    session = get_db_session()
    nSolvers = session.query(sqlalchemy.func.count(dbobj.Solver.id)).scalar()
    nRuns = session.query(sqlalchemy.func.count(dbobj.Run.id)).scalar()
    nBenchmarks = session.query(sqlalchemy.func.count(dbobj.Benchmark.id)).scalar()
    nVersions = session.query(sqlalchemy.func.count(dbobj.SolverVersion.id)).scalar()
    return render_template('root.html', nRuns=nRuns, nBenchmarks=nBenchmarks, nVersions=nVersions, nSolvers=nSolvers)
