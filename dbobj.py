import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

import config

def mk_engine():
    connection_string = "%s://%s:%s@%s/%s" % (config.dbtype, config.username, config.password, config.dbhost, config.dbname)
    engine = create_engine(connection_string)
    return engine

### ORM definitions

Base = declarative_base()

# A Benchmark has an ID, a benchmark name, and a filesystem path

class Benchmark(Base):
    __tablename__ = 'benchmarks'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    path = Column(String, nullable=False)

    def __repr__(self):
        return "<Benchmark(name='%s', path='%s')>" % (self.name, self.path)

# A Case has an ID, a Benchmark ID, a relative filesystem path, a SHA256 checksum, and an expected status

class Case(Base):
    __tablename__ = 'cases'

    id = Column(Integer, primary_key=True)
    benchmark_id = Column(Integer, ForeignKey('benchmarks.id'))
    path = Column(String, nullable=False)
    checksum = Column(String,nullable=True)
    status = Column(String,nullable=True)

    benchmark = relationship("Benchmark", back_populates="cases") 

    def __repr__(self):
        return "<Case(path='%s')>" % (path,)

Benchmark.cases = relationship("Case", order_by=Case.id, back_populates="benchmark", cascade="all, delete, delete-orphan")

# A Solver has an ID and a solver name, and a list of versions

class Solver(Base):
    __tablename__ = 'solvers'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    def __repr__(self):
        return "<Solver(%s)>" % (name,)

# A SolverVersion has an ID, a Solver ID, a version name,
# a relative filesystem path, a creation date, and a SHA256 checksum

class SolverVersion(Base):
    __tablename__ = 'solverversions'

    id = Column(Integer, primary_key=True)
    solver_id = Column(Integer, ForeignKey('solvers.id'))
    version = Column(String, nullable=False)
    path = Column(String, nullable=True)
    creationdate = Column(DateTime(timezone=False), server_default=func.now())
    checksum = Column(String, nullable=True)

    solver = relationship("Solver", back_populates="versions")

    def __repr__(self):
        return "<SolverVersion(solver=%s, version=%s)>" % (solver.name, version)

Solver.versions = relationship(SolverVersion, order_by=SolverVersion.creationdate, back_populates="solver")
