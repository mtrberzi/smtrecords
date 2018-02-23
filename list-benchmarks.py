#!/usr/bin/env python3

from smtrecords import dbobj, config

import sqlalchemy
from sqlalchemy.orm import sessionmaker
import sys
import os

engine = dbobj.mk_engine()
Session = sessionmaker(bind=engine)
session = Session()

benchmarks = session.query(dbobj.Benchmark).all()

if len(benchmarks) == 0:
    print("No benchmarks registered.")
else:
    print("{} benchmarks registered:".format(len(benchmarks),))
    for benchmark in benchmarks:
        print("{}".format(benchmark.name,))
