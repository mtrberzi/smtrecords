## global system config

# This creates a sqlalchemy connection string;
# modify this as necessary.
# A "sqlite" database does not require a database server,
# but is suitable for small-scale usage only.
# If any of the concurrency features or distributed system features
# are to be used, it is highly recommended to set up
# a high-quality database server.

dbtype = "sqlite"
username = "strings"
password = "swordfish"
dbhost = "localhost"
dbname = "strings"

# global paths for work files

workbase = "/work"
benchmarkbase = "/work/benchmarks"
solverbase = "/work/solvers"
validationsolverbase = "/work/validation_solvers"

# Activate cluster mode if set to True.
# Celery workers must be configured and available.

usecluster = False

## per-host config

# set remotecopy to True if the work directory lives on a remote host;
# solvers/benchmarks/etc. will be copied over SSH (SCP) to a machine
# with access to workbase
remotecopy = False
remotehost = "fileserver"
remoteusername = "nobody"
