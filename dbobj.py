import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

import config

def mk_engine():
    connection_string = "%s://%s:%s@%s/%s" % (config.dbtype, config.username, config.password, config.dbhost, config.dbname)
    print(connection_string)
#    engine = create_engine(connection_string)
#    return engine

### ORM definitions

Base = declarative_base()

# A Benchmark has an ID, a benchmark name, and a filesystem path

class Benchmark(Base):
    __tablename__ = 'benchmarks'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    path = Column(String)

    def __repr__(self):
        return "<Benchmark(name='%s', path='%s')>" % (self.name, self.path)


