#!/usr/bin/env python3
from smtrecords import dbobj

engine = dbobj.mk_engine()
dbobj.Base.metadata.create_all(engine)
