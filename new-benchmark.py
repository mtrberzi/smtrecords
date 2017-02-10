#!/usr/bin/env python3

import dbobj
import config

import sqlalchemy
from sqlalchemy.orm import sessionmaker
import sys
import os
import os.path
import hashlib
import re
import paramiko

re_status = re.compile("set-info\s+:status\s+(\w+)")

def process_benchmark(path):
    status = None
    hasher = hashlib.sha256()
    with open(path, 'rb') as casedata:
        buf = casedata.read()
        for line in buf.decode('UTF-8').split("\r\n"):
            match = re_status.search(line)
            if match:
                if status is None:
                    status = match.group(1)
                else:
                    print("warning: case %s has multiple (set-info :status) commands, setting status to unknown")
                    status = "unknown"
        hasher.update(buf)
    return (hasher.hexdigest(), status)

def ensure_subdirectories(remotebase, path, sftp):
    if path == '':
        return
    check = remotebase + "/" + path
    try:
        sftp.stat(check)
    except FileNotFoundError:
        (head, tail) = os.path.split(path)
        ensure_subdirectories(remotebase, head, sftp)
        sftp.mkdir(check)

def read_back_and_confirm(sftp, remotecase, expectedhash):
    try:
        hasher = hashlib.sha256()
        with sftp.file(remotecase, 'rb') as remotefile:
            buf = remotefile.read()
            hasher.update(buf)
        if hasher.hexdigest() != expectedhash:
            return False
        # OK
        return True
    except:
        return False

## Entry point

if len(sys.argv) != 3:
    print("Usage: " + sys.argv[0] + " benchmark-name /path/to/benchmark/files")
    sys.exit(1)

name = sys.argv[1]
path = sys.argv[2]

engine = dbobj.mk_engine()
Session = sessionmaker(bind=engine)
session = Session()

# check if the named benchmark already exists
if session.query(dbobj.Benchmark).filter(dbobj.Benchmark.name == name).count() > 0:
    print("Benchmark '" + name + "' already exists.")
    sys.exit(1)

benchmark = dbobj.Benchmark(name=name, path=path)

print("Opening connection to %s for file transfer" % (config.dbhost,))

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
try:
    ssh.connect(config.dbhost)
except paramiko.BadHostKeyException as e:
    print("Bad host key:")
    print(e)
    session.rollback()
    sys.exit(1)
except paramiko.AuthenticationException as e:
    print("Authentication failure:")
    print(e)
    session.rollback()
    sys.exit(1)
except paramiko.SSHException as e:
    print("SSH connection error:")
    print(e)
    session.rollback()
    sys.exit(1)
except Exception as e:
    print("An exception occurred while connecting:")
    print(e)
    session.rollback()
    sys.exit(1)

sftp = ssh.open_sftp()
remotepath = "/work/benchmarks/%s" % (name,)

# the remote path may already exist if we are resuming a previous attempt
try:
    sftp.stat(remotepath)
except FileNotFoundError:
    sftp.mkdir(remotepath)
    print("Created %s" % (remotepath,))

print("Copying files", end='', flush=True)

# iterate over the given path, look for files ending in .smt2

ncases = 0

for root, dirs, files in os.walk(path):
    for f in files:
        if f.endswith(".smt2"):
            fullPathToCase = os.path.join(root, f)
            casename = os.path.relpath(fullPathToCase, path)
            ncases += 1
            (checksum, status) = process_benchmark(fullPathToCase)
            case = dbobj.Case(path=casename, checksum=checksum, status=status)
            benchmark.cases.append(case)
            (head, tail) = os.path.split(casename)
            ensure_subdirectories(remotepath, head, sftp)
            remotecase = remotepath + "/" + casename
            # see if the file already exists
            exists = False
            try:
                sftp.stat(remotecase)
                exists = True
                if not read_back_and_confirm(sftp, remotecase, checksum):
                    print("Failed to verify %s! Aborting." % (remotecase,))
                    sftp.close()
                    ssh.close()
                    session.rollback()
                    sys.exit(1)
            except FileNotFoundError:
                exists = False
                
            try:
                if not exists:
                    sftp.put(fullPathToCase, remotecase)
                    if not read_back_and_confirm(sftp, remotecase, checksum):
                        print("Failed to verify %s! Aborting." % (remotecase,))
                        sftp.close()
                        ssh.close()
                        session.rollback()
                        sys.exit(1)
            except Exception as e:
                print("An exception occurred while copying %s:" % (casename,))
                print(e)
                sftp.close()
                ssh.close()
                session.rollback()
                sys.exit(1)
            print(".", end='', flush=True)
            if ncases % 100 == 0:
                print("(%d)" % (ncases,))
sftp.close()
ssh.close()
print("")
            
if ncases == 0:
    print("No SMT2 files found in benchmark path. Exiting.")
    print("The database has not been modified.")
    session.rollback()
    sys.exit(1)
    
session.add(benchmark)
session.commit()

print("Benchmark %s created with %d cases." % (name, ncases))
