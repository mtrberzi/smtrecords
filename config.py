# global system config

# This creates a sqlalchemy connection string;
# modify this as necessary.
# A "sqlite" database does not require a database server,
# but is suitable for small-scale usage only.
# If any of the concurrency features or distributed system features
# are to be used, it is highly recommended to set up
# a high-quality database server.

dbtype = "sqlite"
username = ""
password = ""
dbhost = ""
dbname = "/work/smtrecords.sqlite"

workbase = "/work"
solverbase = "/work/solvers"
validationsolverbase = "/work/validation_solvers"

# per-host config

# set remotecopy to True if the work directory lives on a remote host;
# solvers/benchmarks/etc. will be copied over SSH (SCP) to a machine
# with access to workbase
remotecopy = False
remotehost = "example.net"
remoteusername = "nobody"
